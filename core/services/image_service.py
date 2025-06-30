import os
from io import BytesIO
from typing import Optional
import logging

from django.http import HttpResponse
from core import constants
from PIL import Image
from core.exceptions import (
    ImageProcessingError,
    UnsupportedFormatError,
    InvalidParametersError,
    ImageNotFound,
)
from core.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class ImageService:
    def __init__(self):
        self.image_processor = ImageProcessor()
        pass

    def list_available_images(self):
        return [
            item
            for item in os.listdir(constants.IMAGE_ROOT)
            if os.path.isfile(os.path.join(constants.IMAGE_ROOT, item))
        ]

    def find_image(
            self, image_path: str, width: Optional[int] = None,
            height: Optional[int] = None, format: Optional[str] = None,
            quality: Optional[int] = None, cache: bool = True,
    ) -> HttpResponse:
        try:
            self._validate_parameters(
                width=width, height=height, format=format, quality=quality)

            [image, processing_needed] = self._find_image(
                image_path=image_path, width=width, height=height,
                format=format, quality=quality, cache=cache)

            output_format = self._get_output_format(
                requested_format=format,
                original_format=image.format,)
            logger.info(f"Expected format: {format}, Returing format: {
                output_format}, Original format:  {image.format}")
            content_type = self._get_content_type(format=output_format)

            buffer = self.image_processor.process_image(
                image=image, processing_needed=processing_needed,
                output_format=output_format, width=width,
                height=height,  quality=quality)

            self._save_to_cache(
                image_buffer=buffer, image_path=image_path, width=width,
                height=height, format=format, quality=quality)
            logger.info("Image was saved, returing response")
            response = HttpResponse(
                buffer.getvalue(), content_type=content_type)
            response['Content-Length'] = len(buffer.getvalue())

            return response

        except Image.UnidentifiedImageError:
            raise UnsupportedFormatError(
                f"Unable to identify image format for path: {image_path}")
        except Exception as e:
            logger.info("Unexpected Exception", exc_info=True)
            raise ImageProcessingError(f"Error processing image: {e}")

    def _find_image(
            self, image_path: str, width: Optional[int] = None,
            height: Optional[int] = None, format: Optional[str] = None,
            quality: Optional[int] = None, cache: bool = True
    ) -> [Image.Image, bool]:
        if cache:
            if cache_response := self._find_image_in_cache(
                    image_path, width=width, height=height, format=format,
                    quality=quality):
                return [cache_response, constants.IMAGE_CACHE_PROCESSED]
        [image, processing_needed] = self._find_image_in_permasotrage(
            image_path, width=width, height=height, format=format,
            quality=quality)
        return [image, processing_needed]

    def _save_to_cache(
            self, image_buffer: BytesIO, image_path: str,
            width: Optional[int] = None, height: Optional[int] = None,
            format: Optional[str] = None, quality: Optional[int] = None
    ) -> bool:
        try:
            logger.info(f"Image saved to cache in [format: {format}]")
            CacheService.cache_processed_image(
                image_buffer.getvalue(), file_path=image_path, width=width,
                height=height, format=format, quality=quality)
            return True
        except Exception:
            logger.error("Error saving cache", exc_info=True)
            return False
    pass

    def _find_image_in_cache(
            self, image_path: str, width: Optional[int] = None,
            height: Optional[int] = None, format: Optional[str] = None,
            quality: Optional[int] = None
    ) -> Optional[Image.Image]:
        try:
            if cache_image := CacheService.get_processed_image(
                    file_path=image_path, width=width, height=height,
                    format=format, quality=quality):
                logging.info("Cache hit")
                return Image.open(BytesIO(cache_image))
            logger.info("Cache Miss")
            return None
        except Exception:
            logger.error("Error fetching cache", exc_info=True)
            return None

    def _find_image_in_permasotrage(
            self, image_path: str, width: Optional[int] = None,
            height: Optional[int] = None, format: Optional[str] = None,
            quality: Optional[int] = None
    ) -> [Image.Image, bool]:
        logger.info(f"Looking for: {image_path}")
        full_path = os.path.join(constants.IMAGE_ROOT, image_path)
        processing_needed = True
        if not os.path.exists(full_path):
            raise ImageNotFound(f"Image not found at {full_path}")

        logger.info("Image was found, processing")
        return [Image.open(full_path), processing_needed]

    def _validate_parameters(
            self,
            width: Optional[int],
            height: Optional[int],
            format: Optional[str],
            quality: Optional[int]
    ) -> None:
        if width and (width <= 0 or width > constants.IMAGE_MAX_WIDTH):
            raise InvalidParametersError(f"Width must be between 1 and {
                                         constants.IMAGE_MAX_WIDTH}")

        if height and (height <= 0 or height > constants.IMAGE_MAX_HEIGHT):
            raise InvalidParametersError(f"Height must be between 1 and {
                                         constants.IMAGE_MAX_HEIGHT}")

        if quality and (quality < 1 or quality > 100):
            raise InvalidParametersError("Quality must be between 1 and 100")

    def _get_output_format(self, requested_format: Optional[str],
                           original_format: str) -> str:
        if not requested_format:
            return original_format

        format_upper = requested_format.upper()
        if format_upper == 'JPG':
            return 'JPEG'
        return format_upper

    def _get_content_type(self, format: str) -> str:
        try:
            return Image.MIME[format.upper()]
        except KeyError:
            return f'image/{format.lower()}'


class ImageProcessor:
    def process_image(
            self, image: Image.Image, processing_needed: bool,
            output_format: Optional[str], width: Optional[int] = None,
            height: Optional[int] = None, quality: Optional[int] = None
    ) -> BytesIO:
        buffer = BytesIO()
        save_kwargs = {}
        if processing_needed:
            if (width or height):
                image = self._resize_image(
                    image=image, width=width, height=height)
            if quality:
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            logger.info("Image was processed saving")

        image.save(buffer, format=output_format, **save_kwargs)
        buffer.seek(0)
        return buffer

    def _resize_image(
            self,
            image: Image.Image,
            width: Optional[int],
            height: Optional[int]
    ) -> Image.Image:
        if not width and not height:
            return image
        original_width, original_height = image.size
        original_format = image.format

        if not width:
            ratio = height / original_height
            width = int(original_width * ratio)
        elif not height:
            ratio = width / original_width
            height = int(original_height * ratio)
        image = image.resize((width, height), Image.Resampling.LANCZOS)

        image.format = original_format
        return image
