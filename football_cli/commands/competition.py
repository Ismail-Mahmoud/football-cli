import rich_click as click
from rich.console import Console
from pydantic import ValidationError
from options_validator import OptionsValidator
from request_handler import RequestHandler
from models import Competition, Standings, MatchSet, CompetitionTeams, TopScorers
from output_formation import format_champions, format_standings, format_matches, format_teams, format_top_scorers
from options_callbacks import list_competitions_callback, competition_id_callback, date_callback, stage_callback, group_callback, time_frame_callback
from exception_handling import APIResponseParsingError
from utils import load_json


OPTIONS = load_json("options.json")
STAGES_LIST = OPTIONS.get("stages")
GROUPS_LIST = OPTIONS.get("groups")


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--all", is_flag=True, default=False, is_eager=True,
              help="List all available competitions with their IDs and exit.", callback=list_competitions_callback)
@click.argument("competition_id", type=str, required=True, callback=competition_id_callback)
def competition(ctx, competition_id, all):
    """Show competition info.

    If no command provided, show champions of previous available seasons.
    """
    if not ctx.invoked_subcommand:
        result = RequestHandler(
            path=f"competitions/{competition_id}",
            params=ctx.params.copy()
        ).send_request()

        try:
            competition = Competition(**result)
        except ValidationError as e:
            raise APIResponseParsingError(e)

        output = format_champions(competition)

        Console().print(output, justify="center")


@competition.command()
@click.pass_context
@click.option("--season", type=int, help="Season start year (default is the current season).")
@click.option("--date", type=str, help="Standings at a specific date (yyyy-mm-dd).", callback=date_callback)
def standings(ctx, season, date):
    """Show competition standings.

    --season and --date are mutually exclusive.
    """
    validator = OptionsValidator(
        ctx=ctx,
        meo_groups=[(["season"], ["date"])]
    )
    validator.validate_options()
    if errors := validator.errors:
        raise click.UsageError("\n".join(errors))

    competition_id = ctx.parent.params['competition_id']
    result = RequestHandler(
        path=f"competitions/{competition_id}/standings",
        params=ctx.params.copy()
    ).send_request()

    standings = Standings(**result)
    output = format_standings(standings)

    Console().print(output, justify="center")


@competition.command()
@click.pass_context
@click.option("--season", type=int, help="Season start year (default is the current season).")
@click.option("--matchday", type=click.IntRange(min=1), help="Fixture.")
@click.option("--stage", type=click.Choice(STAGES_LIST, case_sensitive=False) if STAGES_LIST else str, multiple=True,
              help="In case of a cup competition (can be repeated to select multiple stages).", callback=stage_callback)
@click.option("--group", type=click.Choice(GROUPS_LIST, case_sensitive=False) if GROUPS_LIST else str,
              help="In case of a cup competition.", callback=group_callback)
@click.option("--time-frame", nargs=2, type=str,
              help="""Time period during which matches will be shown.\n
                Either two valid dates representing start and end dates (inclusive),\n
                or two integers representing offsets from today.\n
                For example, -2 3 means 2 days in the past and 3 days in the future (with today included).""",
              callback=time_frame_callback)
@click.option("--live", "status", flag_value="LIVE", help="Show live matches.")
@click.option("--past", "status", flag_value="FINISHED", help="Show matches played so far in the current season.")
@click.option("--upcoming", "status", flag_value="TIMED,SCHEDULED", help="Show matches scheduled for the rest of the season.")
@click.option("--show-id", is_flag=True, help="Show match id used to get head-to-head matches summary (check matches --head2head).")
def matches(ctx, season, matchday, stage, group, time_frame, status, show_id, dateFrom=None, dateTo=None):
    """Show competition matches.

    \b
    Mutually exclusive options:
        * --season and --time-frame
        * --live/--past/--upcoming and all other options except for --show-id
        * --stage and --group/--matchday\b
          (By default, --stage is automatically considered GROUP_STAGE if --group/--matchday is specified)
    """
    validator = OptionsValidator(
        ctx=ctx,
        meo_groups=[
            (["time_frame"], ["season", "status"]),
            (["status"], ["season", "matchday", "stage", "group", "time_frame"]),
            (["stage"], ["group", "matchday"])
        ]
    )
    validator.validate_options()
    if errors := validator.errors:
        raise click.UsageError("\n".join(errors))

    competition_id = ctx.parent.params["competition_id"]
    result = RequestHandler(
        path=f"competitions/{competition_id}/matches",
        params=ctx.params.copy()
    ).send_request()

    matches = MatchSet(**result).matches
    output = format_matches(
        matches,
        group_by=["competition", "season", "stage", "matchday", "group"],
        headers=["date", "time"] + (["id"] if show_id else [])
    )

    Console().print(output, justify="center")


@competition.command()
@click.pass_context
@click.option("--season", type=int, help="Season start year (default is the current season).")
def teams(ctx, season):
    """List competing teams."""
    competition_id = ctx.parent.params["competition_id"]
    result = RequestHandler(
        path=f"competitions/{competition_id}/teams",
        params=ctx.params.copy()
    ).send_request()

    teams = CompetitionTeams(**result).teams
    output = format_teams(teams)

    Console().print(output, justify="center")


@competition.command()
@click.pass_context
@click.option("--season", type=int, help="Season start year (default is the current season).")
@click.option("--top", "-n", "limit", type=click.IntRange(min=1), default=5, show_default=True, help="Top n scorers.")
def scorers(ctx, season, limit):
    """Show competition top scorers."""
    competition_id = ctx.parent.params["competition_id"]
    result = RequestHandler(
        path=f"competitions/{competition_id}/scorers",
        params=ctx.params.copy()
    ).send_request()

    scorers = TopScorers(**result).scorers
    output = format_top_scorers(scorers)

    Console().print(output, justify="center")
