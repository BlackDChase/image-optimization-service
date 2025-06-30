from django.core.cache import cache
from core import constants
import logging
from typing import Optional


logger = logging.getLogger(__name__)


class CacheService:

    @staticmethod
    def _make_neccessory_cache_key(file_path: str,
                                   **file_meta: str,) -> str:
        logger.info(f"Processiong {
                    constants.IMAGE_CACHE_PROCESSED}, {file_meta}")
        cache_key: str
        if constants.IMAGE_CACHE_PROCESSED:
            params = ",".join(f"{k}:{v}" for k, v in sorted(file_meta.items()))
            cache_key = f"f:{file_path},{params}"
            logger.info(f"Cache Key :{cache_key}")
        else:
            cache_key = f"f:{file_path}"
        return cache_key

    @staticmethod
    def cache_processed_image(processed_data: bytes, file_path: str,
                              **file_meta: str,) -> None:
        logger.info(f"File Meta Save: {file_meta}, type: {type(file_meta)}")

        key = CacheService._make_neccessory_cache_key(file_path,
                                                      **file_meta)
        ttl = constants.IMAGE_CACHE_TTL
        cache.set(key, processed_data, ttl)
        logger.info(f"Cached processed image: {key}")

    @staticmethod
    def get_processed_image(file_path: str, **file_meta: str,
                            ) -> Optional[bytes]:
        logger.info(f"File Meta get: {file_meta}, type: {type(file_meta)}")
        return cache.get(CacheService._make_neccessory_cache_key(
            file_path, **file_meta)
        )
