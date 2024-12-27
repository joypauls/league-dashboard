import streamlit as st
import pandas as pd
import os

from lgdash.client import FootballDataClient
from lgdash.config import FBD_ENV_VAR
from lgdash.leagues import SUPPORTED_LEAGUES, DEFAULT_LEAGUE

# TODO: should move this logic so user can use --help without the API key
api_token = os.getenv(FBD_ENV_VAR)
if not api_token:
    # TODO: fail more gracefully
    raise ValueError(
        f"API token not found. Please set the {FBD_ENV_VAR} environment variable."
    )
client = FootballDataClient(api_token)


@st.cache_data(ttl=120)
def fetch_standings(league: str) -> pd.DataFrame:
    """
    Fetch league data from an API.
    Replace with the actual API call for your use case.
    """
    df, _ = client.get_standings(league=league)
    return df


st.set_page_config(page_title="League Dashboard")

st.title("League Dashboard")
st.sidebar.title("Controls")

league = st.sidebar.selectbox("Select a League", options=SUPPORTED_LEAGUES.keys())

st.write(f"### {SUPPORTED_LEAGUES[league]['icon']} {SUPPORTED_LEAGUES[league]['name']}")
df = fetch_standings(league)
event = st.dataframe(
    df, hide_index=True, selection_mode="single-row", on_select="rerun"
)

row = event.selection.rows
filtered_df = df.iloc[row]
# if not filtered_df.empty:
#     st.write(filtered_df["team"].values[0])
#     st.image(filtered_df["crest"].values[0], width=50)
