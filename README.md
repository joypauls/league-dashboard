# ⚽ League Dashboard

Currently requires a FootyStats API key and football-data.org API key.

```
FOOTYSTATS_API_KEY=<your key here>
FOOTBALLDATA_API_KEY=<your key here>
```

---

## Dev Notes

### Version Bump

1. Change in `pyproject.toml`
2. Change `__version__` variable in`src/lgdash/__init__.py`

Should automate this eventually.

### TODO

- show start time in system time zone

### Supported Leagues 

- start with just PL to get essentials out of the way then expand

### Match Retrieval Time Period

- default to today, emphasizes the fact that the data is live 
- keyword subcommands for `today`/`tomorrow`, + `upcoming` for scheduled

### Test Cases

#### Match Statuses

Look for Liverpool postponed match 2024 for handling postponed status.
Also some other statuses: https://docs.football-data.org/general/v4/lookup_tables.html#_enum_types
