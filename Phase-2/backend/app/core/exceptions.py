from fastapi import HTTPException, status


class TaskNotFoundException(HTTPException):
    def __init__(self, task_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )


class UserNotFoundException(HTTPException):
    def __init__(self, user_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )


class UnauthorizedAccessException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )