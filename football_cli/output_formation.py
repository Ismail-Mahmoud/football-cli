import rich.box as box
from rich.columns import Columns
from rich.align import Align
from rich.console import Group, RenderableType
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich_click import ClickException
from typing import Any, Optional
from models import Competition, Standings, Scorer, Team, Match, Score, Head2HeadAggregates
from utils import add_rows, add_columns, no_result, load_json
from nested_panels import NestedPanels
from exception_handling import formatting_error_handler


@formatting_error_handler
def format_champions(competition: Competition) -> RenderableType:
    """Return a panel containing champions of previous available seasons."""
    if not competition.seasons:
        return no_result()

    champion_panels = [
        Panel(
            Align.center(season.winner.name, style="green bold"),
            title=season.year,
            border_style="blue"
        )
        for season in competition.seasons if season.winner is not None
    ]

    champions = Panel.fit(
        Columns(champion_panels, equal=True),
        title="[bold]:trophy: Champoions :trophy:", title_align="left", border_style="cyan"
    )

    return champions


@formatting_error_handler
def format_standings(standings_set: Standings) -> RenderableType:
    """Return standings table(s)."""
    standings = [standing for standing in standings_set.standings if standing.type == "TOTAL"] \
        if standings_set.competition.is_league \
        else standings_set.standings

    if not standings:
        return no_result()

    competition_id = standings_set.competition.code
    AVAILABLE_COMPETITIONS = load_json("competitions.json")
    position_colors = AVAILABLE_COMPETITIONS[competition_id]["position_colors"]

    tables = []

    for standing in standings:
        table = Table(
            title=standing.group,
            title_style="blue bold",
            box=box.HORIZONTALS,
            header_style="bold dim",
            style="dim",
        )

        columns = {
            "": {"justify": "right", "style": "bold"},
            "TEAM": {"justify": "center", "min_width": 30, "style": "bold"},
            "MP":  {"justify": "right"},
            "W": {"justify": "right"},
            "D": {"justify": "right"},
            "L": {"justify": "right"},
            "GF": {"justify": "right"},
            "GA": {"justify": "right"},
            "GD": {"justify": "right"},
            "PTS":  {"justify": "right", "style": "bold"},
        }
        add_columns(table, columns)

        rows = [[
            r.position,
            r.team.fullName,
            r.playedGames,
            r.won,
            r.draw,
            r.lost,
            r.goalsFor,
            r.goalsAgainst,
            r.goalDifference,
            r.points
        ] for r in standing.table]
        add_rows(table, rows, styles=position_colors)

        tables.append(Align.center(table))

    color_codes = Table.grid()
    for zone in AVAILABLE_COMPETITIONS[competition_id]["zones"]:
        name, color = zone["name"], zone["color"]
        color_codes.add_row(f"  [on {color}]  [/on {color}] {name}")

    tables.append(Align.left(color_codes))

    return Group(*tables)


@formatting_error_handler
def format_teams(teams: list[Team]) -> RenderableType:
    """Return a table with competition teams info (name, foundation year, stadium, coach)."""
    if not teams:
        return no_result()

    table = Table(
        box=box.HORIZONTALS,
        border_style="dim",
        header_style="bold dim",
    )
    add_columns(table, columns={
        "Full Name (ID)": {"justify": "right", "style": "yellow bold"},
        "Founded": {"justify": "left", "style": "blue"},
        "Stadium": {"justify": "left", "style": "green"},
        "Coach": {"justify": "left", "style": "red"},
    })

    add_rows(table, rows=[[
        f"{team.fullName} [not bold]({team.tla})",
        team.founded,
        team.venue,
        getattr(team.coach, "name", None)
    ] for team in teams])

    return table


