from pathlib import Path

from data_ingestor.ingestor import create_dataset_from_file

if __name__ == "__main__":
    results = create_dataset_from_file(Path("./data/kaggle/results.csv"))
    results.write_results_to_csv(Path("./results.csv"))
