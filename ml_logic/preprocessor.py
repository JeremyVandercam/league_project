import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Clean raw data by
        - Transforming side (Blue, Red) to boolean
        - Select only team rows
        - Remove irrelevant columns
    '''
    # Changing side column to boolean
    df['side'] = df['side'].map({'Blue': 1, 'Red': 0})
    # Select only the teams rows and exclude players
    df = df.loc[df['position'] == 'team']
    # Remove irrelevant data columns
    df = df.select_dtypes(include='number')\
    .reset_index()\
    .drop(columns=[
        'index',
        'year',
        'playoffs',
        'game',
        'patch',
        'participantid',
        'gamelength',
        'kills',
        'deaths',
        'assists',
        'teamkills',
        'teamdeaths',
        'doublekills',
        'triplekills',
        'quadrakills',
        'pentakills',
        'firstbloodkill',
        'firstbloodassist',
        'firstbloodvictim',
        'team kpm',
        'ckpm',
        'dragons',
        'opp_dragons',
        'elementaldrakes',
        'opp_elementaldrakes',
        'infernals',
        'mountains',
        'clouds',
        'oceans',
        'chemtechs',
        'hextechs',
        'dragons_type_unknown',
        'elders',
        'opp_elders',
        'heralds',
        'opp_heralds',
        'void_grubs',
        'opp_void_grubs',
        'barons',
        'opp_barons',
        'towers',
        'opp_towers',
        'inhibitors',
        'opp_inhibitors',
        'damagetochampions',
        'dpm',
        'damageshare',
        'damagetakenperminute',
        'damagemitigatedperminute',
        'wardsplaced',
        'wpm',
        'wardskilled',
        'wcpm',
        'controlwardsbought',
        'visionscore',
        'vspm',
        'totalgold',
        'earnedgold',
        'earned gpm',
        'earnedgoldshare',
        'goldspent',
        'gspd',
        'gpr',
        'total cs',
        'minionkills',
        'monsterkills',
        'monsterkillsownjungle',
        'monsterkillsenemyjungle',
        'cspm'
    ])

    return df
