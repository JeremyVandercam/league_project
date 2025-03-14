import streamlit as st
import pandas as pd
import json
from datetime import datetime
import pytz
import requests
from urllib.parse import urlparse

# --- Configuration ---
url = "https://lolesports.com/api/gql?operationName=homeEvents&variables=%7B%22hl%22%3A%22en-GB%22%2C%22sport%22%3A%22lol%22%2C%22eventDateStart%22%3A%222025-03-12T23%3A00%3A00.000Z%22%2C%22eventDateEnd%22%3A%222025-03-14T22%3A59%3A59.999Z%22%2C%22eventState%22%3A%5B%22inProgress%22%2C%22completed%22%2C%22unstarted%22%5D%2C%22eventType%22%3A%22all%22%2C%22vodType%22%3A%5B%22recap%22%5D%2C%22pageSize%22%3A100%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22089916a64423fe9796f6e81b30e9bda7e329366a5b06029748c610a8e486d23f%22%7D%7D"
#PREDICTION_API_URL = "YOUR_PREDICTION_API_ENDPOINT"  # Prediction API URL

headers = {
    "accept": "*/*",
    "apollographql-client-name": "Esports Web",
    "apollographql-client-version": "2d15f08",
    "content-type": "application/json",
    "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\""
}


def get_match_data(url, headers):
    response = requests.get(url, headers=headers)
    return response.json()

#def predict(id):
    params = {"id": id}
    response = requests.post(PREDICTION_API_URL, headers=params)
    return response



# --- Streamlit App ---

st.set_page_config(
    page_title="LoL E-Sports Predictor",
    page_icon="🎮",
    layout="wide"
)

data = get_match_data(url, headers)


def parse_lol_data(data):
    """
    Parse JSON-Data and convert to Pandas DataFrame
    """
    all_tournaments = []

    for season in data.get('data', {}).get('seasons', []):
        for split in season.get('splits', []):
            split_name = split.get('name', '')
            split_region = split.get('region', '')
            split_start = split.get('startTime', '')
            split_end = split.get('endTime', '')
            split_id = split.get('id', '')


            for tournament in split.get('tournaments', []):
                tournament_name = tournament.get('name', '')
                tournament_id = tournament.get('id', '')

                league = tournament.get('league', {})
                league_name = league.get('name', '')
                league_image = league.get('image', '')

                all_tournaments.append({
                    'split_name': split_name,
                    'split_region': split_region,
                    'split_id' : split_id,
                    'split_start': split_start,
                    'split_end': split_end,
                    'tournament_name': tournament_name,
                    'tournament_id': tournament_id,
                    'league_name': league_name,
                    'league_image': league_image
                })

    df = pd.DataFrame(all_tournaments)

    # Change to Datetime
    if 'split_start' in df.columns:
        df['split_start'] = pd.to_datetime(df['split_start'])
        df['split_end'] = pd.to_datetime(df['split_end'])

        df['start_date'] = df['split_start'].dt.strftime('%d.%m.%Y')
        df['end_date'] = df['split_end'].dt.strftime('%d.%m.%Y')

        df = df.sort_values(by='split_start')

    return df

df = parse_lol_data(data)

st.header("LoL E-Sports Calendar 2025 🎮")

# Set Time filter
current_date = datetime.now(pytz.timezone('Europe/Andorra'))

col1, col2, col3 = st.columns(3)

show_past = col1.checkbox("Past Matches", value=False)
show_current = col2.checkbox("Live Matches", value=True)
show_future = col3.checkbox("Upcoming Matches", value=True)

# Set Region filter
regions = df['split_region'].unique().tolist()
selected_regions = st.multiselect("Select Regions", regions, default=regions)

# Set League Filter
leagues = df['league_name'].unique().tolist()
selected_leagues = st.multiselect("Select Leagues", leagues, default=leagues)

# Filtered Data Dataframe
filtered_df = df.copy()

# Apply Time Filter
if not show_past:
    filtered_df = filtered_df[filtered_df['split_end'] > current_date]
if not show_current:
    filtered_df = filtered_df[~((filtered_df['split_start'] <= current_date) & (filtered_df['split_end'] >= current_date))]
if not show_future:
    filtered_df = filtered_df[filtered_df['split_start'] <= current_date]

# Apply Region & League Filter
filtered_df = filtered_df[filtered_df['split_region'].isin(selected_regions)]
filtered_df = filtered_df[filtered_df['league_name'].isin(selected_leagues)]

# Sort by time
filtered_df = filtered_df.sort_values(by='split_start')

# Display of Filtered Data
if len(filtered_df) > 0:
        st.write(f"{len(filtered_df)} Matches selected")

        for i, row in enumerate(filtered_df.itertuples()):
            with st.container():
                cols = st.columns([1, 3, 2])

                with cols[0]:
                    # Status
                    if row.split_end < current_date:
                        st.markdown("🔴 **Finished**")
                    elif row.split_start <= current_date <= row.split_end:
                        st.markdown("🟢 **Live**")
                    else:
                        st.markdown("⚪ **Scheduled**")

                with cols[1]:
                    # Match Information
                    st.subheader(f"{row.league_name}: {row.tournament_name}")
                    st.write(f"**Split:** {row.split_name} ({row.split_region})")
                    st.write(f"**Tournament-ID:** {row.tournament_id}")

                with cols[2]:
                    # Tournament period
                    st.write(f"**Tournament period:** {row.start_date} - {row.end_date}")

                    # Days unitl Start/End
                    if row.split_start > current_date:
                        days_to_start = (row.split_start - current_date).days
                        st.write(f"**Starts in:** {days_to_start} Days")
                    elif row.split_end > current_date:
                        days_to_end = (row.split_end - current_date).days
                        st.write(f"**Ends in:** {days_to_end} Days")

            st.markdown("---")
else:
    st.warning("No matches found.")
