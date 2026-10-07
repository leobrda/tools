from django.urls import path
from .views import home_view, converter_view, comprimir_view, remover_fundo_view, redimensionar_view, imagem_para_pdf_view

urlpatterns = [
    path('', home_view, name='home_view'),
    path('converter/', converter_view, name='converter_view'),
    path('comprimir/', comprimir_view, name='comprimir_view'),
    path('remover-fundo/', remover_fundo_view, name='remover_fundo_view'),
    path('redimensionar/', redimensionar_view, name='redimensionar_view'),
    path('imagem-para-pdf/', imagem_para_pdf_view, name='imagem_para_pdf_view'),
]