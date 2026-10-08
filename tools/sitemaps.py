from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'home_view',
            'converter_view',
            'comprimir_view',
            'remover_fundo_view',
            'redimensionar_view',
            'imagem_para_pdf_view',
            'pdf_para_imagem_view',
            'gerador_favicon_view',
            'cortar_imagem_view',
            'marca_dagua_view',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        # Dá prioridade máxima à página principal
        if item == 'home_view':
            return 1.0
        return 0.8