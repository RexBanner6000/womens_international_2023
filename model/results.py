from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from pandas import DataFrame

from model.entities import Event, Match, Team, Tournament


@dataclass
class ResultsDataset:
    events: List[Event] = field(default_factory=list)
    matches: List[Match] = field(default_factory=list)
    tournaments: List[Tournament] = field(default_factory=list)
    teams: List[Team] = field(default_factory=list)

    def populate_data_from_df(self, df: DataFrame) -> None:
        self._get_teams_from_df(df)
        self._get_events_from_df(df)
        self._get_tournaments_from_df(df)
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

    def _get_teams_from_df(self, df: DataFrame) -> None:
        for index, row in df.iterrows():
            self._add_team(row["home_team"])
            self._add_team(row["away_team"])

    def _add_team(self, team_name: str) -> None:
        team_names = [x.name for x in self.teams]
        if team_name not in team_names:
            self.teams.append(Team(name=team_name))

    def _get_events_from_df(self, df: DataFrame) -> None:
        for index, row in df.iterrows():
            self._add_event(row["tournament"])

    def _add_event(self, event_name: str) -> None:
        event_names = [x.name for x in self.events]
        if event_name not in event_names:
            self.events.append(Event(name=event_name))

    def _get_tournaments_from_df(self, df: DataFrame) -> None:
        for index, row in df.iterrows():
            year = datetime.strptime(row["date"], "%Y-%m-%d").year
            event_name = row["tournament"]
            self._add_event(event_name)
            self._add_tournament(event_name, year)

    def _add_tournament(self, event_name: str, year: int) -> None:
        event = self.get_event_from_name(event_name)
        for tournament in self.tournaments:
            if tournament.name == event.name and tournament.year == year:
                return None

        self.tournaments.append(Tournament(event_name, year))

    def _get_matches_from_df(self, df: DataFrame) -> None:
        for index, row in df.iterrows():
            date = datetime.strptime(row["date"], "%Y-%m-%d")
            self.matches.append(
                Match(
                    home_team=self.get_team_from_name(row["home_team"]),
                    away_team=self.get_team_from_name(row["away_team"]),
                    date=date,
                    home_score=row["home_score"],
                    away_score=row["away_score"],
                    tournament=self.get_tournament_from_year(
                        row["tournament"], date.year
                    ),
                    city=row["city"],
                    country=row["country"],
                    neutral=bool(row["neutral"]),
                )
            )
