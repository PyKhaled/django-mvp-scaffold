"""Build the documentation contract from the installed helpdesk router/serializers."""

import argparse
import copy
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def representation(schema, *, request):
    """Separate writable input from serialized output, including nested fields."""
    schema = copy.deepcopy(schema)
    if "pattern" in schema:
        # DRF emits Python regex anchors such as \z, which are not portable
        # OpenAPI/ECMAScript expressions. Keep server validation explicit.
        schema.pop("pattern")
        schema["description"] = (
            schema.get("description", "") + " Server-side regular-expression validation applies."
        ).strip()
    if "properties" in schema:
        excluded = "readOnly" if request else "writeOnly"
        schema["properties"] = {
            key: representation(value, request=request)
            for key, value in schema["properties"].items()
            if not value.get(excluded)
        }
        required = [key for key in schema.get("required", []) if key in schema["properties"]]
        schema.pop("required", None)
        if required:
            schema["required"] = required
    if "items" in schema:
        schema["items"] = representation(schema["items"], request=request)
    if not request and schema.get("format") == "binary":
        schema["format"] = "uri"
    return schema


def build_schema():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "product.settings")
    os.environ.setdefault("DJANGO_ENV", "development")
    import django

    django.setup()
    from rest_framework.schemas.openapi import AutoSchema

    from product.helpdesk.api_urls import router

    schemas = {}
    paths = {}
    tags = []
    # Custom fields are deployment data, not part of the baseline contract.
    # Do not read or mutate a developer's database while building documentation.
    with patch("helpdesk.serializers.CustomField.objects.all", return_value=[]):
        for prefix, viewset, _basename in router.registry:
            name = viewset.serializer_class.__name__.removesuffix("Serializer")
            mapped = AutoSchema().map_serializer(viewset.serializer_class())
            schemas[name] = representation(mapped, request=False)
            schemas[f"{name}Input"] = representation(mapped, request=True)
            partial = copy.deepcopy(schemas[f"{name}Input"])
            partial.pop("required", None)
            schemas[f"{name}Patch"] = partial
            tags.append({"name": prefix})
            ref = {"$ref": f"#/components/schemas/{name}"}
            schemas[f"{name}Page"] = {
                "type": "object",
                "required": ["count", "next", "previous", "results"],
                "properties": {
                    "count": {"type": "integer", "minimum": 0},
                    "next": {"type": "string", "format": "uri", "nullable": True},
                    "previous": {"type": "string", "format": "uri", "nullable": True},
                    "results": {"type": "array", "items": ref},
                },
            }
            for route in router.get_routes(viewset):
                actions = router.get_method_map(viewset, route.mapping)
                if not actions:
                    continue
                path = f"/help/api/{prefix}/" + ("{id}/" if route.detail else "")
                for method, action in actions.items():
                    operation = {
                        "operationId": f"{action}_{prefix.replace('-', '_')}",
                        "summary": f"{action.replace('_', ' ').capitalize()} {prefix}",
                        "tags": [prefix],
                        "responses": {
                            "403": {"description": "Authentication, staff permission, or CSRF denied."},
                        },
                    }
                    parameters = []
                    if route.detail:
                        parameters.append({
                            "name": "id", "in": "path", "required": True,
                            "schema": {"type": "integer", "minimum": 1},
                        })
                        operation["responses"]["404"] = {
                            "description": "Object not found or outside the accessible queryset."
                        }
                    if action == "list":
                        operation["responses"]["404"] = {"description": "Requested page does not exist."}
                        parameters.extend([
                            {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                            {"name": "page_size", "in": "query", "schema": {"type": "integer", "minimum": 1, "default": 25}},
                        ])
                        if prefix == "tickets":
                            parameters.append({
                                "name": "status", "in": "query",
                                "description": "Comma-separated numeric status codes, e.g. 1,3. Names are not supported.",
                                "schema": {"type": "string"},
                            })
                    if method in {"post", "put", "patch", "delete"}:
                        parameters.append({
                            "name": "X-CSRFToken", "in": "header",
                            "description": "Required with Django session authentication; match the CSRF cookie. Not required for Basic authentication without a session.",
                            "schema": {"type": "string"},
                        })
                    if parameters:
                        operation["parameters"] = parameters
                    if method in {"post", "put", "patch"}:
                        input_name = f"{name}Patch" if method == "patch" else f"{name}Input"
                        if prefix == "tickets" and action == "create":
                            input_name = "TicketCreate"
                        operation["requestBody"] = {
                            "required": True,
                            "content": {
                                media: {"schema": {"$ref": f"#/components/schemas/{input_name}"}}
                                for media in ("application/json", "application/x-www-form-urlencoded", "multipart/form-data")
                            },
                        }
                        operation["responses"]["400"] = {"description": "Field or form validation failed."}
                    status = "204" if method == "delete" else "201" if method == "post" else "200"
                    response = {"description": "Deleted." if status == "204" else "Success."}
                    if status != "204":
                        response["content"] = {"application/json": {"schema": {
                            "$ref": f"#/components/schemas/{name + 'Page' if action == 'list' else name}"
                        }}}
                    operation["responses"][status] = response
                    if prefix == "followups" and action == "create":
                        operation["description"] = "The server sets user to the authenticated staff account."
                    paths.setdefault(path, {})[method] = operation

    schemas["TicketCreate"] = copy.deepcopy(schemas["TicketInput"])
    schemas["TicketCreate"]["required"] = ["queue", "title", "description", "priority"]
    schemas["TicketCreate"]["properties"]["description"].update(nullable=False, minLength=1)
    for name in ("Ticket", "TicketInput", "TicketPatch", "TicketCreate"):
        schemas[name]["description"] = (
            "Baseline fields only. Deployments can add custom_<name> fields with their own validation."
        )
    paths["/help/api/"] = {"get": {
        "operationId": "api_root", "summary": "Browse API collection links",
        "security": [],
        "responses": {"200": {
            "description": "Router links, not ticket or account data. Individual endpoints require staff access.",
            "content": {"application/json": {"schema": {
                "type": "object", "additionalProperties": {"type": "string", "format": "uri"}
            }}},
        }},
    }}
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Django MVP Scaffold — Helpdesk API", "version": "0.1.0",
            "description": (
                "Baseline contract derived from the registered django-helpdesk 2.4.0 viewsets and serializers. "
                "Resource operations require is_staff. Session-authenticated writes require a CSRF token. "
                "Basic authentication must use HTTPS. Queue permissions restrict accessible objects. "
                "Deployment custom fields and storage behavior require separate validation. "
                "This is a documentation snapshot, not a runtime schema endpoint."
            ),
        },
        "servers": [{"url": "/", "description": "Application origin; docs may be hosted separately."}],
        "tags": tags,
        "security": [{"sessionAuth": []}, {"basicAuth": []}],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "sessionAuth": {"type": "apiKey", "in": "cookie", "name": "sessionid",
                                "description": "Django staff session. Writes also require X-CSRFToken and a matching CSRF cookie."},
                "basicAuth": {"type": "http", "scheme": "basic", "description": "Staff credentials over HTTPS."},
            },
            "schemas": schemas,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when the checked-in contract has drifted.")
    args = parser.parse_args()
    target = ROOT / "docs/api/openapi.json"
    rendered = json.dumps(build_schema(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not target.exists() or target.read_text() != rendered:
            parser.exit(1, "OpenAPI contract has drifted; run python tools/generate_openapi.py\n")
        print("OpenAPI contract matches the registered baseline API.")
    else:
        target.write_text(rendered)
        print(f"Wrote {target}")


if __name__ == "__main__":
    main()
