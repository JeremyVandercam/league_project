import pandas as pd
from datetime import datetime

from league.ml_logic.params import DTYPES_DICT
from league.ml_logic.riot_api import Match, Team


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw data by
        - Transforming side (Blue, Red) to 1 or 0
        - Select only team rows and exclude players
        - Remove irrelevant columns
    """
    df["side"] = df["side"].map({"Blue": 1, "Red": 0})

    df = df.loc[df["position"] == "team", DTYPES_DICT.keys()]

    return df


def set_null_values(row: pd.Series, minute: str) -> pd.Series:
    """Set null values in columns matching given minute marks"""
    row_dict = dict(row)

    row_dict.update(
        {
            f"goldat{minute}": None,
            f"csat{minute}": None,
            f"opp_goldat{minute}": None,
            f"opp_csat{minute}": None,
            f"golddiffat{minute}": None,
            f"csdiffat{minute}": None,
            f"killsat{minute}": None,
            f"assistsat{minute}": None,
            f"deathsat{minute}": None,
            f"opp_killsat{minute}": None,
            f"opp_assistsat{minute}": None,
            f"opp_deathsat{minute}": None,
        }
    )

    updated_row = pd.Series(row_dict)

    return updated_row


def expand_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand rows by adding rows for specific minute marks.
    """
    expanded_rows = []

    df["minutes"] = ""

    for _, row in df.iterrows():
        row_20 = set_null_values(row, "25")
        row_20.update({"minutes": 20})

        row_15 = set_null_values(row_20, "20")
        row_15.update({"minutes": 15})

        row_10 = set_null_values(row_15, "15")
        row_10.update({"minutes": 10})

        row.update({"minutes": 25})

        expanded_rows.append(row_10)
        expanded_rows.append(row_15)
        expanded_rows.append(row_20)
        expanded_rows.append(row)

    expanded_df = pd.DataFrame(expanded_rows).reset_index(drop=True)

    return expanded_df


def get_api_data(match_id: str, startingTime: str) -> tuple[Match, Match]:
    match = Match(match_id=match_id)
    match.get_match_timeline(timestamp=startingTime)

    blue = Team(side=1)
    red = Team(side=0)

    start_timestamp = datetime.strptime(startingTime, "%Y-%m-%dT%H:%M:%S.%fZ")

    for window in match.timeline:
        timestamp = window["rfc460Timestamp"]

        try:
            frame_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            frame_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

        minutes = round((frame_timestamp - start_timestamp).seconds / 60)

        blue_team = window.get("blueTeam", {})
        red_team = window.get("redTeam", {})

        if (
            blue_team.get("totalKills") or red_team.get("totalKills")
        ) and blue.firstblood not in [0, 1]:
            blue.add_firstblood(blue_team.get("totalKills"), red_team.get("totalKills"))
            red.add_firstblood(red_team.get("totalKills"), blue_team.get("totalKills"))

        if (
            blue_team.get("dragons") or red_team.get("dragons")
        ) and blue.firstdragon not in [0, 1]:
            blue.add_firstdragon(
                len(blue_team.get("dragons")), len(red_team.get("dragons"))
            )
            red.add_firstdragon(
                len(red_team.get("dragons")), len(blue_team.get("dragons"))
            )

        if (
            blue_team.get("barons") or red_team.get("barons")
        ) and blue.firstbaron not in [0, 1]:
            blue.add_firstbaron(blue_team.get("barons"), red_team.get("barons"))
            red.add_firstbaron(red_team.get("barons"), blue_team.get("barons"))

        if (
            blue_team.get("towers") or red_team.get("towers")
        ) and blue.firsttower not in [0, 1]:
            blue.add_firsttower(blue_team.get("towers"), red_team.get("towers"))
            red.add_firsttower(red_team.get("towers"), blue_team.get("towers"))

        if (
            blue_team.get("towers") == 3 or red_team.get("towers") == 3
        ) and blue.firsttothreetowers not in [0, 1]:
            blue.add_firsttothreetowers(blue_team.get("towers"), red_team.get("towers"))
            red.add_firsttothreetowers(red_team.get("towers"), blue_team.get("towers"))

        blue.add_gold(blue_team.get("totalGold"), minutes)
        red.add_gold(red_team.get("totalGold"), minutes)

        blue.add_kills(blue_team.get("totalKills"), minutes)
        red.add_kills(red_team.get("totalKills"), minutes)

        blue.add_cs(
            sum(
                [participant["creepScore"] for participant in blue_team["participants"]]
            ),
            minutes,
        )
        red.add_cs(
            sum(
                [participant["creepScore"] for participant in red_team["participants"]]
            ),
            minutes,
        )

        blue.add_assists(
            sum([participant["assists"] for participant in blue_team["participants"]]),
            minutes,
        )
        red.add_assists(
            sum([participant["assists"] for participant in red_team["participants"]]),
            minutes,
        )

        blue.add_deaths(
            sum([participant["deaths"] for participant in blue_team["participants"]]),
            minutes,
        )
        red.add_deaths(
            sum([participant["deaths"] for participant in red_team["participants"]]),
            minutes,
        )

    return blue, red


