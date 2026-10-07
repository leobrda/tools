from django.urls import path
from .views import converter_view, comprimir_view

urlpatterns = [
    path('', converter_view, name='converter_view'),
    path('comprimir/', comprimir_view, name='comprimir_view'),
]