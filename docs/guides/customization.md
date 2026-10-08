# Customize the scaffold

1. Define one end-to-end product workflow and its customer/operator permissions.
2. Set `SITE_NAME` to your product display name (default: Django MVP Scaffold).
   Shared pages, administration, and account emails use this setting. Customize
   the mark in `product/templates/layout/brand.html`, replace landing-page copy
   as features are implemented, and review every outbound link.
3. Set site identity and sender settings; keep secrets outside source control.
4. Add focused Django apps under `product/`, register them, and create migrations.
5. Keep custom CSS in `product/static/css/app.css`; avoid editing minified vendor
   files. Preserve Tabler notices and test layout after upgrading assets.
6. Test permitted and denied paths, invalid input, email, and account lifecycle.
7. Complete applicable [adoption templates](../templates/index.md), rehearse
   deployment and recovery, and record acceptance evidence.

The account model uses Django's built-in user plus related metadata. Plan any
custom-user-model change before creating production data. Keep helpdesk capability,
CSRF, and throttling checks when changing customer access.
