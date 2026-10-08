# Security reporting

Report suspected vulnerabilities privately through
[GitHub private vulnerability reporting](https://github.com/PyKhaled/django-mvp-scaffold/security/advisories/new).
Include the affected revision, reproduction with synthetic data, expected versus
observed behavior, and impact. Do not post exploit details or credentials in public
issues. If GitHub reporting is temporarily unavailable, withhold sensitive details
until a private channel is available.

The scaffold is early-stage. No stable release support window or response-time
SLA is currently promised. Review fixes against current `main`; deployed forks
must track their own dependencies, configuration, and supported versions.

Dependency auditing is one check, not proof of application security. Verify
production proxy trust, secrets, access controls, email links, and media access
before deployment. See [security guidance](docs/security/index.md).
