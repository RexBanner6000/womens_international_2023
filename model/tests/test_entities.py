from datetime import datetime

from model.entities import _DEFAULT_RATING, Team

team_a = Team(name="TEAM A")
team_b = Team(name="TEAM B", initial_rating=600)


def test_team_get_rating_date():
    rating = team_a.get_rating(datetime.strptime("2000-01-01", "%Y-%m-%d"))
    assert rating == _DEFAULT_RATING


def test_team_get_rating_with_early_date():
    rating = team_a.get_rating(datetime.strptime("1800-01-01", "%Y-%m-%d"))
    assert rating == _DEFAULT_RATING


def test_team_initial_rating():
    rating = team_b.get_rating(datetime.strptime("2000-01-01", "%Y-%m-%d"))
    assert rating == 600
