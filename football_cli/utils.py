import os
import json
from typing import Any
from datetime import datetime, date, timedelta, timezone
from rich.panel import Panel
from rich.table import Table
from rich.console import RenderableType
from functools import lru_cache


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)


def load_json(filename: str) -> dict:
    """Load data from a JSON file.
    
    :param filename: name of the file

    :return: data dictionary
    """
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        data = json.load(f)
    return data

def save_json(data: Any, filename: str):
    """Save data to a JSON file.
    
    :param data: data object to save
    :param filename: name of the file
    """
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def add_rows(table: Table, rows: list[list], styles: dict[str, str] = {}):
    """Add rows to a table (`rich.Table`).

    :param table: `rich.Table` where to add rows
    :param rows: rows values
    :param styles: row styles dictionary where the key is the row number (1-based) and the value is the row style
        (An optional key named `default` represents the default style applied on rows whose number are not found in the dictionary)
    """
    for i, row in enumerate(rows):
        if not row:
            continue
        idx = i + 1
        defualt_style = styles.get("default")
        style = styles.get(str(idx), defualt_style)
        table.add_row(*map(lambda x: str(x) if x not in [None, ""] else "N/A", row), style=style)


def add_columns(table: Table, columns: dict[str, dict[str, Any]]):
    """Add columns to a table (`rich.Table`).

    :param table: `rich.Table` where to add columns
    :param columns: column name as well as their styles
    """
    for name, attributes in columns.items():
        table.add_column(name, **attributes)


@lru_cache
def format_datetime(date_string: str, local_timezone=False, format="%Y-%m-%dT%H:%M:%SZ") -> datetime:
    """Return datetime with time zone.

    :param date_string: string representation of the date
    :param local_timezone: if `True`, set time zone to the local time zone (default is UTC)

    :return: datetime with time zone (UTC or local time zone)
    """
    dt = datetime.strptime(date_string, format)
    dt = dt.replace(tzinfo=timezone.utc)
    if local_timezone:
        dt = dt.astimezone()
    return dt


def to_isoformat(date_string: str, format="%Y-%m-%d", end=False) -> str:
    """Convert date string to ISO format (yyyy-mm-dd).

    :param date_string: string representation of the date
    :param format: date string format
    :param end: if end date, add 1 day to consider this date (exclusive end date in the API call)

    :return: string representation of the date in ISO format (yyyy-mm-dd)
    """
    date_ = datetime.strptime(date_string, format).date() + timedelta(days=end)
    return date_.isoformat()


def date_from_offset(offset: int, end=False) -> str:
    """Calculate date from offset (number of days from today).

    :param offset: offset from today (positive or negative)
    :param end: if end date, add 1 day to consider this date (exclusive end date in the API call)

    :return: string representation of the date in ISO format (yyyy-mm-dd)
    """
    date_ = date.today() + timedelta(days=offset+end)
    return date_.isoformat()


def no_result(message: str = "No Available Data") -> RenderableType:
    """Output of the script in case of no results returned from the API."""
    return Panel(message, border_style="white dim", style="red bold")
