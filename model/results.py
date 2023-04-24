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
        for index, row in df.iterrows():
            date = datetime.strptime(row["date"], "%Y-%m-%d")
            self.matches.append(
                Match(
                    home_team=self._create_team(row["home_team"]),
                    away_team=self._create_team(row["away_team"]),
                    date=date,
                    home_score=row["home_score"],
                    away_score=row["away_score"],
                    tournament=self._create_tournament(
                        row["tournament"], date.year
                    ),
                    city=row["city"],
                    country=row["country"],
                    neutral=bool(row["neutral"]),
                )
            )
