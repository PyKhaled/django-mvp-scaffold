# Changelog

## Unreleased

### Fixed
- Account and profile metadata history now records changes and acting users; admin
  activation actions preserve history. Password hashes and login timestamps are excluded.
- Hijack warning templates now use the active user context and CSRF-protected release forms;
  the custom persistent notification is injected during impersonation.
- Notification pages respect unread filtering and pagination, use the shared layout,
  and provide CSRF-protected read/unread actions.
- Helpdesk module imports and `/help/` routing.
- Login destination and local maintenance cache configuration.
- Production configuration validation and container application/dependency paths.

### Changed
- Default product identity is Django MVP Scaffold, configurable through `SITE_NAME`.
- Website and welcome email copy describe the included account and support features.
- Container roles now support web and a serialized release command using Gunicorn.
- Production host lists accept comma-separated hostnames; invalid Boolean values fail.
- Production keys require 50 characters and required deployment values fail early.
- Documentation separates scaffold guidance from downstream adoption templates.

### Added
- Generated helpdesk OpenAPI contract and embedded API reference, with a CI drift check.
- CI checks, configuration/customization/release guides, and contribution templates.
- Private vulnerability-reporting guidance and third-party asset notices.

### Removed
- Undeclared Celery/Flower startup roles and unused direct OpenAI/Pydantic dependencies.

No tagged release has been published by this change.
