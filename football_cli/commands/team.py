import rich_click as click
from rich.console import Console
from options_validator import OptionsValidator
from request_handler import RequestHandler
from models import Team, MatchSet
from output_formation import format_team, format_team_matches
from options_callbacks import list_teams_callback, team_id_callback, time_frame_callback, last_callback, next_callback


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--all", is_flag=True, default=False, is_eager=True,
              help="List all available teams with their IDs and exit.", callback=list_teams_callback)
@click.argument("team_id", type=str, required=True, callback=team_id_callback)
def team(ctx, team_id, all):
    """Show team info.

    If no command provided, show squad info.
    """
    ctx.params["team_id"] = int(ctx.params["team_id"])
    if not ctx.invoked_subcommand:
        result = RequestHandler(
            path=f"teams/{team_id}",
            params=ctx.params.copy()
        ).send_request()

        team = Team(**result)
        output = format_team(team)

        Console().print(output, justify="center")


@team.command()
@click.pass_context
@click.option("--season", type=int, help="Season start year (default is the current season).")
@click.option("--competitions", type=str, help="Limit the results on specific competitions (comma-separated IDs).")
@click.option("--home", "venue", flag_value="HOME", help="Only show home matches.")
@click.option("--away", "venue", flag_value="AWAY", help="Only show away matches.")
@click.option("--time-frame", nargs=2, type=str,
              help="""Time period during which matches will be shown.\n
                Either two valid dates representing start and end dates (inclusive),\n
                or two integers representing offsets from today.\n
                For example, -2 3 means 2 days in the past and 3 days in the future (with today included).""",
              callback=time_frame_callback)
@click.option("--last", "-l", "limit", is_flag=False, flag_value=1000, type=click.IntRange(min=1),
              help="""Show last l matches for the team in the current season.\n
                If no value provided, show all previous matches.""", callback=last_callback)
@click.option("--next", "-n", is_flag=False, flag_value=100, type=click.IntRange(min=1),
              help="""Show next n matches for the team in the current season.\n
                If no value provided, show all next matches.""", callback=next_callback)
@click.option("--show-id", is_flag=True, help="Show match id used to get head-to-head matches summary (check matches --head2head).")
def matches(ctx, season, competitions, venue, time_frame, limit, next, show_id, status=None, dateFrom=None, dateTo=None):
    """Show team matches.

    \b
    Mutually exclusive options:
        * --season and --time-frame and --last/--next
        * --last and --next
    """
    validator = OptionsValidator(
        ctx=ctx,
        meo_groups=[
            (["season"], ["time_frame", "limit", "next"]),
            (["time_frame"], ["limit", "next"]),
            (["limit"], ["next"])
        ]
    )
    validator.validate_options()
    if errors := validator.errors:
        raise click.UsageError("\n".join(errors))

    team_id = ctx.parent.params["team_id"]
    result = RequestHandler(
        path=f"teams/{team_id}/matches",
        params=ctx.params.copy()
    ).send_request()

    matches = MatchSet(**result).matches[:next]
    output = format_team_matches(
        team_id=team_id, matches=matches,
        group_by=["competition", "season", "stage", "group"],
        headers=["date", "time"] + (["id"] if show_id else [])
    )

    Console().print(output, justify="center")
