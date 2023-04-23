from dataclasses import dataclass, field
from typing import List

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
        pass

    def _get_matches_from_df(self, df: DataFrame) -> None:
        pass