@formatting_error_handler
def format_team(team: Team) -> RenderableType:
    """Return team info (general club info + squad)."""
    if not team.squad:
        return no_result()

    title_style = "blue bold not dim"
    border_style = "cyan"

    def _format_general_info() -> Columns:
        """Return club info."""
        team_info = {
            "Team": team.fullName,
            "Country": getattr(team.area, "name", None) or "N/A",
            "Founded": team.founded or "N/A",
            "Stadium": team.venue or "N/A",
            "Coach": getattr(team.coach, "name", None) or "N/A"
        }
        if team_info["Team"] == team_info["Country"]:
            del team_info["Country"]

        info = Columns([
            Panel.fit(
                Align.center(str(attr), style="green bold"),
                title=f"[{title_style}]{title}", border_style=border_style
            )
            for title, attr in team_info.items()
        ], equal=True)

        return info

    def _format_squad() -> Panel:
        """Return squad players info (name, nationality, position, date of birth)."""
        squad = team.squad
        if not squad:
            return ""

        players_info = {
            "Nationality": "nationality",
            "Position": "position",
            "Shirt Number": "shirtNumber",
            "DOB": "dateOfBirth",
        }

        player_panels = [
            Panel(
                Group(*[
                    Align.left(
                        f"{str(title)}: {str(val).replace('Offence', 'Attack')}",
                        style="blue"
                    )
                    for title, attr in players_info.items() if (val := getattr(player, attr, None))
                ]),
                title=f"[green bold not dim]{player.name}",
                border_style=border_style
            )
            for player in squad
        ]

        squad_panel = Panel.fit(
            Columns(player_panels, equal=True),
            title=f"[{title_style}]Squad", title_align="left", border_style=border_style
        )

        return squad_panel

    return Group(_format_general_info(), _format_squad())


@formatting_error_handler
def format_top_scorers(scorers: list[Scorer]) -> RenderableType:
    """Return a table with player name, goals, assists and penalties."""
    if not scorers:
        return no_result()

    table = Table(
        box=box.HORIZONTALS,
        border_style="dim",
        header_style="bold dim",
    )
    add_columns(table, columns={
        "": {"style": "dim"},
        "Player": {"justify": "right", "style": "yellow bold"},
        "Team": {"justify": "right", "style": "blue"},
        "Goals": {"justify": "right", "style": "green bold"},
        "Assists": {"justify": "right", "style": "cyan"},
        "Penalties": {"justify": "right", "style": "red"},
        "Played": {"justify": "right", "style": "yellow"},
    })
    add_rows(table, rows=[[
        idx + 1,
        scorer.player.name,
        scorer.team.shortName,
        scorer.goals,
        scorer.assists,
        scorer.penalties,
        scorer.playedMatches,
    ] for idx, scorer in enumerate(scorers)])

    return table


@formatting_error_handler
def format_matches(
    matches: list[Match],
    group_by: list[str] = [],
    headers: list[str] = []
) -> RenderableType:
    """Format a set of matches after grouping them.

    :param group_by: grouping order
    :param headers: match attributes to show beside the score
    """
    if not matches:
        return no_result()

    panels = NestedPanels()
    if not group_by:
        group_by = [None]

    def _create_empty_table(headers=[]):
        """Return an empty table which will be populated later with match scores."""
        table = Table.grid(padding=(0, 1), expand=True)
        columns = {
            "Home": {"justify": "right", "min_width": 15},
            "Score": {"justify": "center"},
            "Away": {"justify": "left", "min_width": 15},
            **{header: {"justify": "left", "min_width": 10} for header in headers},
        }
        add_columns(table, columns)
        return table

    for attr in ["date", "time"]:   # move to the end for rendering purposes
        if attr in headers:
            headers.remove(attr)
            headers.append(attr)

    for match in matches:
        keys = [getattr(match, str(attr), None) for attr in group_by]
        table = panels.get(keys, default=_create_empty_table(headers))
        header_values = [
            f"[blue not bold]{getattr(match, str(header), 'N/A')}" for header in headers]
        _update_matches_table(match, table, header_values)

    return panels.construct()[0]


