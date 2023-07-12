from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from pandas import DataFrame
from tqdm import tqdm

from model.entities import Event, Match, MatchType, Result, Team, Tournament
from model.ratings import ELORater


@dataclass
class ResultsDataset:
    events: List[Event] = field(default_factory=list)
    matches: List[Match] = field(default_factory=list)
    tournaments: List[Tournament] = field(default_factory=list)
    teams: List[Team] = field(default_factory=list)
    matches_by_team: Dict[str, List[Match]] = field(
        default_factory=lambda: defaultdict(list)
    )

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
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        for index, row in df.iterrows():
            match = Match(
                home_team=self._create_team(row["home_team"]),
                away_team=self._create_team(row["away_team"]),
                date=row["date"],
                home_score=row["home_score"],
                away_score=row["away_score"],
                tournament=self._create_tournament(row["tournament"], row["date"].year),
                city=row["city"],
                country=row["country"],
                neutral=bool(row["neutral"]),
            )
            match.find_event_type(row["tournament"])
            self.matches.append(match)
            self.matches_by_team[match.home_team.name].append(match)
            self.matches_by_team[match.away_team.name].append(match)

    def calculate_ratings(self) -> None:
        rating_system = ELORater()
        for match in self.matches:
            rating_system.update_ratings(match)

    def calculate_rankings(self, date: datetime, n_years: int = 4) -> Dict[str, int]:
        current_ratings = {}
        for team in self.teams:
            try:
                if date - team.get_last_played_date(date) < timedelta(n_years * 365):
                    current_ratings[team.name] = team.get_rating(date)
                else:
                    current_ratings[team.name] = np.nan
            except TypeError:
                current_ratings[team.name] = np.nan
        return {
            key: rank
            for rank, key in enumerate(
                sorted(current_ratings, key=current_ratings.get, reverse=True), 1
            )
        }

    def get_most_recent_matches(
        self, team_name: str, date: datetime, n_days: int = 90
    ) -> Optional[List[Match]]:
        team_matches = []
        for match in self.matches_by_team[team_name]:
            if date - timedelta(days=n_days) < match.date < date:
                if team_name in [match.home_team.name, match.away_team.name]:
                    team_matches.append(match)
        return team_matches

    def get_last_n_games(self, team_name: str, date: datetime, n_games: int = 5):
        team_matches = []
        for match in self.matches_by_team[team_name]:
            if match.date < date:
                team_matches.append(match)
        if len(team_matches) < n_games:
            return team_matches
        else:
            return team_matches[-n_games:]

    @staticmethod
    def get_team_goals_from_matches(team_name: str, matches: List[Match]) -> (int, int):
        scored = 0
        conceded = 0
        for match in matches:
            if match.home_team.name is team_name:
                scored += match.home_score
                conceded += match.away_score
            elif match.away_team.name is team_name:
                scored += match.away_score
                conceded += match.home_score
        return scored, conceded

    def write_results_to_csv(self, output_path: Path) -> None:
        df = pd.DataFrame()
        for idx, match in enumerate(tqdm(self.matches)):
            match_dict = self._match_to_dict(match)
            df = pd.concat([df, pd.DataFrame(match_dict, index=[idx])])
        df.to_csv(output_path, index=False)

    def _match_to_dict(self, match: Match):
        if match.home_score > match.away_score:
            result = Result.HOME_WIN
        elif match.home_score < match.away_score:
            result = Result.AWAY_WIN
        else:
            result = Result.DRAW

        home_rating = match.home_team.get_rating(match.date - timedelta(days=1))
        away_rating = match.away_team.get_rating(match.date - timedelta(days=1))

        world_rankings = self.calculate_rankings(match.date)

        last_games_home = self.get_last_n_games(match.home_team.name, match.date)
        last_games_away = self.get_last_n_games(match.away_team.name, match.date)
        home_scored, home_conceded = self.get_team_goals_from_matches(
            match.home_team.name, last_games_home
        )
        away_scored, away_conceded = self.get_team_goals_from_matches(
            match.away_team.name, last_games_away
        )

        return {
            "date": match.date.strftime("%d/%m/%Y"),
            "home_team": match.home_team.name,
            "away_team": match.away_team.name,
            "home_rating": home_rating,
            "away_rating": away_rating,
            "match_type": str(match.type),
            "home_ranking": world_rankings[match.home_team.name],
            "away_ranking": world_rankings[match.away_team.name],
            "home_recent_scored": home_scored,
            "away_recent_scored": away_scored,
            "home_recent_conceded": home_conceded,
            "away_recent_conceded": away_conceded,
            "result": result.value,
        }

    def create_test_df(self, submission_df: pd.DataFrame) -> pd.DataFrame:
        test_df = pd.DataFrame()
        for index, row in submission_df.iterrows():
            fixture_dict = self._fixture_to_dict(
                row["team1"], row["team2"], datetime(2023, 7, 20), row["group"]
            )
            test_df = pd.concat([test_df, pd.DataFrame(fixture_dict, index=[index])])
        return test_df

    def _fixture_to_dict(
        self,
        home_team_name: str,
        away_team_name: str,
        date: datetime,
        match_type: MatchType = MatchType.WORLD_CUP,
    ) -> Dict:

        home_team = self.get_team_from_name(self.remap_team_name(home_team_name))
        away_team = self.get_team_from_name(self.remap_team_name(away_team_name))
        world_rankings = self.calculate_rankings(date)

        last_games_home = self.get_last_n_games(home_team.name, date)
        last_games_away = self.get_last_n_games(away_team.name, date)
        home_scored, home_conceded = self.get_team_goals_from_matches(
            home_team.name, last_games_home
        )
        away_scored, away_conceded = self.get_team_goals_from_matches(
            away_team.name, last_games_away
        )
        return {
            "home_team": home_team.name,
            "away_team": away_team.name,
            "home_rating": home_team.get_rating(date),
            "away_rating": away_team.get_rating(date),
            "match_type": str(match_type),
            "home_ranking": world_rankings[home_team.name],
            "away_ranking": world_rankings[away_team.name],
            "home_recent_scored": home_scored,
            "away_recent_scored": away_scored,
            "home_recent_conceded": home_conceded,
            "away_recent_conceded": away_conceded,
        }

    @staticmethod
    def remap_team_name(team_name: str) -> str:
        name_remaps = {
            "USA": "United States",
            "Korea Republic": "South Korea"
        }
        if name_remaps.get(team_name):
            return name_remaps[team_name]
        else:
            return team_name
