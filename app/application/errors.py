class ApplicationError(Exception):
    pass


class ValidationError(ApplicationError):
    pass


class NotFoundError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass


class RepositoryError(ApplicationError):
    pass