@formatting_error_handler
def format_match_score(match_: Match) -> list[list[str]]:
    """Return full time score in addition to extra time and penalties score if exist int he following order:

    <home_team> <score> <away_team>

    Extra Time  <score>

    Penalties   <score>
    """

    def _format_score(score: Optional[Score], prefix: str = "", suffix: str = "") -> list[str]:
        """Format a single score of a match (full time, extra time or penalties).

        :param prefix: score prefix (Home team name, "Extra Time" or "Penalties")
        :param suffix: score suffix (Away team name or "" if extra time or penalties score)
        """
        if not score:
            return []

        placeholder = "-"
        separator = ":"
        home_score = score.home if score.home is not None else placeholder
        away_score = score.away if score.away is not None else placeholder
        winner = match_.score.winner

        match winner:
            case "HOME_TEAM":
                home_color, away_color = "green", "red"
            case "AWAY_TEAM":
                home_color, away_color = "red", "green"
            case "DRAW":
                home_color, away_color = "yellow", "yellow"
            case _:
                home_color, away_color = "white not bold", "white not bold"

        return [
            f"[{home_color}]{prefix}",
            f"[{home_color}]{home_score}" +
            f" [white dim]{separator}" +
            f" [not dim {away_color}]{away_score}",
            f"[{away_color}]{suffix}"
        ]

    home_team = match_.homeTeam.name
    away_team = match_.awayTeam.name

    scores = [
        _format_score(
            match_.score.regularTime or match_.score.fullTime, home_team, away_team),
        _format_score(match_.score.extraTime, "[white dim]Extra Time"),
        _format_score(match_.score.penalties, "[white dim]Penalties")
    ]

    return scores


def _update_matches_table(match: Match, table: Table, attributes: list[Any] = []):
    """Update matches table with a match score."""
    scores = format_match_score(match)  # [full_time, extra_time, penalties]
    scores[0].extend(attributes)        # Add attributes beside the main score

    if match.is_live:
        scores[0].append("[green not bold]live")

    add_rows(table, scores, styles={
        "1": "bold",
        "default": "dim"
    })


@formatting_error_handler
def format_team_matches(
    team_id: int,
    matches: list[Match],
    headers: list[str] = [],
    group_by: list[str] = []
) -> RenderableType:
    """Format stats and scores of team matches."""
    if not matches:
        return no_result()

    stats = _format_team_stats(team_id, matches)
    matches_details = format_matches(
        matches, headers=headers, group_by=group_by)
    if not stats:
        return matches_details
    return Group(Align.center(matches_details), Align.center(stats))


def _format_team_stats(team_id: int, matches: list[Match]) -> RenderableType | None:
    """Return a table with number of matches played, won, drawn, lost and scheduled."""
    def _calc_stats() -> dict[str, int]:
        stats = {
            "Played": 0,
            "Won": 0,
            "Drawn": 0,
            "Lost": 0,
            "Scheduled": 0
        }

        for match_ in matches:
            home_team_id = match_.homeTeam.id
            away_team_id = match_.awayTeam.id

            win, draw, loss, scheduled = [False] * 4
            match match_.score.winner:
                case "HOME_TEAM":
                    win = team_id == home_team_id
                    loss = not win
                case "AWAY_TEAM":
                    win = team_id == away_team_id
                    loss = not win
                case "DRAW":
                    draw = True
                case _:
                    scheduled = True

            stats["Scheduled"] += scheduled
            stats["Played"] += not scheduled
            stats["Drawn"] += draw
            stats["Won"] += win
            stats["Lost"] += loss

        return stats

    stats = _calc_stats()
    if stats["Played"] == 0:
        return None

    table = Table(box=box.ROUNDED, border_style="dim")
    columns = {
        "Played": {"header_style": "blue", "style": "blue bold", "justify": "center"},
        "Won": {"header_style": "green", "style": "green bold", "justify": "center"},
        "Drawn": {"header_style": "yellow", "style": "yellow bold", "justify": "center"},
        "Lost": {"header_style": "red", "style": "red bold", "justify": "center"},
    }

    if stats["Scheduled"] == 0:
        stats.pop("Scheduled")
    else:
        columns["Scheduled"] = {"header_style": "not bold",
                                "style": "not bold", "justify": "center"}

    add_columns(table, columns)
    add_rows(table, [list(stats.values())])

    return table


