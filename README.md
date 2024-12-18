# League Dashboard ⚽📈

Currently requires a football-data.org API key.

```
FOOTBALLDATA_API_KEY=<your key here>
```


## Quick Start

### Get API Key

### Install

### Use

#### Get Scores

#### Get Upcoming Matches

#### Get Standings


## Commands


---

## Development

`poetry install`
- install package locally
`poetry run lgdash`
- run package CLI with local installation



### TODO

- move sort to display logic
- combine matches requests all into one and filter when possible
- avoid changing values too much from API's (e.g. status) keep that in the display logic instead
- setup pytest
- backup default to something when detecting system timezone in case of failure

### Version Bump

1. Change in `pyproject.toml`
2. Change `__version__` variable in`src/lgdash/__init__.py`

Should automate this eventually.

### Supported Leagues 

- start with just PL to get essentials out of the way then expand

### Match Retrieval Time Period

- default to today, emphasizes the fact that the data is live 
- keyword subcommands for `today`/`tomorrow`, + `upcoming` for scheduled

### Test Cases

#### Match Statuses

Look for Liverpool postponed match 2024 for handling postponed status.
Also some other statuses: https://docs.football-data.org/general/v4/lookup_tables.html#_enum_types
