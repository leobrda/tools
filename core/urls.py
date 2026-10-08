from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from tools.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

def robots_txt(request):
    linhas = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(linhas), content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tools.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path(
        "ads.txt",
        lambda r: HttpResponse(
            "google.com, pub-1920791853485408, DIRECT, f08c47fec0942fa0\n",
            content_type="text/plain",
        ),
        name="ads_txt",
    ),
]