import os
from rich.console import Console
from rich_click import Context, Parameter, ClickException, BadParameter, UsageError, Choice, prompt, style
from utils import to_isoformat, date_from_offset, load_json
from output_formation import format_competitions_list, format_teams_list


def group_callback(ctx: Context, param: Parameter, group: str | tuple[str] | None) -> str | None:
    """Prefix group number with 'GROUP_' and concatenate groups if many."""
    if group is None:
        return
    if isinstance(group, str):
        return f"GROUP_{group.upper()}"
    return ",".join([f"GROUP_{g.upper()}" for g in group])


def stage_callback(ctx: Context, param: Parameter, stage: str | tuple[str] | None) -> str | None:
    """Concatenate stages if many."""
    if stage is None:
        return
    if isinstance(stage, str):
        return stage
    if len(stage) == 0:
        return None
    return ",".join(stage)


def date_callback(ctx: Context, param: Parameter, date_: str | None) -> str | None:
    """Convert date string to upper case if one of ("today", "yesterday", "tomorrow") or to ISO format otherwise.
    
    :raise click.BadParameter: if invalid date
    """
    if date_ is None:
        return
    if date_.lower() in ["today", "yesterday", "tomorrow"]:
        return date_.upper()
    try:
        return to_isoformat(date_)
    except:
        raise BadParameter(f"{date_!r} is not a valid date.")


def last_callback(ctx: Context, param: Parameter, last: int | None) -> int | None:
    """Set context parameter `status` to 'FINISHED,LIVE' if last matches for a team are requested."""
    if last is None:
        return
    ctx.params["status"] = "FINISHED,LIVE"
    return last


def next_callback(ctx: Context, param: Parameter, next: int | None) -> int | None:
    """Set context parameter `status` to 'TIMED,SCHEDULED' if next matches for a team are requested."""
    if next is None:
        return
    ctx.params["status"] = "TIMED,SCHEDULED"
    return next


def last_h2h_callback(ctx: Context, param: Parameter, last: int | None) -> int | None:
    """Make sure `--last` is used with `--head2head` and set its default value.
    
    :raise click.UsageError: if `--last` is used without `--head2head`
    """
    DEFAULT = 1000
    if ctx.params.get("head2head"):
        return last or DEFAULT
    if last:
        raise UsageError("--last may only be used with --head2head/--h2h")
    return last


def time_frame_callback(ctx: Context, param: Parameter, time_frame: tuple[str, str] | None) -> tuple[str, str] | None:
    """Parse and validate time frame and set context parameters `dateFrom` and `dateTo`.
    
    :raise click.BadParameter: if invalid time frame
    """
    if time_frame is None:
        return
    try:
        try:
            offset1, offset2 = int(time_frame[0]), int(time_frame[1])   # offsets from today
            start_date, end_date = date_from_offset(offset1), date_from_offset(offset2, end=True)
        except:
            start_date, end_date = to_isoformat(time_frame[0]), to_isoformat(time_frame[1], end=True)
        if start_date >= end_date:  # exclusive end date
            raise ValueError()
        ctx.params["dateFrom"], ctx.params["dateTo"] = start_date, end_date
    except:
        raise BadParameter(
            "\n".join([
                f"{time_frame!r} is not a valid time frame.",
                "Expected two integers (representing offsets from today) or two valid dates (yyyy-mm-dd).",
                "First value must be less than or equal to the second one."
            ])
        )
    return time_frame


def team_id_callback(ctx: Context, param: Parameter, tla: str) -> int | None:
    """Map team name TLA (Three-Letter Abbreviation) to team ID.
    
    :raise click.BadParameter: if no such team found
    """
    if tla is None:
        return
    
    tla = tla.upper()
    AVAILABLE_TEAMS = load_json("teams.json")
    if tla not in AVAILABLE_TEAMS:
        raise BadParameter("No such team. Check available teams using '--all' flag.")
    
    teams_dict: dict[str, dict] = AVAILABLE_TEAMS[tla]
    ids = list(teams_dict.keys())
    if len(ids) == 1:
        return int(ids[0])
    
    teams = list(teams_dict.values())    
    message = style("Multiple teams with the same code, please choose one of the teams below:\n", fg="yellow")
    for i, team in enumerate(teams):
        message += style(f"{i + 1}. {team['full_name']} ({team['country']})\n", fg="green")
    
    i = prompt(message, type=Choice(list(map(str, range(1, len(teams) + 1)))))
    team_id = ids[int(i) - 1]
    
    return int(team_id)


def competition_id_callback(ctx: Context, param: Parameter, code: str) -> str | None:
    """Convert competition id (code) to upper case.
    
    :param code: competition id

    :raise click.BadParameter: if no such competition found
    """
    if code is None:
        return code
    
    code = code.upper()
    AVAILABLE_COMPETITIONS = load_json("competitions.json")
    if code not in AVAILABLE_COMPETITIONS:
        raise BadParameter("No such competition. Check available competition using '--all' flag.")
    
    return code


def list_competitions_callback(ctx: Context, param: Parameter, value: bool):
    """List available competitions and exit.
    
    :raise click.BadParameter: if available competitions data couldn't be found and need to be fetched
    """
    if not value:
        return
    
    competitions = format_competitions_list()
    if len(competitions.rows) == 0:
        raise ClickException("\n".join([
            "Data for available competitions are not found.",
            "Please run `data_preparation.py` first to generate data."
        ]))
    
    Console().print(competitions)
    
    ctx.exit(0)


def list_teams_callback(ctx: Context, param: Parameter, value: bool):
    """List available teams and exit.
    
    :raise click.BadParameter: if available teams data couldn't be found and need to be fetched
    """
    if not value:
        return
    
    teams = format_teams_list()
    if len(teams.rows) == 0:
        raise ClickException("\n".join([
            "Data for available teams are not found.",
            "Please run `data_preparation.py` first to generate data."
        ]))
    
    console = Console()
    pager = os.getenv("MANPAGER") or os.getenv("PAGER")
    if pager:   # use pager if available (list too long)
        with console.pager(styles=True):
            console.print(teams)
    else:
        console.print(teams)
    
    ctx.exit(0)
