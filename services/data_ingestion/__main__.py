import logging

from pathlib import Path

import pandas as pd

from data_ingestor.ingestor import create_dataset_from_file


raw_data = "./data/kaggle/results.csv"
sample_submission = "./rss-wwc-2023-prediction-competition/submission-template.csv"

if __name__ == "__main__":
    logging.info(f"Reading data from {raw_data}...")
    results = create_dataset_from_file(Path(raw_data))

    logging.info(f"Reading sample submission from {sample_submission}")
    submission_df = pd.read_csv(sample_submission)

    logging.info("Generating training output...")
    results.write_results_to_csv(Path("./results.csv"))

    logging.info("Generating test output")
    test_df = results.create_test_df(submission_df)
    test_df.to_csv("./test.csv", index=False)

    logging.info("Done!")
