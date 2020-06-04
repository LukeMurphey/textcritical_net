from django.test import TestCase
from reader.sitemaps import StaticSitemap, WorksSitemap


class TestStaticSitemap(TestCase):

    def test_load(self):
        sitemap = StaticSitemap()
        sitemap.items()


class TestWorksSitemap(TestCase):

    def test_load(self):
        sitemap = WorksSitemap()
        sitemap.items()
