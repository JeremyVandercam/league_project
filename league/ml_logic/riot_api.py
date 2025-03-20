import requests
from datetime import datetime, timedelta


class Match:
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.window: dict = {}
        self.timeline: list = []

    def get_match_window(self, timestamp: str):
        url = f"https://feed.lolesports.com/livestats/v1/window/{self.match_id}"

        params = {"startingTime": timestamp}

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

        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            self.window = response.json()

    def get_match_timeline(self, timestamp: str):
        start_datetime_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

        for minute in range(50):
            datetime_timestamp = start_datetime_timestamp + timedelta(minutes=minute)

            self.get_match_window(
                timestamp=datetime_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            )

            [self.timeline.append(frame) for frame in self.window.get("frames")]


class Team:
    def __init__(self, side):
        self.side: int = side
        self.firstblood: float = 0
        self.firstdragon: float = 0
        self.firstbaron: float = 0
        self.firsttower: float = 0
        self.firsttothreetowers: float = 0
        self.goldat10: float = 0
        self.csat10: float = 0
        self.killsat10: float = 0
        self.assistsat10: float = 0
        self.deathsat10: float = 0
        self.goldat15: float = 0
        self.csat15: float = 0
        self.killsat15: float = 0
        self.assistsat15: float = 0
        self.deathsat15: float = 0
        self.goldat20: float = 0
        self.csat20: float = 0
        self.killsat20: float = 0
        self.assistsat20: float = 0
        self.deathsat20: float = 0
        self.goldat25: float = 0
        self.csat25: float = 0
        self.killsat25: float = 0
        self.assistsat25: float = 0
        self.deathsat25: float = 0

    def add_firstblood(self, firstblood: float, opp_firstblood: float):
        self.firstblood = 1 if firstblood > 0 and opp_firstblood == 0 else 0

    def add_firstdragon(self, firstdragon: float, opp_firstdragon: float):
        self.firstdragon = 1 if firstdragon > 0 and opp_firstdragon == 0 else 0

    def add_firstbaron(self, firstbaron: float, opp_firstbaron: float):
        self.firstbaron = 1 if firstbaron > 0 and opp_firstbaron == 0 else 0

    def add_firsttower(self, firsttower: float, opp_firsttower: float):
        self.firsttower = 1 if firsttower > 0 and opp_firsttower == 0 else 0

    def add_firsttothreetowers(
        self, firsttothreetowers: float, opp_firsttothreetowers: float
    ):
        self.firsttothreetowers = (
            1 if firsttothreetowers > 2 and opp_firsttothreetowers < 3 else 0
        )

    def add_gold(self, gold: float, minutes: int):
        if minutes == 10 and self.goldat10 == 0:
            self.goldat10 = gold
        if minutes == 15 and self.goldat15 == 0:
            self.goldat15 = gold
        if minutes == 20 and self.goldat20 == 0:
            self.goldat20 = gold
        if minutes == 25 and self.goldat25 == 0:
            self.goldat25 = gold

    def add_cs(self, cs: float, minutes: int):
        if minutes == 10 and self.csat10 == 0:
            self.csat10 = cs
        if minutes == 15 and self.csat15 == 0:
            self.csat15 = cs
        if minutes == 20 and self.csat20 == 0:
            self.csat20 = cs
        if minutes == 25 and self.csat25 == 0:
            self.csat25 = cs

    def add_kills(self, kills: float, minutes: int):
        if minutes == 10 and self.killsat10 == 0:
            self.killsat10 = kills
        if minutes == 15 and self.killsat15 == 0:
            self.killsat15 = kills
        if minutes == 20 and self.killsat20 == 0:
            self.killsat20 = kills
        if minutes == 25 and self.killsat25 == 0:
            self.killsat25 = kills

    def add_assists(self, assists: float, minutes: int):
        if minutes == 10 and self.assistsat10 == 0:
            self.assistsat10 = assists
        if minutes == 15 and self.assistsat15 == 0:
            self.assistsat15 = assists
        if minutes == 20 and self.assistsat20 == 0:
            self.assistsat20 = assists
        if minutes == 25 and self.assistsat25 == 0:
            self.assistsat25 = assists

    def add_deaths(self, deaths: float, minutes: int):
        if minutes == 10 and self.deathsat10 == 0:
            self.deathsat10 = deaths
        if minutes == 15 and self.deathsat15 == 0:
            self.deathsat15 = deaths
        if minutes == 20 and self.deathsat20 == 0:
            self.deathsat20 = deaths
        if minutes == 25 and self.deathsat25 == 0:
            self.deathsat25 = deaths
