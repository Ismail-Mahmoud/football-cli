import os
from dotenv import load_dotenv
from pydantic import ValidationError
from rich_click import ClickException
from rich.console import Console
from requests.exceptions import RequestException
from utils import no_result


load_dotenv()
SHOW_ERROR_DETAILS = os.getenv("SHOW_ERROR_DETAILS") == "1"


def formatting_error_handler(f):
    """Decorator for output formatting functions."""
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ClickException as e:
            raise e
        except:
            if SHOW_ERROR_DETAILS:
                Console().print_exception(extra_lines=3, width=None)
            return no_result("Error while formatting the output")
    return wrapper


class APIResponseParsingError(ClickException):
    def __init__(self, error: ValidationError):
        message = "Error while parsing API response."
        if SHOW_ERROR_DETAILS:
            message += f"\n\n{error}"
        super().__init__(message)


class APIRequestException(ClickException):
    def __init__(self, error_type="", status_code="", error_details=""):
        message = f"{error_type} {status_code}"
        if SHOW_ERROR_DETAILS and error_details:
            message += f"\n{error_details}"
        super().__init__(message)


class ConnectionError(APIRequestException):
    def __init__(self):
        super().__init__(error_type="Connection Error")


class HTTPError(APIRequestException):
    def __init__(self, error: RequestException):
        super().__init__(
            error_type="HTTP Error",
            status_code=error.response.status_code,
            error_details=error.response.json().get("message", "")
        )


class RequestError(APIRequestException):
    def __init__(self, error: RequestException):
        super().__init__(
            error_type="Request Error",
            status_code=error.response.status_code,
            error_details=error.response.json().get("message", "")
        )
