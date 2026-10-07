from django.urls import path
from .views import converter_view, comprimir_view, remover_fundo_view

urlpatterns = [
    path('', converter_view, name='converter_view'),
    path('comprimir/', comprimir_view, name='comprimir_view'),
    path('remover-fundo/', remover_fundo_view, name='remover_fundo_view'),
]