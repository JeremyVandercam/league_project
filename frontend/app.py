import numpy as np
import streamlit as st
import pandas as pd
import requests
import json

from datetime import datetime, timedelta
from typing import Dict, Any


# --- Configuration ---
class Matches:
    def __init__(self):
        self.base_url = "https://lolesports.com/api/gql"

    def get_matches_data(self, date_start: str, date_end: str) -> Dict[str, Any]:
        """
        Fetch match data from the LOL Esports API

        Args:
            date_start: Start date in ISO format (YYYY-MM-DDThh:mm:ss.sssZ)
            date_end: End date in ISO format (YYYY-MM-DDThh:mm:ss.sssZ)

        Returns:
            JSON response data
        """
        query_params = {
            "operationName": "homeEvents",
            "variables": {
                "hl": "en-GB",
                "sport": "lol",
                "eventDateStart": date_start,
                "eventDateEnd": date_end,
                "eventState": ["inProgress", "completed", "unstarted"],
                "eventType": "all",
                "vodType": ["recap"],
                "pageSize": 100,
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "089916a64423fe9796f6e81b30e9bda7e329366a5b06029748c610a8e486d23f",
                }
            },
        }

        # Convert query params to correct URL format
        url_variables = json.dumps(query_params["variables"]).replace(" ", "")
        url_extensions = json.dumps(query_params["extensions"]).replace(" ", "")
        url = f"{self.base_url}?operationName={query_params['operationName']}&variables={url_variables}&extensions={url_extensions}"

        headers = {
            "accept": "*/*",
            "apollographql-client-name": "Esports Web",
            "apollographql-client-version": "2d15f08",
            "content-type": "application/json",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        }

        response = requests.get(url, headers=headers)

        return response.json()

    @staticmethod
    def extract_event_info(event: dict) -> dict:
        """Extract basic match and event information."""
        return {
            "match_id": event.get("id", ""),
            "block_name": event.get("blockName", ""),
            "start_time": event.get("startTime", ""),
            "state": event.get("state", ""),
            "league_name": event.get("league", {}).get("name", ""),
            "tournament_name": event.get("tournament", {}).get("name", ""),
            "match_type": event.get("match", {}).get("type", ""),
            "match_state": event.get("match", {}).get("state", ""),
            "best_of": event.get("match", {}).get("strategy", {}).get("count", 0),
        }

    @staticmethod
    def extract_team_info(match: dict) -> tuple:
        """Extract team names, scores, and determine the winner."""
        teams, scores, winners = [], [], []

        for team in match.get("matchTeams", []):
            team_code = team.get("code", "")
            team_name = team.get("name", "")
            teams.append(f"{team_code} ({team_name})")

            result = team.get("result", {})
            if result:
                scores.append(result.get("gameWins", 0))
                winners.append(result.get("outcome", "") == "win")

        teams_str = " vs ".join(teams) if teams else "TBD"
        score_str = f"{scores[0]} - {scores[1]}" if len(scores) >= 2 else "0 - 0"
        winner = teams[winners.index(True)] if any(winners) else ""

        return teams_str, score_str, winner

    @staticmethod
    def extract_game_info(match: dict) -> tuple:
        """Extract the number of completed and total games."""
        games = match.get("games", [])

        return (
            sum(1 for game in games if game.get("state") == "completed"),
            len(games),
            [game.get("id") for game in games if game.get("state") != "unneeded"],
        )

    def parse_matches_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse JSON-Data and convert to Pandas DataFrame

        Args:
            data: JSON data from the LOL Esports API

        Returns:
            DataFrame containing processed match data
        """
        all_matches = []
        for event in data.get("data", {}).get("esports", {}).get("events", []):
            if event.get("__typename") == "EventMatch" and "match" in event:
                event_info = self.extract_event_info(event)
                teams_str, score_str, winner = self.extract_team_info(event["match"])
                games_completed, total_games, game_ids = self.extract_game_info(
                    event["match"]
                )

                all_matches.append(
                    {
                        **event_info,
                        "teams": teams_str,
                        "score": score_str,
                        "winner": winner,
                        "games_completed": games_completed,
                        "total_games": total_games,
                        "game_ids": game_ids,
                    }
                )

        df = pd.DataFrame(all_matches)
        if not df.empty:
            df["start_time"] = pd.to_datetime(df["start_time"]) + timedelta(hours=1)
            df["start_date"] = df["start_time"].dt.strftime("%d.%m.%Y")
            df["start_time_display"] = df["start_time"].dt.strftime("%H:%M")
            return df.sort_values(by="start_time")
        return df

    def get_matches(self, date_start: str, date_end: str) -> pd.DataFrame:
        """
        Fetch match data from the LOL Esports API

        Args:
            date_start: Start date in ISO format (YYYY-MM-DDThh:mm:ss.sssZ)
            date_end: End date in ISO format (YYYY-MM-DDThh:mm:ss.sssZ)

        Returns:
            DataFrame containing processed match data
        """
        data = self.get_matches_data(date_start, date_end)
        return self.parse_matches_data(data)


# --- Streamlit App ---
# Set page to wide mode for full-screen width
st.set_page_config(
    page_title="LOL Esports Schedule",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .match-card {
        background-color: #333333;
        color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid #ff4b4b;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .match-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .match-card.in-progress {
        border-left: 4px solid #00cc66;
    }
    .match-card.completed {
        border-left: 4px solid #1e88e5;
    }
    .match-title {
        font-weight: bold;
        color: #ffffff;
    }
    .match-time {
        color: #cccccc;
        font-size: 0.9em;
    }
    .match-score {
        font-weight: bold;
        font-size: 1.2em;
        color: #ffffff;
    }
    .match-format {
        color: #cccccc;
        font-size: 0.8em;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        border: none;
        padding: 10px;
        background-color: #f0f2f6;
        color: black;
        text-align: left;
    }
    .prev-next-btn {
        background-color: #1e88e5 !important;
        color: white !important;
        text-align: center !important;
    }
    .day-header {
        background-color: #1e88e5;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 10px;
    }
    .sidebar .stButton>button {
        margin-bottom: 5px;
    }
    .back-button {
        margin-bottom: 20px;
    }
    .prediction-button button {
        background-color: #333333 !important;
        color: white !important;
        text-align: center !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state for week navigation and filters
if "week_offset" not in st.session_state:
    st.session_state.week_offset = 0
if "selected_leagues" not in st.session_state:
    st.session_state.selected_leagues = []


# Function to get current week's Monday and Sunday
def get_week_dates(offset=0):
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


# Function to update week offset and refresh data
def change_week(offset):
    st.session_state.week_offset += offset
    st.rerun()


# Get current week's dates
start_date, end_date = get_week_dates(st.session_state.week_offset)

# Fetch matches data
matches = Matches().get_matches(start_date.isoformat(), end_date.isoformat())

# Get query parameters
query_params = st.query_params.to_dict()
game_ids = st.query_params.get_all("game_ids")

match_id = query_params.get("match_id", None)

# Check if we're viewing a specific match detail
if "match_id" in query_params:
    start_time = query_params.get("start_time", None)
    start_time = datetime.fromisoformat(start_time)

    response = requests.post(
        url="http://127.0.0.1:8000/predict",
        json={
            "game_ids": game_ids,
            "startingTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        },
    )

    predictions = (
        response.json()
        if response.status_code == 200
        else f"{response.status_code} status code error"
    )

    # We're on the match details page
    st.title("Match Prediction")

    # Add a back button
    if st.button("← Back to Schedule", key="back_button", help="Return to schedule"):
        # Remove match_id from query parameters
        st.query_params.clear()
        st.rerun()

    # Find the match by ID
    if not matches.empty:
        match = matches[matches["match_id"] == match_id]

        if not match.empty:
            match = match.iloc[0]

            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**League:** {match['league_name']}")
                st.markdown(f"**Tournament:** {match['tournament_name']}")
                st.markdown(
                    f"**Date & Time:** {match['start_date']} at {match['start_time_display']}"
                )
                st.markdown(f"**Format:** Best of {match['best_of']}")
                st.markdown(f"**Status:** {match['state']}")

            with col2:
                st.markdown(f"### {match['teams']}")
                st.markdown(f"**Current Score:** {match['score']}")

                # Show completed games vs total games
                progress = (
                    match["games_completed"] / match["total_games"]
                    if match["total_games"] > 0
                    else 0
                )
                st.progress(progress)
                st.text(
                    f"Games Played: {match['games_completed']} / {match['total_games']}"
                )

                if predictions:
                    for idx in range(len(predictions["predictions"])):
                        preds = pd.DataFrame(
                            {
                                "blue_preds": [
                                    predictions["predictions"][idx][i]
                                    for i in np.arange(0, 7, 2)
                                ],
                                "red_preds": [
                                    predictions["predictions"][idx][i]
                                    for i in np.arange(1, 8, 2)
                                ],
                            },
                            index=np.arange(10, 26, 5),
                        )

                        st.bar_chart(preds, stack=False)

                elif match["winner"]:
                    st.success(f"Winner: {match['winner']}")
        else:
            st.error("Match not found.")
    else:
        st.error("No matches data available.")

else:
    # Sidebar for filters and navigation
    with st.sidebar:
        st.title("🎮 LOL Esports Schedule")

        st.markdown(
            f"### Week: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "⬅ Previous", key="prev_week_sidebar", help="View previous week"
            ):
                change_week(-1)
        with col2:
            if st.button("Next ➡", key="next_week_sidebar", help="View next week"):
                change_week(1)

        st.divider()

        # Filter options
        if not matches.empty:
            available_leagues = sorted(matches["league_name"].unique())
            st.subheader("Filters")
            selected_leagues = st.multiselect(
                "Leagues",
                options=available_leagues,
                default=st.session_state.selected_leagues,
            )
            st.session_state.selected_leagues = selected_leagues

            # Apply filters
            if selected_leagues:
                matches = matches[matches["league_name"].isin(selected_leagues)]

            # Summary statistics
            st.divider()
            st.subheader("Summary")
            total_matches = len(matches)
            completed_matches = len(matches[matches["state"] == "completed"])
            in_progress_matches = len(matches[matches["state"] == "inProgress"])
            upcoming_matches = len(matches[matches["state"] == "unstarted"])

            st.markdown(f"**Total Matches:** {total_matches}")
            st.markdown(f"**Completed:** {completed_matches}")
            st.markdown(f"**In Progress:** {in_progress_matches}")
            st.markdown(f"**Upcoming:** {upcoming_matches}")
        else:
            st.info("No matches available for this week.")

    # Main content area
    st.title("League of Legends Esports Schedule")

    # Display matches in a full-width row format (Monday to Sunday)
    if not matches.empty:
        # Day View
        week_days = [start_date + timedelta(days=i) for i in range(7)]
        cols = st.columns(len(week_days))

        for col, day in zip(cols, week_days):
            with col:
                st.markdown(
                    f"<div class='day-header'>{day.strftime('%A, %b %d')}</div>",
                    unsafe_allow_html=True,
                )
                day_matches = matches[matches["start_time"].dt.date == day.date()]
                if not day_matches.empty:
                    for idx, match in day_matches.iterrows():
                        match_id = match["match_id"]
                        start_time = match["start_time"]
                        game_ids = match["game_ids"]

                        # Determine card style based on match state
                        state_class = ""
                        if match["state"] == "inProgress":
                            state_class = "in-progress"
                        elif match["state"] == "completed":
                            state_class = "completed"

                        with st.container():
                            # Create clickable card that redirects to match details page
                            st.markdown(
                                f"""
                            <div class='match-card {state_class}'
                                style='cursor: pointer; padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin: 10px 0;'
                                onclick="window.location.href='?match_id={match_id}&start_time={start_time}">
                                <div class='match-time'>{match["start_time_display"]} - {match["league_name"]}</div>
                                <div class='match-title'>{match["teams"]}</div>
                                <div class='match-score'>{match["score"]}</div>
                                <div class='match-format'>Best of {match["best_of"]}</div>
                            """,
                                unsafe_allow_html=True,
                            )
                            # Update query parameters on button click
                            if st.button("View Match Prediction", key=match_id):
                                st.query_params.from_dict(
                                    {
                                        "match_id": match_id,
                                        "start_time": start_time,
                                        "game_ids": game_ids,
                                    }
                                )
                                st.rerun()

                            st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("No matches")
    else:
        st.info("No matches found for the selected week and filters.")

# Footer
st.markdown("---")
st.markdown("Data sourced from LOL Esports API. Refreshed on page load.")
