from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

import matplotlib.pyplot as plt

_DEFAULT_RATING = 1500
_RATINGS_START_DATE = datetime.strptime("01/01/1950", "%d/%m/%Y")


@dataclass
class MatchType(Enum):
    WORLD_CUP = 60
    OLYMPIC_GAMES = 40
    CONTINENTAL = 50
    QUALIFIERS = 40
    OTHER_TOURNAMENTS = 30
    FRIENDLY = 20


@dataclass
class Result(Enum):
    AWAY_WIN = 0
    HOME_WIN = 1
    DRAW = 2


@dataclass
class Team:
    name: str
    rating: Dict[datetime, int]

    def __init__(self, name: str, initial_rating: Optional[int] = None):
        self.name = name
        if initial_rating:
            self.rating = {_RATINGS_START_DATE: initial_rating}
        else:
            self.rating = {_RATINGS_START_DATE: _DEFAULT_RATING}

    def update_rating(self, date: datetime, rating: int) -> None:
        self.rating[date] = rating

    def get_rating(self, date: datetime) -> Optional[int]:
        if self.rating.get(date):
            return self.rating[date]
        else:
            previous_rating = _DEFAULT_RATING
            for key, rating in self.rating.items():
                if date < key:
                    break
                previous_rating = rating
            return previous_rating

    def show_rating_history(self) -> None:
        fig, ax = plt.subplots()
        plt.title(self.name)
        x = [x for x in self.rating.keys()]
        y = [y for y in self.rating.values()]
        plt.plot(x, y)
        plt.show()

    def get_last_played_date(self, date: datetime) -> Optional[datetime]:
        last_played = None
        for match_date in self.rating.keys():
            if match_date > date:
                return last_played
            last_played = match_date
        return last_played


@dataclass
class Event:
    name: str


@dataclass
class Tournament(Event):
    year: int


@dataclass
class Match:
    home_team: Team
    away_team: Team
    date: datetime
    home_score: int
    away_score: int
    tournament: Optional[Tournament] = None
    city: Optional[str] = None
    country: Optional[str] = None
    neutral: Optional[bool] = None
    type: MatchType = MatchType.OTHER_TOURNAMENTS

    def find_event_type(self, event_name: str) -> None:
        if "qualifiers" in event_name.lower() or "qualification" in event_name.lower():
            self.type = MatchType.QUALIFIERS
        elif "world cup" in event_name.lower():
            self.type = MatchType.WORLD_CUP
        elif "olympic" in event_name.lower():
            self.type = MatchType.OLYMPIC_GAMES
        elif "friend" in event_name.lower():
            self.type = MatchType.FRIENDLY
        elif (
            "concacaf" in event_name.lower()
            or "copa america" in event_name.lower()
            or "euro" in event_name.lower()
            or "african cup" in event_name.lower()
        ):
            self.type = MatchType.CONTINENTAL
        else:
            self.type = MatchType.OTHER_TOURNAMENTS
