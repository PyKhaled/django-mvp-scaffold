# API scope

The application is primarily server-rendered Django. The helpdesk integration
includes Django REST Framework routes under `/help/api/`, defined in
`product/helpdesk/api_urls.py`. Review the included package view permissions and
tests before exposing or extending them. The customer ticket listing is excluded;
public ticket access uses capability-protected views rather than matching a
mutable account email address.

No general product API, JWT authentication contract, or `/health` endpoint is
promised. [Example OpenAPI and Swagger files](../templates/index.md) are adoption
templates, not verified endpoint documentation. Define and test a real contract
when adding your product API.
