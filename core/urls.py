from django.urls import re_path
from core.views import ImageProcessingView, ImageListView, CoreView


urlpatterns = [
    re_path(r'^images/$', ImageListView.as_view(), name='list_images'),
    re_path(r'^core/$', CoreView.as_view(), name='core'),
    re_path(r'^image/(?P<image_path>[^/]+)/?$',
            ImageProcessingView.as_view(), name='fetch_image'),
]
