import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import pytz
import requests

# --- Configuration ---
url = "https://lolesports.com/api/gql?operationName=homeEvents&variables=%7B%22hl%22%3A%22en-GB%22%2C%22sport%22%3A%22lol%22%2C%22eventDateStart%22%3A%222025-03-12T23%3A00%3A00.000Z%22%2C%22eventDateEnd%22%3A%222025-03-17T22%3A59%3A59.999Z%22%2C%22eventState%22%3A%5B%22inProgress%22%2C%22completed%22%2C%22unstarted%22%5D%2C%22eventType%22%3A%22all%22%2C%22vodType%22%3A%5B%22recap%22%5D%2C%22pageSize%22%3A100%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22089916a64423fe9796f6e81b30e9bda7e329366a5b06029748c610a8e486d23f%22%7D%7D"
PREDICTION_API_URL = "https://leagueproject-284519494207.europe-west1.run.app/predict?side=1&firstblood=0&firstdragon=0&firstherald=1&firstbaron=1&firsttower=0&firstmidtower=0&firsttothreetowers=0&turretplates=3&opp_turretplates=2&goldat10=15071&xpat10=18472&csat10=346&opp_goldat10=14898&opp_xpat10=19153&opp_csat10=349&golddiffat10=173&xpdiffat10=-681&csdiffat10=-3&killsat10=0&assistsat10=0&deathsat10=0&opp_killsat10=0&opp_assistsat10=0&opp_deathsat10=0&goldat15=22726&xpat15=28780&csat15=540&opp_goldat15=23480&opp_xpat15=30504&opp_csat15=545&golddiffat15=-754&xpdiffat15=-1724&csdiffat15=-5&killsat15=0&assistsat15=0&deathsat15=2&opp_killsat15=2&opp_assistsat15=2&opp_deathsat15=0&goldat20=30923&xpat20=38143&csat20=669&opp_goldat20=33135&opp_xpat20=42547&opp_csat20=696&golddiffat20=-2212&xpdiffat20=-4404&csdiffat20=-27&killsat20=3&assistsat20=9&deathsat20=6&opp_killsat20=6&opp_assistsat20=13&opp_deathsat20=3&goldat25=37681&xpat25=47022&csat25=775&opp_goldat25=46904&opp_xpat25=59120&opp_csat25=869&golddiffat25=-9223&xpdiffat25=-12098&csdiffat25=-94&killsat25=5&assistsat25=15&deathsat25=17&opp_killsat25=17&opp_assistsat25=34&opp_deathsat25=5"

headers = {
    "accept": "*/*",
    "apollographql-client-name": "Esports Web",
    "apollographql-client-version": "2d15f08",
    "content-type": "application/json",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}


def get_match_data(url, headers):
    response = requests.get(url, headers=headers)
    return response.json()


def get_match_stats(match_id: str, startingTime: str):
    url = f"https://feed.lolesports.com/livestats/v1/details/{match_id}"

    params = {"startingTime": startingTime, "participantIds": "1_2_3_4_5_6_7_8_9_10"}

    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7",
        "origin": "https://lolesports.com",
        "priority": "u=1, i",
        "referer": "https://lolesports.com/",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers, params=params)

    return response.json()


def predict(id):
    response = requests.get(PREDICTION_API_URL, params={"id": id})
    return response.json()


def predict(match_id, start_time):
    params = {"match_id": match_id, "start_time": start_time}


# response = requests.get(PREDICTION_API_URL, params=params)
# return response.json()


# --- Streamlit App ---

st.set_page_config(page_title="LoL E-Sports Predictor", page_icon="🎮", layout="wide")

data = get_match_data(url, headers)
if "predictions" not in st.session_state:
    st.session_state.predictions = {}


def parse_lol_data(data):
    """
    Parse JSON-Data and convert to Pandas DataFrame
    """
    all_matches = []

    for event in data["data"]["esports"]["events"]:
        if event["__typename"] == "EventMatch" and "match" in event:
            # Basic info about Match
            match_id = event.get("id", "")
            block_name = event.get("blockName", "")
            start_time = event.get("startTime", "")
            state = event.get("state", "")

            # League info
            league = event.get("league", {})
            league_name = league.get("name", "")
            league_image = league.get("image", "")

            # Tournament info
            tournament = event.get("tournament", {})
            tournament_name = tournament.get("name", "") if tournament else ""

            # Match info
            match = event.get("match", {})
            match_type = match.get("type", "")
            match_state = match.get("state", "")

            # Strategy (Best of X)
            strategy = match.get("strategy", {})
            best_of = strategy.get("count", 0) if strategy else 0

            # Team info
            teams = []
            scores = []
            winners = []

            for team in match.get("matchTeams", []):
                team_name = team.get("name", "")
                team_code = team.get("code", "")
                team_image = team.get("image", "")

                result = team.get("result", {})
                game_wins = result.get("gameWins", 0) if result else 0
                outcome = result.get("outcome", "") if result else ""

                teams.append(f"{team_code} ({team_name})")
                scores.append(game_wins)
                winners.append(outcome == "win")

            # Game info
            games_completed = sum(
                1 for game in match.get("games", []) if game.get("state") == "completed"
            )
            total_games = len(match.get("games", []))

            # Team 1 vs Team 2 String creation
            teams_str = " vs ".join(teams) if teams else "TBD"
            score_str = f"{scores[0]} - {scores[1]}" if len(scores) >= 2 else "0 - 0"

            # Winner
            winner = ""
            if any(winners):
                winner_index = winners.index(True) if True in winners else -1
                winner = (
                    teams[winner_index]
                    if winner_index >= 0 and winner_index < len(teams)
                    else ""
                )

            all_matches.append(
                {
                    "match_id": match_id,
                    "league_name": league_name,
                    "tournament_name": tournament_name,
                    "block_name": block_name,
                    "start_time": start_time,
                    "state": state,
                    "match_type": match_type,
                    "match_state": match_state,
                    "best_of": best_of,
                    "teams": teams_str,
                    "score": score_str,
                    "winner": winner,
                    "games_completed": games_completed,
                    "total_games": total_games,
                }
            )

    df = pd.DataFrame(all_matches)

    # Change to Datetime

    df["start_time"] = pd.to_datetime(df["start_time"]) + timedelta(hours=1)

    df["start_date"] = df["start_time"].dt.strftime("%d.%m.%Y")
    df["start_time_display"] = df["start_time"].dt.strftime("%H:%M")

    # Sort by Starttime
    df = df.sort_values(by="start_time")

    return df


