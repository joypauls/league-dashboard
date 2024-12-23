[![python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org)
[![PyPI version](https://badge.fury.io/py/lgdash.svg)](https://badge.fury.io/py/lgdash)

⚠️ This project is currently under active development and considered experimental.

# League Dashboard (lgdash)

Soccer at the command line. ⚽

Under the hood the app is calling the [football-data.org](https://www.football-data.org/) API, so an API token from that service is required. Register [here](https://www.football-data.org/pricing) to get one. 

## Features

- live scores
- league standings
- league schedules

### Currently Supported Leagues

- Premier League (England 🏴󠁧󠁢󠁥󠁮󠁧󠁿)
- La Liga (Spain 🇪🇸)
- Serie A (Italy 🇮🇹)
- Bundesliga (Germany 🇩🇪)
- Ligue 1 (France 🇫🇷)
- UEFA Champions League (Europe)

## Quick Start

### Get API Token

If you don't have one, register for an API token [here](https://www.football-data.org/pricing).

Then add this line with your token to `.zshrc` or another appropriate startup file.
```
export FOOTBALLDATA_API_TOKEN=<token>
```

### Install

Available on PyPI.

`pip install lgdash`

### How to Use

#### Today's Slate of Matches

Live scores and start times in local system time.

Example: Premier League (Default)  
`lgdash today`, or `lgdash today -l PL`

Example: Serie A  
`lgdash today -l SA`

#### Standings

Current state of a league's standings with some statistics for each team.

Example: Premier League (Default)  
`lgdash standings`

Example: Serie A  
`lgdash standings -l SA`

#### Help

Each command and subcommand supports the `--help` option, for example:

`lgdash --help` and `lgdash today --help`


## Commands

`lgdash today`
- get live scores and today's scheduled matches
- `-l, --league`: specify a league code

`lgdash schedule`
- get upcoming matches
- `-l, --league`: specify a league code
- `-d, --days`: specify number of days in future

`lgdash standings`
- get league standings
- `-l, --league`: specify a league code

`lgdash leagues`
- get all supported league codes


