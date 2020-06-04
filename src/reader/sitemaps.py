from django.contrib.sitemaps import Sitemap
from reader.models import Work
from django.core.urlresolvers import reverse


class StaticSitemap(Sitemap):
    priority = 0.5
    lastmod = None

    def items(self):
        return [
            "/",
            reverse('home'),
            reverse('about'),
            reverse('contact'),
            reverse('search')
        ]

    def location(self, obj):
        return obj[0] if isinstance(obj, tuple) else obj

    def changefreq(self, obj):
        return obj[1] if isinstance(obj, tuple) else "monthly"


class WorksSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Work.objects.all().order_by('title')

    def location(self, work):
        return reverse('read_work', kwargs={'title': work.title_slug})
