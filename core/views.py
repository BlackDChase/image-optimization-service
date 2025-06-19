from django.http import JsonResponse
from django.core.cache import cache
import time

def test_cache(request):
    key = 'test_timestamp'
    cached_value = cache.get(key)
    
    if cached_value is None:
        timestamp = int(time.time())
        cache.set(key, timestamp, 30)
        return JsonResponse({'timestamp': timestamp, 'cached': False})
    else:
        return JsonResponse({'timestamp': cached_value, 'cached': True})
