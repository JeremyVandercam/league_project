import pandas as pd


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
        row_20.update({"minutes": 20})
        row_15 = set_null_values(row_20, "20")
        row_15.update({"minutes": 15})
        row_10 = set_null_values(row_15, "15")
        row_10.update({"minutes": "10"})
        row.update({"minutes": 25})

        # Append created rows to original
        expanded_rows.append(row_10)
        expanded_rows.append(row_15)
        expanded_rows.append(row_20)
        expanded_rows.append(row)

    expanded_df = pd.DataFrame(expanded_rows).reset_index(drop=True)

    return expanded_df
