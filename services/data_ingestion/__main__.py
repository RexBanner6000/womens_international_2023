from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

from data_ingestor.ingestor import create_dataset_from_file


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "raw_data",
        help="Match results file to ingest",
        type=Path
    )

    parser.add_argument(
        "sample_submission",
        help="Sample submission file",
        type=Path
    )

    parser.add_argument(
        "--training_output",
        help="File name for training output",
        default="training_data.csv"
    )

    parser.add_argument(
        "--submission_output",
        help="File name for submission output",
        default="submission_data.csv"
    )

    args = parser.parse_args()
    
    print(f"Reading data from {args.raw_data}...")
    results = create_dataset_from_file(Path(args.raw_data))

    print(f"Reading sample submission from {args.sample_submission}")
    submission_df = pd.read_csv(args.sample_submission)

    print(f"Generating training output {args.training_output}...")
    results.write_results_to_csv(Path(args.training_output))

    print(f"Generating test output {args.submission_output}...")
    test_df = results.create_test_df(submission_df)
    test_df.to_csv(args.submission_output, index=False)

    print("Done!")
