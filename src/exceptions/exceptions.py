from fastapi import HTTPException, status


class APIError(HTTPException):
    def __init__(
        self,
        detail: str = "Bad request",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: dict | None = None,
        locations: list | None = None,
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.locations = locations

        self.headers = self.__set_headers(headers)

    def __set_headers(self, headers: dict | None = None) -> dict:
        current_headers = {
            "content-type": "application/json",
        }

        if headers:
            current_headers.update(headers)

        return current_headers


class NotFoundError(APIError):
    def __init__(
        self,
        detail: str = "Not found",
        headers: dict | None = None,
        status_code=status.HTTP_404_NOT_FOUND,
        locations: list | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status_code,
            headers=headers,
            locations=locations,
        )


class ValidationError(APIError):
    def __init__(
        self,
        detail: str = "Unprocessable entity",
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        headers: dict | None = None,
        locations: list | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status_code,
            headers=headers,
            locations=locations,
        )


class AuthenticationError(APIError):
    def __init__(
        self,
        detail: str = "Not authorized",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        headers: dict | None = None,
        locations: list | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status_code,
            headers=headers,
            locations=locations,
        )
