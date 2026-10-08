from django.urls import path
from .views import (home_view,
                    converter_view,
                    comprimir_view,
                    remover_fundo_view,
                    redimensionar_view,
                    imagem_para_pdf_view,
                    gerador_favicon_view,
                    cortar_imagem_view,
                    marca_dagua_view,
                    pdf_para_imagem_view,)

urlpatterns = [
    path('', home_view, name='home_view'),
    path('converter/', converter_view, name='converter_view'),
    path('comprimir/', comprimir_view, name='comprimir_view'),
    path('remover-fundo/', remover_fundo_view, name='remover_fundo_view'),
    path('redimensionar/', redimensionar_view, name='redimensionar_view'),
    path('imagem-para-pdf/', imagem_para_pdf_view, name='imagem_para_pdf_view'),
    path('gerador-favicon/', gerador_favicon_view, name='gerador_favicon_view'),
    path('cortar/', cortar_imagem_view, name='cortar_imagem_view'),
    path('marca-dagua/', marca_dagua_view, name='marca_dagua_view'),
    path('pdf-para-imagem/', pdf_para_imagem_view, name='pdf_para_imagem_view'),
]