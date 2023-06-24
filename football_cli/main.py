import os
import rich_click as click
from dotenv import load_dotenv
from models import update_forward_refs
from commands.competition import competition
from commands.team import team
from commands.matches import matches
from request_handler import RequestHandler


load_dotenv()


@click.group()
@click.option("--api-key", envvar="FOOTBALL_CLI_API_KEY", required=True,
              help="""Can be provided through an environment variable called FOOTBALL_CLI_API_KEY.\n
              Get it from https://www.football-data.org/client/register.""")
def cli(api_key):
    update_forward_refs()
    os.environ["FOOTBALL_CLI_API_KEY"] = api_key
    RequestHandler.API_KEY = api_key


for cmd in [competition, team, matches]:
    cli.add_command(cmd)


if __name__ == '__main__':
    cli()
