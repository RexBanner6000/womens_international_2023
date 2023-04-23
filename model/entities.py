from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


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
class Match:
    home_team: Team
    away_team: Team
    date: datetime
    home_score: int
    away_score: int
    tournament: str
    city: str
    country: str
    neutral: str

    def get_team_ratings(self):
        pass

    def update_team_ratings(self):
        pass


@dataclass
class Tournament:
    name: str
    year: int
    matches: List[Match] = field(default_factory=list)


@dataclass
class Event:
    name: str
    tournaments: List[Tournament] = field(default_factory=list)
