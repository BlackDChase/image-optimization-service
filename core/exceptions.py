class ImageServiceError(Exception):
    """Base exception for image service errors"""
    pass


class ImageNotFound(ImageServiceError):
    """Raised when fetching image"""
    pass


class ImageProcessingError(ImageServiceError):
    """Raised when image processing fails"""
    pass


class UnsupportedFormatError(ImageServiceError):
    """Raised when image format is not supported"""
    pass


class InvalidParametersError(ImageServiceError):
    """Raised when invalid parameters are provided"""
    pass
