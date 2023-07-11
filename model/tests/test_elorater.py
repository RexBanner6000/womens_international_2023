from datetime import datetime

from model.entities import Match, MatchType, Team
from model.ratings import ELORater

team_a = Team(name="A", initial_rating=630)
team_b = Team(name="B", initial_rating=500)

home_win = Match(
    home_team=team_a,
    away_team=team_b,
    home_score=3,
    away_score=1,
    type=MatchType.FRIENDLY,
    date=datetime.now(),
)

draw = Match(
    home_team=team_a,
    away_team=team_b,
    home_score=2,
    away_score=2,
    type=MatchType.FRIENDLY,
    date=datetime.now(),
)

away_win = Match(
    home_team=team_a,
    away_team=team_b,
    home_score=1,
    away_score=3,
    type=MatchType.FRIENDLY,
    date=datetime.now(),
)


def test_calculate_goal_index():
    rater = ELORater()
    assert rater.calculate_goal_index(0) == 1
    assert rater.calculate_goal_index(1) == 1
    assert rater.calculate_goal_index(2) == 1.5
    assert rater.calculate_goal_index(3) == 14 / 8
    assert rater.calculate_goal_index(10) == 21 / 8


def test_calculate_expected_results():
    rater = ELORater()
    assert rater.calculate_expected_result(0) == 0.5
    assert rater.calculate_expected_result(120) == 0.6661394245831221
    assert rater.calculate_expected_result(800) == 0.9900990099009901


def test_calculate_points_change_home_win():
    rater = ELORater()
    points_change = rater.calculate_points_change(home_win)
    assert points_change == 9.6354924061573


def test_calculate_points_change_draw():
    rater = ELORater()
    points_change = rater.calculate_points_change(draw)
    assert points_change == -3.5763383958951334


def test_calculate_away_win():
    rater = ELORater()
    points_change = rater.calculate_points_change(away_win)
    assert points_change == -20.3645075938427
