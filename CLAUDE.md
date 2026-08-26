# Notes for working on compas_sandbox

Things that cost real time to discover and are not visible from the code alone. The
changelog says what changed; this says what will bite you.

## The solver

**`mu_strategy="adaptive"` in `_CRA_OPTIONS` is load bearing.** CRA's complementarity
constraints are degenerate and IPOPT's monotone barrier update crawls on them. Without
it the 20-block arch takes 1964 of its 3000 permitted iterations and reaches its answer
only through the restoration phase — enough margin to pass here and not enough on a
wheel that rounds differently, which is how macOS users got
`solve failed: failed (Maximum_Iterations_Exceeded)`. With it: 668 iterations, same
answer to 1e-10.

**Do not "fix" the tolerances.** `tol=1e-10 / constr_viol_tol=1e-12` look absurd for
double precision and they are, but they are what drives the solve into restoration,
which is where it finds its answer. Measured: `tol=1e-8 / constr_viol_tol=1e-9` turns a
solve that stops at a feasible point into one that exhausts the 3000-iteration cap.
Looser is worse, not safer.

**An iteration-capped point is not feasible.** `native.py` rescues `Restoration_Failed`
and `Search_Direction_Becomes_Too_Small` by checking the returned point's violation.
`Maximum_Iterations_Exceeded` is deliberately excluded. Adding it was tried: at caps of
50, 200, 1000 and 1900 iterations the point failed the feasibility check every time, so
it rescues nothing and risks accepting a non-solution.

**Never let the arch test skip itself again.** `test_cra_arch` used to `pytest.skip` on
a stall. That is exactly why a broken macOS wheel shipped green.
`test_cra_arch_has_iteration_headroom` guards the margin, not just the answer — a solve
creeping back toward the cap is the actual regression.

## The IPOPT build

**MUMPS races under parallel make.** Its makefiles are missing dependencies, so a `-j`
build intermittently dies linking `libcoinmumps` — always just after `dtype3_root.F`,
and coinbrew reports only `Build failed, see error output above` with no error above it.
It failed three of six pipeline runs. Linux sets `JOBS=1`; macOS and Windows are only
safe because they restore a cached stage tree and never enter the build.

**The caches hide a broken from-scratch build.** `hashFiles('packaging/build_ipopt.sh')`
is part of the ipopt cache key, so *any* edit to that file evicts the macOS and Windows
stage trees and makes them compile for the first time in months. Windows' last green run
before this was discovered shows `Build ipopt: skipped`. If you touch that script, expect
those platforms to build from scratch and to hit the race; give them `JOBS=1` too.

**`hashFiles()` is not a plain sha256.** It hashes the file, then hashes the digest —
`sha256(sha256(content))`. Comparing a plain `sha256sum` against a cache key will tell
you the cache misses when it actually hits.

**macOS is on Accelerate on purpose (for now).** Moving it to OpenBLAS for
bit-reproducibility was tried and reverted. Pointed at `libopenblas.a`, libtool refuses
to link a static archive into the shared `libcoinmumps` coinbrew builds regardless of
`--disable-shared`; pointed at `libopenblas.dylib`, that complaint goes and it still
fails silently. Linux only escapes this because `-lcralapack` is a linker script, so
libtool sees an ordinary `-l` flag rather than a library path.

## Releasing

**The PyPI upload must live in `release.yml`, not in the reusable `pipeline.yml`.**
Trusted publishing matches the `job_workflow_ref` claim, which names the file a job is
*defined* in. A job in the reusable workflow presents `pipeline.yml` to a publisher
configured for `release.yml` and fails with `invalid-publisher`. Reusable workflows are
not supported by trusted publishing at all.

**Version numbers are cheap; failed tags are not reusable.** 0.7.3 and 0.7.4 are skipped
— both tags point at builds that failed before publishing. A failed release means either
deleting the tag or bumping again.

**A flaky wheel job does not need a new tag.** `gh run rerun <id> --failed` re-runs just
the failed job on the existing tag; the other jobs keep their results and `publish`
cascades if it passes.

## Local development

A source checkout has no compiled `compas_sandbox._core`, so every solver test skips.
That is intentional (`pytest.importorskip`), and it cannot mask a solver-less wheel in
CI because the wheel build smoke-tests the extension and the test job imports `_core`
before pytest runs. To run them locally, `packaging/build_ipopt.sh` then `pip install .`.

`invoke release` needs `ruff`, `pytest` and `bump-my-version`, and ends in an
interactive confirm — it cannot run unattended.
