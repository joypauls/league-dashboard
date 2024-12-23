[![python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org)

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

### Usage

#### Get Today's Slate of Matches

Live scores and start times in local system time.

#### Get Upcoming Matches

#### Get Standings


## Commands

`lgdash today`

`lgdash schedule`

`lgdash standings`

`lgdash leagues`


