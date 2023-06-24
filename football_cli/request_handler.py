import requests
import os
from typing import Any
from dotenv import load_dotenv
from rich.console import Console
from exception_handling import ConnectionError, HTTPError, RequestError
from utils import save_json


load_dotenv()


class RequestHandler():
    BASE_URL = os.getenv("FOOTBALL_CLI_BASE_URL", "https://api.football-data.org/v4")
    API_KEY = os.getenv("FOOTBALL_CLI_API_KEY")
    SAVE_API_RESPONSE = os.getenv("SAVE_API_RESPONSE") == "1"
    ALLOWED_PARAMS = [      # Parameters that are expected by the API
        "matchday", "season", "venue", "competitions", "date", "dateFrom", "dateTo", "status", "stage", "group", "limit",
        "ids", "areas", "lineup", "e", "offset"
    ]

    def __init__(self, path: str, params: dict[str, Any] = {}, headers: dict[str, Any] = {}):
        self.params = self.get_request_params(params)
        self.url = f"{RequestHandler.BASE_URL}/{path}"
        self.headers = {"X-Auth-Token": RequestHandler.API_KEY, **headers}

    def send_request(self) -> dict[str, Any]:
        with Console().status("[bold green]Fetching data from api.football-data.org ..."):
            try:
                response = requests.get(url=self.url, params=self.params, headers=self.headers)
                response.raise_for_status()
                if self.SAVE_API_RESPONSE:
                    save_json(response.json(), "response.json")
                return response.json()
            except requests.exceptions.ConnectionError:
                raise ConnectionError()
            except requests.exceptions.HTTPError as e:
                raise HTTPError(e)
            except requests.exceptions.RequestException as e:
                raise RequestError(e)

    @classmethod
    def get_request_params(cls, params: dict[str, Any]):
        """Prepare request parameters by excluding redundant ones that are either not expected by the API or have `None` values.

        :param params: parameters dictionary (usually `click.Context.params`) containing all `click` command options
        :return: request parameters
        """
        return {key: val for key, val in params.items() if val is not None and key in cls.ALLOWED_PARAMS}
