from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

_DEFAULT_RATING = 1500


@dataclass
class MatchType(Enum):
    WORLD_CUP = 60
    OLYMPIC_GAMES = 60
    CONTINENTAL = 50
    QUALIFIERS = 40
    OTHER_TOURNAMENTS = 30
    FRIENDLY = 20


@dataclass
class Team:
    name: str
    rating: Dict[datetime, int]

    def __init__(self, name: str, initial_rating: Optional[int] = None):
        date = datetime.strptime("01/01/1900", "%d/%m/%Y")
        self.name = name
        if initial_rating:
            self.rating = {date: initial_rating}
        else:
            self.rating = {date: _DEFAULT_RATING}

    def update_rating(self):
        pass

    def get_rating(self, date: datetime) -> Optional[int]:
        if self.rating.get(date):
            return self.rating[date]
        else:
            for key, rating in self.rating.items():
                if date > key:
                    return rating
        return _DEFAULT_RATING


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

    def get_ratings(self) -> (int, int):
        home_rating = self.home_team.get_rating(self.date)
        away_rating = self.away_team.get_rating(self.date)
        return home_rating, away_rating

    def update_ratings(self):
        pass
