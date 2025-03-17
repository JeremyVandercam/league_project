import pandas as pd
from datetime import datetime

from league.ml_logic.riot_api import Match, Team


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw data by
        - Transforming side (Blue, Red) to boolean
        - Select only team rows
        - Remove irrelevant columns
    """
    # Changing side column to boolean
    df["side"] = df["side"].map({"Blue": 1, "Red": 0})

    # Select only the teams rows and exclude players
    df = df.loc[df["position"] == "team"]

    # Remove irrelevant data columns
    df = (
        df.select_dtypes(include="number")
        .reset_index(drop=True)
        .drop(
            columns=[
                "year",
                "playoffs",
                "game",
                "patch",
                "participantid",
                "gamelength",
                "kills",
                "deaths",
                "assists",
                "teamkills",
                "teamdeaths",
                "doublekills",
                "triplekills",
                "quadrakills",
                "pentakills",
                "firstbloodkill",
                "firstbloodassist",
                "firstbloodvictim",
                "team kpm",
                "ckpm",
                "dragons",
                "opp_dragons",
                "elementaldrakes",
                "opp_elementaldrakes",
                "infernals",
                "mountains",
                "clouds",
                "oceans",
                "chemtechs",
                "hextechs",
                "dragons_type_unknown",
                "elders",
                "opp_elders",
                "heralds",
                "opp_heralds",
                "void_grubs",
                "opp_void_grubs",
                "barons",
                "opp_barons",
                "towers",
                "opp_towers",
                "inhibitors",
                "opp_inhibitors",
                "damagetochampions",
                "dpm",
                "damageshare",
                "damagetakenperminute",
                "damagemitigatedperminute",
                "wardsplaced",
                "wpm",
                "wardskilled",
                "wcpm",
                "controlwardsbought",
                "visionscore",
                "vspm",
                "totalgold",
                "earnedgold",
                "earned gpm",
                "earnedgoldshare",
                "goldspent",
                "gspd",
                "gpr",
                "total cs",
                "minionkills",
                "monsterkills",
                "monsterkillsownjungle",
                "monsterkillsenemyjungle",
                "cspm",
            ]
        )
    )

    return df


def expand_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand rows
    """

    def set_null_values(row: pd.Series, minute: str) -> pd.Series:
        # Set null values in columns matching given minute marks
        row_dict = dict(row)

        row_dict.update(
            {
                f"goldat{minute}": None,
                f"xpat{minute}": None,
                f"csat{minute}": None,
                f"opp_goldat{minute}": None,
                f"opp_xpat{minute}": None,
                f"opp_csat{minute}": None,
                f"golddiffat{minute}": None,
                f"xpdiffat{minute}": None,
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

    expanded_rows = []

    df["minutes"] = ""

    for index, row in df.iterrows():
        # Create rows with null values for in game timestamp
        row_20 = set_null_values(row, "25")
        row_20.update({"minutes": 20.0})
        row_15 = set_null_values(row_20, "20")
        row_15.update({"minutes": 15.0})
        row_10 = set_null_values(row_15, "15")
        row_10.update({"minutes": 10.0})
        row.update({"minutes": 25.0})

        # Append created rows to original
        expanded_rows.append(row_10)
        expanded_rows.append(row_15)
        expanded_rows.append(row_20)
        expanded_rows.append(row)

    expanded_df = pd.DataFrame(expanded_rows).reset_index(drop=True)

    return expanded_df


def get_api_data(match_id: str, startingTime: str) -> tuple[Match, Match]:
    match = Match(match_id=match_id)
    match.get_match_timeline(timestamp=startingTime)

    blue = Team(side=True)
    red = Team(side=False)

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

        blue.add_firsts(
            firstblood=(
                1 if blue_team["totalKills"] >= 1 and red_team["totalKills"] == 0 else 0
            ),
            firstdragon=(
                1
                if len(blue_team["dragons"]) != 0 and len(red_team["dragons"]) == 0
                else 0
            ),
            #'firstherald'
            firstbaron=1 if blue_team["barons"] >= 1 and red_team["barons"] == 0 else 0,
            firsttower=1 if blue_team["towers"] >= 1 and red_team["towers"] == 0 else 0,
            #'firstmidtower'
            firsttothreetowers=(
                1 if blue_team["towers"] >= 3 and red_team["towers"] < 3 else 0
            ),
        )
        blue.add_gold(gold=blue_team.get("totalGold"), minutes=minutes)
        blue.add_kills(kills=blue_team.get("totalKills"), minutes=minutes)
        blue.add_cs(
            cs=sum(
                [participant["creepScore"] for participant in blue_team["participants"]]
            ),
            minutes=minutes,
        )
        blue.add_assists(
            assists=sum(
                [participant["assists"] for participant in blue_team["participants"]]
            ),
            minutes=minutes,
        )
        blue.add_deaths(
            deaths=sum(
                [participant["deaths"] for participant in blue_team["participants"]]
            ),
            minutes=minutes,
        )

        red.add_firsts(
            firstblood=(
                1 if red_team["totalKills"] >= 1 and blue_team["totalKills"] == 0 else 0
            ),
            firstdragon=(
                1
                if len(red_team["dragons"]) != 0 and len(blue_team["dragons"]) == 0
                else 0
            ),
            #'firstherald'
            firstbaron=1 if red_team["barons"] >= 1 and blue_team["barons"] == 0 else 0,
            firsttower=1 if red_team["towers"] >= 1 and blue_team["towers"] == 0 else 0,
            #'firstmidtower'
            firsttothreetowers=(
                1 if red_team["towers"] >= 3 and blue_team["towers"] < 3 else 0
            ),
        )
        red.add_gold(gold=red_team.get("totalGold"), minutes=minutes)
        red.add_kills(kills=red_team.get("totalKills"), minutes=minutes)
        red.add_cs(
            cs=sum(
                [participant["creepScore"] for participant in red_team["participants"]]
            ),
            minutes=minutes,
        )
        red.add_assists(
            assists=sum(
                [participant["assists"] for participant in red_team["participants"]]
            ),
            minutes=minutes,
        )
        red.add_deaths(
            deaths=sum(
                [participant["deaths"] for participant in red_team["participants"]]
            ),
            minutes=minutes,
        )

    return blue, red


def get_df_from_api_data(match_id: str, startingTime: str) -> pd.DataFrame:
    blue, red = get_api_data(match_id=match_id, startingTime=startingTime)
    df = pd.DataFrame(
        {
            "side": [blue.side, red.side],
            "firstblood": [blue.firstblood, red.firstblood],
            "firstdragon": [blue.firstdragon, red.firstdragon],
            # "firstherald": [blue.side, red.side],
            "firstbaron": [blue.firstbaron, red.firstbaron],
            "firsttower": [blue.firsttower, red.firsttower],
            # "firstmidtower": [blue.side, red.side],
            "firsttothreetowers": [blue.firsttothreetowers, red.firsttothreetowers],
            # "turretplates": [blue.side, red.side],
            # "opp_turretplates": [blue.side, red.side],
            "goldat10": [blue.goldat10, red.goldat10],
            # "xpat10": [blue.side, red.side],
            "csat10": [blue.csat10, red.csat10],
            "opp_goldat10": [red.goldat10, blue.goldat10],
            # "opp_xpat10": [blue.side, red.side],
            "opp_csat10": [red.csat10, blue.csat10],
            "golddiffat10": [
                blue.goldat10 - red.goldat10,
                red.goldat10 - blue.goldat10,
            ],
            # "xpdiffat10": [blue.side, red.side],
            "csdiffat10": [blue.csat10 - red.csat10, red.csat10 - blue.csat10],
            "killsat10": [blue.killsat10, red.killsat10],
            "assistsat10": [blue.assistsat10, red.assistsat10],
            "deathsat10": [blue.deathsat10, red.deathsat10],
            "opp_killsat10": [red.killsat10, blue.killsat10],
            "opp_assistsat10": [red.assistsat10, blue.assistsat10],
            "opp_deathsat10": [red.deathsat10, blue.deathsat10],
            "goldat15": [blue.goldat15, red.goldat15],
            # "xpat15": [blue.side, red.side],
            "csat15": [blue.csat15, red.csat15],
            "opp_goldat15": [red.goldat15, blue.goldat15],
            # "opp_xpat15": [blue.side, red.side],
            "opp_csat15": [red.csat15, blue.csat15],
            "golddiffat15": [
                blue.goldat15 - red.goldat15,
                red.goldat15 - blue.goldat15,
            ],
            # "xpdiffat15": [blue.side, red.side],
            "csdiffat15": [blue.csat15 - red.csat15, red.csat15 - blue.csat15],
            "killsat15": [blue.killsat15, red.killsat15],
            "assistsat15": [blue.assistsat15, red.assistsat15],
            "deathsat15": [blue.deathsat15, red.deathsat15],
            "opp_killsat15": [red.killsat15, blue.killsat15],
            "opp_assistsat15": [red.assistsat15, blue.assistsat15],
            "opp_deathsat15": [red.deathsat15, blue.deathsat15],
            "goldat20": [blue.goldat20, red.goldat20],
            # "xpat20": [blue.side, red.side],
            "csat20": [blue.csat20, red.csat20],
            "opp_goldat20": [red.goldat20, blue.goldat20],
            # "opp_xpat20": [blue.side, red.side],
            "opp_csat20": [red.csat20, blue.csat20],
            "golddiffat20": [
                blue.goldat20 - red.goldat20,
                red.goldat20 - blue.goldat20,
            ],
            # "xpdiffat20": [blue.side, red.side],
            "csdiffat20": [blue.csat20 - red.csat20, red.csat20 - blue.csat20],
            "killsat20": [blue.killsat20, red.killsat20],
            "assistsat20": [blue.assistsat20, red.assistsat20],
            "deathsat20": [blue.deathsat20, red.deathsat20],
            "opp_killsat20": [red.killsat20, blue.killsat20],
            "opp_assistsat20": [red.assistsat20, blue.assistsat20],
            "opp_deathsat20": [red.deathsat20, blue.deathsat20],
            "goldat25": [blue.goldat25, red.goldat25],
            # "xpat25": [blue.side, red.side],
            "csat25": [blue.csat25, red.csat25],
            "opp_goldat25": [red.goldat25, blue.goldat25],
            # "opp_xpat25": [blue.side, red.side],
            "opp_csat25": [red.csat25, blue.csat25],
            "golddiffat25": [
                blue.goldat25 - red.goldat25,
                red.goldat25 - blue.goldat25,
            ],
            # "xpdiffat25": [blue.side, red.side],
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
