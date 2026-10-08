# Changelog

## Unreleased

### Fixed
- Helpdesk module imports and `/help/` routing.
- Login destination and local maintenance cache configuration.
- Production configuration validation and container application/dependency paths.

### Changed
- Container roles now support web and a serialized release command using Gunicorn.
- Production host lists accept comma-separated hostnames; invalid Boolean values fail.
- Production keys require 50 characters and required deployment values fail early.
- Documentation separates scaffold guidance from downstream adoption templates.

### Added
- CI checks, configuration/customization/release guides, and contribution templates.
- Private vulnerability-reporting guidance and third-party asset notices.

### Removed
- Undeclared Celery/Flower startup roles and unused direct OpenAI/Pydantic dependencies.

No tagged release has been published by this change.
