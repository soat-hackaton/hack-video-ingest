class VideoIngestException(Exception):
    """Base para todas as exceções do projeto"""
    pass

class ResourceNotFoundException(VideoIngestException):
    """Equivalente ao 404"""
    pass

class BusinessRuleException(VideoIngestException):
    """Equivalente ao 400"""
    pass