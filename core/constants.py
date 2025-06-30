from django.conf import settings


IMAGE_MAX_WIDTH = getattr(settings, 'IMAGE_MAX_WIDTH', 2000)
IMAGE_MAX_HEIGHT = getattr(settings, 'IMAGE_MAX_HEIGHT', 2000)
DEFAULT_PAGE_SIZE = getattr(settings, 'DEFAULT_PAGE_SIZE', 20)

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', '')
IMAGE_ROOT = getattr(settings, 'IMAGE_ROOT', 'images')

IMAGE_CACHE_PROCESSED = getattr(settings, 'IMAGE_CACHE_PROCESSED', True)
IMAGE_CACHE_TTL = getattr(settings, 'IMAGE_CACHE_TTL', 3600)
