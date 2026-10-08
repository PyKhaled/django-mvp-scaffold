# Helpdesk API reference

The application is primarily server-rendered Django. The helpdesk integration
includes Django REST Framework routes under `/help/api/`, defined in
`product/helpdesk/api_urls.py`. The customer ticket listing is excluded;
public ticket access uses capability-protected views rather than matching a
mutable account email address.

## OpenAPI contract

Download [the OpenAPI 3.0.3 document](openapi.json).
The inline reference loads Swagger UI 5.33.1 from a CDN; it requires internet
access and JavaScript. The JSON document is also included in the built site.

<div id="swagger-ui" data-spec-url="openapi.json" aria-label="Helpdesk API reference">
  <p>Loading the API reference. If it does not appear, use the OpenAPI document linked above.</p>
</div>

## Access and behavior

- Resource operations require an authenticated account with `is_staff=True`.
  Queue permissions further restrict which objects the account can access.
- Django session authentication and HTTP Basic authentication are supported.
  Session-authenticated writes require a matching CSRF cookie and `X-CSRFToken`.
  Use Basic authentication only over HTTPS.
- The API root exposes collection links; it does not expose ticket or account data.
- Ticket, follow-up, and attachment lists use page-number pagination, with 25
  results per page by default. `page_size` changes the requested page size.
- Ticket filtering uses comma-separated **numeric** status codes, such as `1,3`.
- User creation is staff-only. There is no general user listing or retrieval route.
- File uploads use multipart form data. Deployment storage and attachment policy
  still need validation; this reference does not establish media-access safety.

The embedded reference disables live requests and the online schema validator.
See [Swagger UI configuration](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/).

## Scope and regeneration

The contract is generated from the registered viewsets and baseline serializers
in django-helpdesk 2.4.0. It covers canonical JSON resource routes; implicit
`HEAD`/`OPTIONS`, format-suffix aliases, and HTML support forms are omitted.
Database-defined `custom_<name>` ticket fields are deployment-specific and are
not enumerated. The document is a checked-in snapshot, not a runtime schema route
or a guarantee that an individual deployment supports every operation.

Install the development dependencies and run from the repository root:

```sh
python tools/generate_openapi.py
python tools/generate_openapi.py --check
mkdocs build --strict
```

The generator does not read or modify the application database. CI checks for
contract drift before building documentation. Regenerate after route, serializer,
or dependency changes, and review the resulting contract against runtime behavior.

No general product API, JWT authentication contract, or `/health` endpoint is
provided. The files under [adoption templates](../templates/index.md) remain
examples for downstream products and are separate from this helpdesk contract.
