from django.urls import path
from .views import converter_view

urlpatterns = [
    path('', converter_view, name='converter_view'),
]