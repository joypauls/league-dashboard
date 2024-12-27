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


@st.cache_data(ttl=30)
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
data = fetch_standings(league)
st.dataframe(data, hide_index=True)
