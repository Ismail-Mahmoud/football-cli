# Football CLI
A command line interface to get information about various football competitions, teams and matches.

# Installation
Clone this repo to your local machine:
```bash
git clone https://github.com/Ismail-Mahmoud/football-cli.git
```
Go to the project directory:
```bash
cd football-cli
```
[Optional] Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```
Install the package:
```bash
pip3 install .
```

# Getting Started

## 1. Config
First, you need to get your API key from https://www.football-data.org/client/register.

Then, set `FOOTBALL_CLI_API_KEY` in [.env](./.env) with the key you've got. Otherwise you'll need to pass it every time you run a command using `--api-key`.

In addition to API key, there are extra few environment variables to set in [.env](./.env) that are useful for debugging:
- `SHOW_ERROR_DETAILS`: to show detailed error messages instead of just a brief message (`1` for `True`, any other value for `False`).
- `SAVE_API_RESPONSE`: to save API response in `response.json` under [football_cli/data](./football_cli/data/) (`1` for `True`, any other value for `False`).


## 2. Shell completion
This is an optional step where can enable shell completion to get suggestions for commands and options when pressing `tab` as you're typing.

To get completion enabled, run the following script with your shell name:
```bash
./scripts/shell_completion.sh <SHELL_NAME>
```
**This will generate a new script, save it to `football_complete.<bash/zsh>` and source it in your shell config file if you're using `bash`/`zsh`, or to `~/.config/fish/completions/football_complete.fish` if you're using `fish`.**

Note that completion is only supported for `bash`, `zsh` and `fish`. If you want to enable completion for a different shell, check [Adding Support for a Shell](https://click.palletsprojects.com/en/8.1.x/shell-completion/#adding-support-for-a-shell).

## 3. Data directory
Nothing to be done here, but this is just an illustration for the data directory [football_cli/data](./football_cli/data/).

This directory contains basic info about available competitions/teams (mainly IDs) to select from.

These files were generated using [football_cli/data_preparation.py](./football_cli/data_preparation.py) script. If this directory is lost for some reason, you'll need to run the script to regenerate data or just run this command: `football_gen`.

# Usage
There are 3 main commands to use:
1. <code>competition</code>: to show competitions info.
2. <code>team</code>: to show teams info.
3. <code>matches</code>: to show past, live and upcoming matches.


## Competitions
#### List all available competitions with their IDs:
```bash
football competition --all
```
#### Champions of previous seasons:
```bash
football competition <ID>
```
#### Standings:
```bash
football competition <ID> standings [OPTIONS]
```
#### Top scorers:
```bash
football competition <ID> scorers [OPTIONS]
```
#### Competition matches:
```bash
football competition <ID> matches [OPTIONS]
```
#### Competition teams:
```bash
football competition <ID> teams [OPTIONS]
```
#### Show help:
```bash
football competition --help
```

## Teams
#### List all available teams with their IDs:
```bash
football team --all
```
#### Team squad:
```bash
football team <ID>
```
#### Team matches:
```bash
football team <ID> matches [OPTIONS]
```
#### Show help;
```bash
football team --help
```

## Matches
#### Show available matches:
```bash
football matches [OPTIONS]
```
#### Show help:
```bash
football matches --help
```

# Demo
For live demo, run [scripts/demo.sh](./scripts/demo.sh)
<details>
  <summary>Premier League champions</summary>

  ![PL champions](https://i.imgur.com/Qln0BPc.gif)
</details>

<details>
  <summary>Premier League standings</summary>

  ![PL standings](https://i.imgur.com/GkoPP0D.gif)
</details>

<details>
  <summary>Premier League top 5 scorers</summary>
  
  ![PL top scorers](https://i.imgur.com/NXVaAUL.gif)
</details>

<details>
  <summary>Premier League matchday 38</summary>
  
  ![PL matches](https://i.imgur.com/LxQsidp.gif)
</details>

<details>
  <summary>World Cup matches</summary>
  
  ![WC matches](https://i.imgur.com/lIMIVJP.gif)
</details>

<details>
  <summary>UEFA Champions League semi-final/final matches</summary>
  
  ![CL matches](https://i.imgur.com/nVQZeyJ.gif)
</details>


<details>
  <summary>Team matches of the whole season</summary>
  
  ![FCB matches](https://i.imgur.com/zud8yeL.gif)
</details>

<details>
  <summary>Last/Next <b>N</b> matches for a team</summary>
  You can specify whether to show only home matches (<code>--home</code>), away matches (<code>--away</code>) or both (no flag).
  
  ![ARS matches](https://i.imgur.com/fWaRzuL.gif)
</details>

<details>
  <summary>Team squad</summary>
  
  ![FCB squad](https://i.imgur.com/tMwJh5y.gif)
</details>

<details>
  <summary>Today's/Live matches</summary>
  
  ![Matches today](https://i.imgur.com/e3QY9RY.gif)
</details>

<details>
  <summary>Matches of the big 5 leagues at a specific date</summary>
  
  ![Matches date/competitions](https://i.imgur.com/HINIhl1.gif)
</details>

<details>
  <summary>Matches within a time frame</summary>
  Note that <b>-3</b> means the last three days and <b>5</b> means the next five days (with today included).

  Alternatively, You can provide two valid dates.
  
  ![Matches time frame](https://i.imgur.com/SAjYnJg.gif)
</details>


<details>
  <summary>Head-to-head matches</summary>
  Note that you need to get match ID first using <code>--show-id</code> flag.
  
  ![Matches H2H](https://i.imgur.com/9Zdd7h3.gif)
</details>