def get_df_from_api_data(match_id: str, startingTime: str) -> pd.DataFrame:
    blue, red = get_api_data(match_id=match_id, startingTime=startingTime)

    df = pd.DataFrame(
        {
            "side": [blue.side, red.side],
            "firstblood": [blue.firstblood, red.firstblood],
            "firstdragon": [blue.firstdragon, red.firstdragon],
            "firstbaron": [blue.firstbaron, red.firstbaron],
            "firsttower": [blue.firsttower, red.firsttower],
            "firsttothreetowers": [blue.firsttothreetowers, red.firsttothreetowers],
            "goldat10": [blue.goldat10, red.goldat10],
            "csat10": [blue.csat10, red.csat10],
            "opp_goldat10": [red.goldat10, blue.goldat10],
            "opp_csat10": [red.csat10, blue.csat10],
            "golddiffat10": [
                blue.goldat10 - red.goldat10,
                red.goldat10 - blue.goldat10,
            ],
            "csdiffat10": [blue.csat10 - red.csat10, red.csat10 - blue.csat10],
            "killsat10": [blue.killsat10, red.killsat10],
            "assistsat10": [blue.assistsat10, red.assistsat10],
            "deathsat10": [blue.deathsat10, red.deathsat10],
            "opp_killsat10": [red.killsat10, blue.killsat10],
            "opp_assistsat10": [red.assistsat10, blue.assistsat10],
            "opp_deathsat10": [red.deathsat10, blue.deathsat10],
            "goldat15": [blue.goldat15, red.goldat15],
            "csat15": [blue.csat15, red.csat15],
            "opp_goldat15": [red.goldat15, blue.goldat15],
            "opp_csat15": [red.csat15, blue.csat15],
            "golddiffat15": [
                blue.goldat15 - red.goldat15,
                red.goldat15 - blue.goldat15,
            ],
            "csdiffat15": [blue.csat15 - red.csat15, red.csat15 - blue.csat15],
            "killsat15": [blue.killsat15, red.killsat15],
            "assistsat15": [blue.assistsat15, red.assistsat15],
            "deathsat15": [blue.deathsat15, red.deathsat15],
            "opp_killsat15": [red.killsat15, blue.killsat15],
            "opp_assistsat15": [red.assistsat15, blue.assistsat15],
            "opp_deathsat15": [red.deathsat15, blue.deathsat15],
            "goldat20": [blue.goldat20, red.goldat20],
            "csat20": [blue.csat20, red.csat20],
            "opp_goldat20": [red.goldat20, blue.goldat20],
            "opp_csat20": [red.csat20, blue.csat20],
            "golddiffat20": [
                blue.goldat20 - red.goldat20,
                red.goldat20 - blue.goldat20,
            ],
            "csdiffat20": [blue.csat20 - red.csat20, red.csat20 - blue.csat20],
            "killsat20": [blue.killsat20, red.killsat20],
            "assistsat20": [blue.assistsat20, red.assistsat20],
            "deathsat20": [blue.deathsat20, red.deathsat20],
            "opp_killsat20": [red.killsat20, blue.killsat20],
            "opp_assistsat20": [red.assistsat20, blue.assistsat20],
            "opp_deathsat20": [red.deathsat20, blue.deathsat20],
            "goldat25": [blue.goldat25, red.goldat25],
            "csat25": [blue.csat25, red.csat25],
            "opp_goldat25": [red.goldat25, blue.goldat25],
            "opp_csat25": [red.csat25, blue.csat25],
            "golddiffat25": [
                blue.goldat25 - red.goldat25,
                red.goldat25 - blue.goldat25,
            ],
            "csdiffat25": [blue.csat25 - red.csat25, red.csat25 - blue.csat25],
            "killsat25": [blue.killsat25, red.killsat25],
            "assistsat25": [blue.assistsat25, red.assistsat25],
            "deathsat25": [blue.deathsat25, red.deathsat25],
            "opp_killsat25": [red.killsat25, blue.killsat25],
            "opp_assistsat25": [red.assistsat25, blue.assistsat25],
            "opp_deathsat25": [red.deathsat25, blue.deathsat25],
        }
    )
    return df
