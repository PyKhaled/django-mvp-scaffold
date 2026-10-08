# Django MVP Scaffold documentation

Build and customize the scaffold using the guides below. Operational procedures
require validation against your own infrastructure.

- [Getting started](getting-started/index.md): installation and first local run.
- [Development](guides/development.md): changes, tests, and review.
- [Customization](guides/customization.md): turn the example into your product.
- [Configuration](configuration.md): environment variables and runtime roles.
- [Architecture](architecture/system-overview.md): components and request flow.
- [API scope](api/index.md): actual integration boundaries and example contracts.
- [Runbooks](runbooks/index.md): deployment, maintenance, backup, support, incidents.
- [Known issues](known-issues.md): current limitations and evidence boundaries.
- [Releases](guides/releases.md): versioning, checks, and rollback notes.
- [Security](security/index.md): private reporting and handling.
- [Adoption templates](templates/index.md): worksheets for downstream products.

## Build and review

From the repository root, install `python -m pip install --group docs` and run
`mkdocs serve`. Before submission run `mkdocs build --strict` and inspect changed
pages. CI builds documentation but does not publish a hosted site.

Update docs in the same PR as behavior changes. Keep configuration defaults in
sync with settings. Record revision and environment for operational evidence.
