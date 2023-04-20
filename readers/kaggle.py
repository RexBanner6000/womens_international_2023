from pathlib import Path
from pandas import DataFrame
import pandas as pd


def read_kaggle_data(csv_file: Path) -> DataFrame:
    return pd.read_csv(csv_file)
