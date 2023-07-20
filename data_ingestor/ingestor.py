from pathlib import Path

from model.results import ResultsDataset
from readers.kaggle import read_kaggle_data


def create_dataset_from_file(csv_file: Path) -> ResultsDataset:
    results = ResultsDataset()
    df = read_kaggle_data(csv_file)

    results.populate_data_from_df(df)
    results.calculate_ratings()

    return results


if __name__ == "__main__":
    results = create_dataset_from_file(Path("../data/results.csv"))
