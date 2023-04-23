from pathlib import Path

import pandas as pd
from pandas import DataFrame


def read_kaggle_data(csv_file: Path) -> DataFrame:
    return pd.read_csv(csv_file)
