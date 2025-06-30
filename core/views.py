from django.http import JsonResponse
import logging
from typing import Optional
from core.services import ImageService
from core.exceptions import ImageServiceError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.views import APIView

logger = logging.getLogger(__name__)
_image_service = ImageService()


def _get_int_param(request, param_name):
    value = request.GET.get(param_name)
    if value:
        try:
            return int(value)
        except (ValueError, TypeError):
            pass
    return None


def _get_bool_param(request, param_name, default: Optional[bool]) -> Optional[bool]:
    value = request.GET.get(param_name)
    if value is not None:
        value_lower = value.lower()
        if value_lower in ('true', '1', 'on', 'yes'):
            return True
        elif value_lower in ('false', '0', 'off', 'no'):
            return False
    return default


class CoreView(APIView):
    def get(self, request):
        return JsonResponse({'status': 'OK'}, status=200)


class ImageProcessingView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter('w', int, OpenApiParameter.QUERY,
                             description='Desired width'),
            OpenApiParameter('h', int, OpenApiParameter.QUERY,
                             description='Desired height'),
            OpenApiParameter('format', str, OpenApiParameter.QUERY,
                             description='Output format (e.g., jpg, png, webp)'),
            OpenApiParameter('q', int, OpenApiParameter.QUERY,
                             description='Quality (1-100) for lossy formats'),
            OpenApiParameter('cache', bool, OpenApiParameter.QUERY,
                             description='To fetch from cache'),
        ],
        responses={
            200: OpenApiTypes.BINARY,
            400: {'description': 'Bad Request / Invalid Parameters'},
            404: {'description': 'Image Not Found'},
            500: {'description': 'Internal Server Error'}
        }
    )
    def get(self, request, image_path,):
        try:
            width = _get_int_param(request, 'w')
            height = _get_int_param(request, 'h')
            format_param = request.GET.get('format')
            quality = _get_int_param(request, 'q')
            cache = _get_bool_param(request, 'cache', False)

            logger.info(f"Query params: {
                width, height, format_param, quality, cache}")
            response = _image_service.find_image(
                image_path=image_path,
                width=width,
                height=height,
                format=format_param,
                quality=quality,
                cache=cache,
            )
            return response

        except ImageServiceError as e:
            logger.error(f"Image service error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error processing image: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


class ImageListView(APIView):
    @extend_schema(
        responses={
            200: {'description': 'List of files'},
            500: {'description': 'Internal Server Error'}
        }
    )
    def get(self, request):
        try:
            data = _image_service.list_available_images()
            return JsonResponse({'images': data})
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
