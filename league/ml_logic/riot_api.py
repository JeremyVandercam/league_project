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

        self.window = response.json()

    def get_match_timeline(self, timestamp: str):
        start_datetime_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

        for minute in range(26):
            datetime_timestamp = start_datetime_timestamp + timedelta(minutes=minute)

            self.get_match_window(
                timestamp=datetime_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            )

            [self.timeline.append(frame) for frame in self.window.get("frames")]


class Team:
    def __init__(self, side):
        self.side: bool = side
        self.firstblood: bool = None
        self.firstdragon: bool = None
        self.firstbaron: bool = None
        self.firsttower: bool = None
        self.firsttothreetowers: bool = None
        self.goldat10: int = None
        self.csat10: int = None
        self.killsat10: int = None
        self.assistsat10: int = None
        self.deathsat10: int = None
        self.goldat15: int = None
        self.csat15: int = None
        self.killsat15: int = None
        self.assistsat15: int = None
        self.deathsat15: int = None
        self.goldat20: int = None
        self.csat20: int = None
        self.killsat20: int = None
        self.assistsat20: int = None
        self.deathsat20: int = None
        self.goldat25: int = None
        self.csat25: int = None
        self.killsat25: int = None
        self.assistsat25: int = None
        self.deathsat25: int = None

    def add_firsts(
        self,
        firstblood: bool,
        firstdragon: bool,
        firstbaron: bool,
        firsttower: bool,
        firsttothreetowers: bool,
    ):
        if firstblood:
            self.firstblood = firstblood
        if firstdragon:
            self.firstdragon = firstdragon
        if firstbaron:
            self.firstbaron = firstbaron
        if firsttower:
            self.firsttower = firsttower
        if firsttothreetowers:
            self.firsttothreetowers = firsttothreetowers

    def add_gold(self, gold: int, minutes: int):
        if minutes == 10:
            if self.goldat10 is None:
                self.goldat10 = gold
        if minutes == 15:
            if self.goldat15 is None:
                self.goldat15 = gold
        if minutes == 20:
            if self.goldat20 is None:
                self.goldat20 = gold
        if minutes == 25:
            if self.goldat25 is None:
                self.goldat25 = gold

    def add_cs(self, cs: int, minutes: int):
        if minutes == 10:
            if self.csat10 is None:
                self.csat10 = cs
        if minutes == 15:
            if self.csat15 is None:
                self.csat15 = cs
        if minutes == 20:
            if self.csat20 is None:
                self.csat20 = cs
        if minutes == 25:
            if self.csat25 is None:
                self.csat25 = cs

    def add_kills(self, kills: int, minutes: int):
        if minutes == 10:
            if self.killsat10 is None:
                self.killsat10 = kills
        if minutes == 15:
            if self.killsat15 is None:
                self.killsat15 = kills
        if minutes == 20:
            if self.killsat20 is None:
                self.killsat20 = kills
        if minutes == 25:
            if self.killsat25 is None:
                self.killsat25 = kills

    def add_assists(self, assists: int, minutes: int):
        if minutes == 10:
            if self.assistsat10 is None:
                self.assistsat10 = assists
        if minutes == 15:
            if self.assistsat15 is None:
                self.assistsat15 = assists
        if minutes == 20:
            if self.assistsat20 is None:
                self.assistsat20 = assists
        if minutes == 25:
            if self.assistsat25 is None:
                self.assistsat25 = assists

    def add_deaths(self, deaths: int, minutes: int):
        if minutes == 10:
            if self.deathsat10 is None:
                self.deathsat10 = deaths
        if minutes == 15:
            if self.deathsat15 is None:
                self.deathsat15 = deaths
        if minutes == 20:
            if self.deathsat20 is None:
                self.deathsat20 = deaths
        if minutes == 25:
            if self.deathsat25 is None:
                self.deathsat25 = deaths
