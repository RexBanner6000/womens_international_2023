from datetime import datetime

from model.entities import _DEFAULT_RATING, Team

team_a = Team(name="TEAM A")
team_b = Team(name="TEAM B", initial_rating=600)
team_b.rating[datetime(year=2000, month=3, day=24)] = 601
team_b.rating[datetime(year=2000, month=4, day=22)] = 602


def test_team_get_rating_date():
    rating = team_a.get_rating(datetime.strptime("2000-01-01", "%Y-%m-%d"))
    assert rating == _DEFAULT_RATING


def test_team_get_rating_with_early_date():
    rating = team_a.get_rating(datetime.strptime("1800-01-01", "%Y-%m-%d"))
    assert rating == _DEFAULT_RATING


def test_team_initial_rating():
    rating = team_b.get_rating(datetime.strptime("2000-01-01", "%Y-%m-%d"))
    assert rating == 600


def test_team_last_played():
    last_played = team_b.get_last_played_date(datetime(2000, 4, 1))
    assert last_played == datetime(2000, 3, 24)
    last_played = team_b.get_last_played_date(datetime(2000, 5, 1))
    assert last_played == datetime(2000, 4, 22)
