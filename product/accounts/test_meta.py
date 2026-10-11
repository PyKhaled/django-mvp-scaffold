from django.test import SimpleTestCase, override_settings


class LandingMetadataTests(SimpleTestCase):
    @override_settings(META_SITE_DOMAIN="example.org", META_SITE_PROTOCOL="https", SITE_NAME="Demo")
    def test_landing_renders_metadata_and_canonical_url(self):
        response = self.client.get("/")
        self.assertContains(response, '<link rel="canonical" href="https://example.org/">')
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, 'property="og:site_name" content="Demo"')
        self.assertContains(response, 'name="twitter:card"')
        self.assertContains(response, '<title>Demo · Accounts and support</title>', html=True)
