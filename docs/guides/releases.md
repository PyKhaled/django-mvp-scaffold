# Releases

Use `CHANGELOG.md` to describe user-visible changes under Unreleased. Before a tag,
run all CI checks on the exact candidate revision, rehearse deployment/rollback,
and record resolved dependencies and image digest. Do not publish a passing badge
or release claim based only on local tests.

Start with a prerelease such as `v0.1.0-alpha.1` after acceptance. Keep the package
version and release notes consistent. Each release should state Python/Django
support, migration/configuration changes, known limitations, and upgrade steps.
No historical release or deployment evidence should be invented.

Tags identify source; immutable container digests identify deployments. Record
both. Publish a GitHub release with the reviewed changelog after acceptance.
Follow the [deployment runbook](../runbooks/deployment.md) for recovery; a code
rollback does not automatically reverse database migrations.
