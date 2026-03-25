class AppError(Exception):
    """Some app error"""
    pass

class ClientError(AppError):
    """HTTP-client error"""
    pass

class BadStatusError(ClientError):
    """Response error"""
    pass

class ConfigError(AppError):
    """Config error"""
    pass

class NetworkError(AppError):
    """Connection error"""
    pass

class ServiceError(AppError):
    """Validation/business rule error"""
    pass

class StorageError(AppError):
    """Filesystem/save error"""
    pass

class TimeoutError(AppError):
    """Timeout"""
    pass

class ValidationError(AppError):
    """Validation/business rule error"""
    pass
