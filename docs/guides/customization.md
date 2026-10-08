# Customize the scaffold

1. Define one end-to-end product workflow and its customer/operator permissions.
2. Replace CreativeBatch identity in `product/templates/layout/brand.html`, shared
   shells, landing/maintenance pages, account templates, and corresponding tests.
   Replace example marketing copy and review every outbound link.
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