df = parse_lol_data(data)

st.header("LoL E-Sports Match Calendar")

current_date = datetime.now(pytz.timezone("Europe/Andorra"))

col1, col2, col3 = st.columns(3)

show_past = col1.checkbox("Past Matches", value=False)
show_current = col2.checkbox("Live Matches", value=True)
show_future = col3.checkbox("Upcoming Matches", value=True)

# Set League Filter
leagues = df["league_name"].unique().tolist()
selected_leagues = st.multiselect("Select Leagues", leagues, default=leagues)

# Set Match-Status Filter
states = df["state"].unique().tolist()
selected_states = st.multiselect("Status filtern", states, default=states)

# Filtered Data Dataframe
filtered_df = df.copy()


if not show_past:
    filtered_df = filtered_df[filtered_df["start_time"] > current_date]
if not show_current:
    today_start = datetime.combine(
        current_date.date(), datetime.min.time(), tzinfo=pytz.timezone("Europe/Andorra")
    )
    today_end = datetime.combine(
        current_date.date(), datetime.max.time(), tzinfo=pytz.timezone("Europe/Andorra")
    )
    filtered_df = filtered_df[
        ~(
            (filtered_df["start_time"] >= today_start)
            & (filtered_df["start_time"] <= today_end)
        )
    ]
if not show_future:
    filtered_df = filtered_df[filtered_df["start_time"] <= current_date]

# Apply League & Status Filter
if selected_leagues:
    filtered_df = filtered_df[filtered_df["league_name"].isin(selected_leagues)]
if selected_states:
    filtered_df = filtered_df[filtered_df["state"].isin(selected_states)]

# Display of Filtered Data
if len(filtered_df) > 0:
    st.write(f"{len(filtered_df)} Matches selected")

    # Matches nach Datum gruppieren
    filtered_df["date_group"] = filtered_df["start_time"].dt.date
    date_groups = filtered_df["date_group"].unique()

    for date in sorted(date_groups):
        date_matches = filtered_df[filtered_df["date_group"] == date]
        st.subheader(date.strftime("%d.%m.%Y"))

        for i, row in enumerate(date_matches.itertuples()):
            with st.container():
                cols = st.columns([1, 3, 2, 1])

                with cols[0]:
                    # Status
                    if row.state == "completed":
                        st.markdown("🏆 **Finished**")
                    elif row.state == "inProgress":
                        st.markdown("🟢 **Live**")
                    else:
                        st.markdown("⏰ **" + row.start_time_display + "**")

                with cols[1]:
                    # Match info
                    st.subheader(f"{row.teams}")
                    st.write(f"**League:** {row.league_name} - {row.tournament_name}")
                    if row.block_name:
                        st.write(f"**Phase:** {row.block_name}")
                    st.write(f"**Format:** Best of {row.best_of}")

                with cols[2]:
                    # Result
                    if row.state == "completed":
                        st.subheader(f"Score: {row.score}")
                        st.write(f"**Winner:** {row.winner}")
                    elif row.state == "inProgress":
                        st.subheader(f"Current Score: {row.score}")
                        st.write(
                            f"**Played matches:** {row.games_completed}/{row.total_games}"
                        )
                    else:
                        st.write("Game has not started")

                with cols[3]:
                    # Prediction button
                    button_key = f"predict_{row.match_id}"
                    if st.button("Predict", key=button_key):
                        # Get prediction and store in session state
                        prediction_result = predict(row.match_id, row.start_time)

                        st.session_state.predictions[row.match_id] = prediction_result

                    # Display prediction if available
                    if row.match_id in st.session_state.predictions:
                        prediction = st.session_state.predictions[row.match_id]
                        if "error" in prediction:
                            st.error("Prediction failed")
                        else:
                            st.success(
                                f"Home team win probability: {prediction.get('pred', 0):.1%}"
                            )

                st.markdown("---")
else:
    st.warning("No matches found.")
