import numpy as np
import pandas as pd
from argparse import ArgumentParser
from sklearn.model_selection import GridSearchCV, train_test_split
from pathlib import Path
from xgboost import XGBClassifier


def remove_enum_from_str(name: str) -> str:
    return name.split(".")[-1]


def post_process_predictions(y_preds: np.ndarray, submission_template: pd.DataFrame) -> pd.DataFrame:
    submission = submission_template.copy()
    submission["p_team1_win"] = y_preds[:, 0]
    submission["p_team2_win"] = y_preds[:, 1]
    submission["p_draw"] = y_preds[:, 2]

    for idx, row in submission.iterrows():
        if row["group"] == "Knockout":
            p1_adjusted = row["p_team1_win"] + row["p_team1_win"] / (row["p_team1_win"] + row["p_team2_win"]) * row["p_draw"]
            p2_adjusted = row["p_team2_win"] + row["p_team2_win"] / (row["p_team1_win"] + row["p_team2_win"]) * row["p_draw"]
            submission.loc[idx, "p_team1_win"] = p1_adjusted
            submission.loc[idx, "p_team2_win"] = p2_adjusted
            submission.loc[idx, "p_draw"] = 0

    return submission


def process_input_data(df: pd.DataFrame) -> pd.DataFrame:
    df["match_type"] = df["match_type"].apply(remove_enum_from_str)
    categorical_vars = df.select_dtypes(exclude=np.number).columns.to_list()

    for col in categorical_vars:
        df[col] = df[col].astype("category")

    return df[
        ["home_rating", "away_rating", "match_type", "home_ranking", "away_ranking", "home_recent_scored", "away_recent_scored", "home_recent_conceded", "away_recent_conceded"]
    ]


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "training_data",
        type=Path,
    )

    parser.add_argument(
        "submission_data",
        type=Path
    )

    parser.add_argument(
        "--output_file",
        type=str,
        default="xgboost_predictions.csv"
    )

    args = parser.parse_args()

    matches_df = pd.read_csv(args.training_data)
    y = matches_df.pop("result")
    X = process_input_data(matches_df)

    X_train, X_val, y_train, y_val = train_test_split(X, y, random_state=1)

    model = XGBClassifier(
        objective="multi:softmax",
        tree_method="gpu_hist",
        num_class=3,
        enable_categorical=True
    )

    parameters = {
        'max_depth': range(4, 10, 1),
        'n_estimators': range(60, 220, 40),
        'learning_rate': [0.1, 0.01, 0.05]
    }

    grid_search = GridSearchCV(
        estimator=model,
        param_grid=parameters,
        scoring='neg_log_loss',
        n_jobs=8,
        cv=5,
        verbose=2,
        return_train_score=True
    )

    grid_search.fit(X, y)

    submission_df = pd.read_csv(args.submission_data)
    X_submission = process_input_data(submission_df)

    y_preds = grid_search.best_estimator_.predict_proba(X_submission)
    np.savetxt("raw_predictions.csv", y_preds, delimiter=",")

    submission_template = pd.read_csv("./rss-wwc-2023-prediction-competition/submission-template.csv")
    submission = post_process_predictions(y_preds, submission_template)
    submission.to_csv(args.output_file, index=False)
