from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import List, Optional

import pandas as pd
from pandas import DataFrame

from model.entities import Event, Match, Team, Tournament
from model.ratings import ELORater


@dataclass
class ResultsDataset:
    events: List[Event] = field(default_factory=list)
    matches: List[Match] = field(default_factory=list)
    tournaments: List[Tournament] = field(default_factory=list)
    teams: List[Team] = field(default_factory=list)

    def populate_data_from_df(self, df: DataFrame) -> None:
        self._get_events_from_df(df)
        self._get_matches_from_df(df)

    def get_event_from_name(self, event_name: str) -> Optional[Event]:
        for event in self.events:
            if event.name == event_name:
                return event
        return None

    def get_team_from_name(self, team_name: str) -> Optional[Team]:
        for team in self.teams:
            if team.name == team_name:
                return team
        return None

    def get_tournament_from_year(
        self, tournament_name: str, year: int
    ) -> Optional[Tournament]:
        for tournament in self.tournaments:
            if tournament.name == tournament_name and tournament.year == year:
                return tournament
        return None

    def _create_team(self, team_name: str) -> Team:
        team_names = [x.name for x in self.teams]
        if team_name not in team_names:
            team = Team(name=team_name)
            self.teams.append(team)
        else:
            team = self.get_team_from_name(team_name)
        return team

    def _get_events_from_df(self, df: DataFrame) -> None:
        for index, row in df.iterrows():
            self._add_event(row["tournament"])

    def _add_event(self, event_name: str) -> None:
        event_names = [x.name for x in self.events]
        if event_name not in event_names:
            self.events.append(Event(name=event_name))

    def _create_tournament(self, event_name: str, year: int) -> Tournament:
        event = self.get_event_from_name(event_name)
        for tournament in self.tournaments:
            if tournament.name == event.name and tournament.year == year:
                return tournament

        tournament = Tournament(event_name, year)
        self.tournaments.append(tournament)
        return tournament

    def _get_matches_from_df(self, df: DataFrame) -> None:
        # TODO: Get match type
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        for index, row in df.iterrows():
            self.matches.append(
                Match(
                    home_team=self._create_team(row["home_team"]),
                    away_team=self._create_team(row["away_team"]),
                    date=row["date"],
                    home_score=row["home_score"],
                    away_score=row["away_score"],
                    tournament=self._create_tournament(
                        row["tournament"], row["date"].year
                    ),
                    city=row["city"],
                    country=row["country"],
                    neutral=bool(row["neutral"]),
                )
            )

    def calculate_ratings(self) -> None:
        rating_system = ELORater()
        for match in self.matches:
            rating_system.update_ratings(match)

    def calculate_rankings(self) -> None:
        # TODO: Add ranking function
        pass

    def write_results_to_csv(self, output_path: Path) -> None:
        df = pd.DataFrame()
        for idx, match in enumerate(self.matches):
            match_dict = self._match_to_dict(match)
            df = pd.concat([df, pd.DataFrame(match_dict, index=[idx])])
        df.to_csv(output_path, index=False)

    @staticmethod
    def _match_to_dict(match: Match):
        if match.home_score > match.away_score:
            result = 1
        elif match.home_score < match.away_score:
            result = 0
        else:
            result = 0.5

        home_rating = match.home_team.get_rating(match.date - timedelta(days=1))
        away_rating = match.away_team.get_rating(match.date - timedelta(days=1))

        return {
            "home_team": match.home_team.name,
            "away_team": match.away_team.name,
            "result": result,
            "home_rating": home_rating,
            "away_rating": away_rating,
            "match_type": str(match.type)
        }
