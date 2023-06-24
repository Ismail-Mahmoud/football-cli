"""This is a standalone script used to generate data as a preprocessing step.

If you already have `data` directory with all required data, you don't need to run this script.

`data` directory after running this script:
     * `all_competitions.json`: All competitions
     * `competitions.json`: Available competitions within your permissions
     * `teams.json`: Available teams within your permissions

`data` directory may also contain an optional file called `options.json` which define choices of CLI options of type `click.Choice`.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from request_handler import RequestHandler
from models import CompetitionTeams, update_forward_refs
from utils import load_json, save_json


# Available competitions within the free-tier permissions
AVAILABLE_COMPETITION_CODES = load_json("options.json").get("competition_codes") \
     or ["WC", "CL", "BL1", "DED", "BSA", "PD", "FL1", "ELC", "PPL", "EC", "SA", "PL", "CLI"]


@dataclass
class Zone:
    name: str
    start_position: int
    end_position: int
    color: str


@dataclass
class CompetitionProperties:
    id: int
    code: str
    name: str
    type: str
    area: str
    zones: list[Zone] = field(default_factory=list)
    position_colors: dict[str, str] = field(default_factory=dict)


def prepare_competitions_data():
    """Prepare available competitions data.
    
    The main purpose is to add `zones` attribute which represents different zones in the standings table
    and hence, colorize the table (when requested) based on these zones.
    """
    d = load_json("all_competitions.json")
    if not d:
        d = RequestHandler(
            path=f"competitions"
        ).send_request()
        save_json(d, "all_competitions.json")    

    competitions: dict[str, CompetitionProperties] = {}
    for competition in d["competitions"]:
        code = competition["code"]
        if code not in AVAILABLE_COMPETITION_CODES:
            continue
        competitions[code] = CompetitionProperties(
            id=competition["id"],
            code=competition["code"],
            name=competition["name"],
            type=competition["type"],
            area=competition["area"]["name"]
        )

    competitions["PL"].zones = [
        Zone(name="UEFA Champions League group stage",
             start_position=1, end_position=4, color="blue"),
        Zone(name="UEFA Europa League group stage",
             start_position=5, end_position=6, color="yellow"),
        Zone(name="UEFA Conference League qualifiers",
             start_position=7, end_position=7, color="green"),
        Zone(name="Relegation",
             start_position=18, end_position=20, color="red"),
    ]

    competitions["PD"].zones = [
        Zone(name="UEFA Champions League group stage",
             start_position=1, end_position=4, color="blue"),
        Zone(name="UEFA Europa League group stage",
             start_position=5, end_position=6, color="yellow"),
        Zone(name="UEFA Conference League qualifiers",
             start_position=7, end_position=7, color="green"),
        Zone(name="Relegation",
             start_position=18, end_position=20, color="red"),
    ]

    competitions["SA"].zones = [
        Zone(name="UEFA Champions League group stage",
             start_position=1, end_position=4, color="blue"),
        Zone(name="UEFA Europa League group stage",
             start_position=5, end_position=6, color="yellow"),
        Zone(name="UEFA Conference League qualifiers",
             start_position=7, end_position=7, color="green"),
        Zone(name="Relegation",
             start_position=18, end_position=20, color="red"),
    ]

    competitions["BL1"].zones = [
        Zone(name="UEFA Champions League group stage",
             start_position=1, end_position=4, color="blue"),
        Zone(name="UEFA Europa League group stage",
             start_position=5, end_position=6, color="yellow"),
        Zone(name="UEFA Conference League qualifiers",
             start_position=7, end_position=7, color="green"),
        Zone(name="Relegation play-offs",
             start_position=16, end_position=16, color="magenta"),
        Zone(name="Relegation",
             start_position=17, end_position=18, color="red")
    ]

    competitions["FL1"].zones = [
        Zone(name="UEFA Champions League group stage",
             start_position=1, end_position=2, color="blue"),
        Zone(name="UEFA Champions League play-offs",
             start_position=3, end_position=3, color="cyan"),
        Zone(name="UEFA Europa League group stage",
             start_position=4, end_position=4, color="yellow"),
        Zone(name="UEFA Conference League qualifiers",
             start_position=5, end_position=5, color="green"),
        Zone(name="Relegation",
             start_position=17, end_position=20, color="red"),
    ]

    competitions["ELC"].zones = [
        Zone(name="Promotion",
             start_position=1, end_position=2, color="blue"),
        Zone(name="Promotion play-offs",
             start_position=3, end_position=6, color="yellow"),
        Zone(name="Relegation",
             start_position=22, end_position=24, color="red"),
    ]

    competitions["CL"].zones = [
        Zone(name="Next round",
             start_position=1, end_position=2, color="green"),
        Zone(name="Europa League round of 16 play-offs",
             start_position=3, end_position=3, color="yellow")
    ]

    competitions["EC"].zones = [
        Zone(name="Next round",
             start_position=1, end_position=2, color="green"),
    ]

    competitions["WC"].zones = [
        Zone(name="Next round",
             start_position=1, end_position=2, color="green"),
    ]

    for code, competition in competitions.items():
        for zone in competition.zones:
            color = zone.color
            for i in range(zone.start_position, zone.end_position + 1):
                competition.position_colors[str(i)] = color

    competitions_to_dump = {key: asdict(val)
                            for key, val in competitions.items()}
    
    save_json(competitions_to_dump, "competitions.json")


def prepare_teams_data():
    """Prepare available teams data (id, name, country).
    
    These data will be shown to the user when requested to get the ID of a specific team.
    """
    update_forward_refs()
    d = defaultdict(dict)
    for i, code in enumerate(AVAILABLE_COMPETITION_CODES):
        print(f"Requesting {code} teams...")
        time.sleep(7)    # in order not to exceed max requests per minute (10)
        result = RequestHandler(
            path=f"competitions/{code}/teams"
        ).send_request()
        teams = CompetitionTeams(**result).teams
        for team in teams:
            d[team.tla][team.id] = {
                "full_name": team.fullName,
                "short_name": team.shortName,
                "country": getattr(team.area, "name", None)
            }

    save_json(d, "teams.json")


def main():
    print("Preparing data.....\nThis might take around one minute, so please wait.")
    prepare_teams_data()
    prepare_competitions_data()


if __name__ == "__main__":
     main()
