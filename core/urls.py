from django.urls import path
from . import views

urlpatterns = [
    path('test-cache/', views.test_cache, name='test_cache'),
]
