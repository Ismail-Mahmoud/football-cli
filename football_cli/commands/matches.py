import rich_click as click
from rich.console import Console
from options_validator import OptionsValidator
from request_handler import RequestHandler
from models import MatchSet
from output_formation import format_matches, format_h2h_matches
from options_callbacks import date_callback, time_frame_callback, last_h2h_callback


@click.command()
@click.pass_context
@click.option("--live", "status", flag_value="LIVE", help="Show live matches.")
@click.option("--date", type=str,
              help="yyyy-mm-dd or one of [YESTERDAY, TODAY, TOMORROW] (default is TODAY).", callback=date_callback)
@click.option("--time-frame", nargs=2, type=str,
              help="""Time period during which matches will be shown.\n
                Either two valid dates representing start and end dates (inclusive),\n
                or two integers representing offsets from today.\n
                For example, -2 3 means 2 days in the past and 3 days in the future (with today included).""",
              callback=time_frame_callback)
@click.option("--competitions", type=str,
              help="Comma-separated competition IDs to show matches for (default is all available competitions).")
@click.option("--head2head", "--h2h", type=int, is_eager=True,
              help="Match ID to show summary of match history between the two teams.")
@click.option("--last", "-n", "limit", type=click.IntRange(min=1),
              help="Only used with --head2head to show summary of the last n matches.",
              callback=last_h2h_callback)
@click.option("--show-id", is_flag=True, help="Show match id used to get head-to-head matches summary (check matches --head2head).")
def matches(ctx, status, date, time_frame, competitions, head2head, limit, show_id, dateFrom=None, dateTo=None):
    """Show match scores.

    \b
    Mutually exclusive options:
    * --date and --time-frame
    * --live and all other options except for --competitions and --show-id
    * --head2head/--last and all other options
    """
    validator = OptionsValidator(
        ctx=ctx,
        meo_groups=[
            (["date"], ["time_frame"]),
            (["live"], ["date", "time_frame", "head2head", "last"]),
            (["head2head", "last"], ["live", "date", "time_frame", "competitions"])
        ]
    )
    validator.validate_options()
    if errors := validator.errors:
        raise click.UsageError("\n".join(errors))

    if head2head:
        result = RequestHandler(
            path=f"matches/{head2head}/head2head",
            params=ctx.params.copy()
        ).send_request()

        aggregates = MatchSet(**result).aggregates
        output = format_h2h_matches(aggregates)
    else:
        result = RequestHandler(
            path=f"matches",
            params=ctx.params.copy()
        ).send_request()

        matches = MatchSet(**result).matches
        output = format_matches(
            matches,
            group_by=["date", "competition", "season", "stage", "matchday", "group"],
            headers=["time"] + (["id"] if show_id else [])
        )

    Console().print(output, justify="center")