@formatting_error_handler
def format_h2h_matches(agg: Head2HeadAggregates | None) -> RenderableType:
    """Return number of matches, total goals and win record for both teams."""
    if not agg or not agg.numberOfMatches:
        return no_result()

    def validate_stats():
        assert stats["team1"]["wins"] == stats["team2"]["losses"]
        assert stats["team1"]["losses"] == stats["team2"]["wins"]
        assert stats["team1"]["draws"] == stats["team2"]["draws"]
        assert stats["total_matches"] == sum(val for key, val in stats["team1"].items()
                                             if key in ["wins", "losses", "draws"])

    stats = {
        "team1": {
            "name": agg.homeTeam.name,
            "wins": agg.homeTeam.wins,
            "draws": agg.homeTeam.draws,
            "losses": agg.homeTeam.losses
        },
        "team2": {
            "name": agg.awayTeam.name,
            "wins": agg.awayTeam.wins,
            "draws": agg.awayTeam.draws,
            "losses": agg.awayTeam.losses
        },
        "draws": agg.homeTeam.draws,
        "total_goals": agg.totalGoals,
        "total_matches": agg.numberOfMatches,
    }

    try:
        validate_stats()
    except AssertionError:
        raise ClickException("Invalid Response from the API.")

    table = Table(
        show_header=False,
        box=box.MINIMAL,
        show_edge=False,
        expand=True,
    )

    add_columns(table, columns={
        "W1": {"justify": "center", "style": "white on red bold", "width": stats['team1']['wins']},
        "D": {"justify": "center", "style": "white on blue bold", "width": stats['draws']},
        "W2": {"justify": "center", "style": "white on red bold", "width": stats['team2']['wins']},
    })

    table.add_row(
        f"{stats['team1']['name']} ({stats['team1']['wins']})",
        f"Draws ({stats['draws']})",
        f"{stats['team2']['name']} ({stats['team2']['wins']})"
    )

    text = Text.from_markup(
        f"\nNumber of Matches: {stats['total_matches']} [white]|[/white] Total Goals: {stats['total_goals']}\n",
        justify="center", style="cyan bold"
    )

    return Group(text, table, fit=False)


@formatting_error_handler
def format_competitions_list() -> Table:
    """Return a table with all available competitions."""
    table = Table(
        box=box.HORIZONTALS,
        border_style="dim",
        header_style="bold dim",
    )

    add_columns(table, columns={
        "ID": {"style": "yellow bold", "justify": "left"},
        "Name": {"style": "blue bold", "justify": "left"},
        "Region": {"style": "green bold", "justify": "left"},
        "Type": {"style": "red bold", "justify": "left"},
    })

    AVAILABLE_COMPETITIONS = load_json("competitions.json")
    add_rows(table, rows=[
        [competition["code"], competition["name"],
            competition["area"], competition["type"]]
        for competition in AVAILABLE_COMPETITIONS.values()
    ])

    return table


@formatting_error_handler
def format_teams_list() -> Table:
    """Return a table with all available teams."""
    table = Table(
        box=box.HORIZONTALS,
        border_style="dim",
        header_style="bold dim",
    )

    add_columns(table, columns={
        "ID": {"style": "yellow bold", "justify": "left"},
        "Full Name": {"style": "blue bold", "justify": "left"},
        "Short Name": {"style": "green bold", "justify": "left"},
        "Country": {"style": "red bold", "justify": "left"},
    })

    AVAILABLE_TEAMS = load_json("teams.json")
    rows = [
        [tla, team["full_name"] or "", team["short_name"] or "", team["country"]]
        for tla, teams in AVAILABLE_TEAMS.items()
        for team in teams.values()
    ]
    rows.sort(key=lambda row: (row[3], row[2]))
    add_rows(table, rows)

    return table
