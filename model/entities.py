from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict


@dataclass
class MatchType(Enum):
    UNKNOWN = 0
    QUALIFIER = 1
    GROUP = 2
    KNOCKOUT = 3
    FINAL = 4


@dataclass
class Team:
    name: str
    rating: Dict[datetime, int] = field(
        default_factory=lambda: {datetime.strptime("01/01/1900", "%d/%m/%Y"): 1500}
    )

    def update_rating(self):
        pass

    def get_rating(self):
        pass


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
    tournament: Tournament
    city: str
    country: str
    neutral: bool
    type: MatchType = MatchType.UNKNOWN

    def get_team_ratings(self):
        pass

    def update_team_ratings(self):
        pass
