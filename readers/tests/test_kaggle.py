from pathlib import Path

from pytest import fixture

from readers.kaggle import read_kaggle_data


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


def test_read_kaggle_data(dummy_csv_file):
    df = read_kaggle_data(Path(dummy_csv_file))

    assert len(df) == 2
