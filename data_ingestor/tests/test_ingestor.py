from pytest import fixture

from data_ingestor.ingestor import create_dataset_from_file
from model.entities import Tournament


@fixture(scope="session")
def dummy_csv_file(tmp_path_factory):
    dummy_csv = """
date,home_team,away_team,home_score,away_score,tournament,city,country,neutral
1969-11-01,Italy,France,1,0,Euro,Novara,Italy,FALSE
1969-11-01,Denmark,England,4,3,Euro,Aosta,Italy,TRUE
"""
    fn = tmp_path_factory.mktemp("data") / "dummy.csv"
    with open(fn, "w") as fp:
        fp.write(dummy_csv)
    return fn


def test_create_dataset_from_file(dummy_csv_file):
    results = create_dataset_from_file(dummy_csv_file)

    assert len(results.teams) == 4
    assert len(results.events) == 1
    assert len(results.tournaments) == 1
    assert results.tournaments[0] == Tournament(name="Euro", year=1969)
