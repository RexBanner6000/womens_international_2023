import os

import psycopg2
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class EventStatus(Enum):
    PENDING = "PENDING"
    IN_PLAY = "IN_PLAY"
    FINISHED = "FINISHED"
    UNKNOWN = "UNKNOWN"


class MatchStage(Enum):
    GROUP = "GROUP"
    KNOCKOUT = "KNOCKOUT"


@dataclass
class MatchResult:
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    event_status: EventStatus
    match_stage: MatchStage


def connect_to_db():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    return conn


def write_match_to_db(result: MatchResult, conn) -> None:
    sql = generate_match_sql(result)
    cur = conn.cursor()
    cur.execute(sql)


def generate_match_sql(result: MatchResult) -> str:
    sql = f"INSERT INTO results " \
          f"(home_team, away_team, stage, score_home, score_away, status, time) " \
          f"VALUES ('{result.home_team}', '{result.away_team}', '{result.match_stage.value}', " \
          f"'{result.home_score}', '{result.away_score}', '{result.event_status.value}', " \
          f"'{datetime.now()}')"
    return sql


def get_status(event_stage: str) -> EventStatus:
    if event_stage == "Finished":
        return EventStatus.FINISHED
    else:
        return EventStatus.UNKNOWN


if __name__ == "__main__":
    url = "https://www.flashscore.co.uk/football/world/world-cup-women/#/plFV0LBD/live"
    driver = webdriver.Chrome()
    driver.get(url)
    summary = driver.find_elements(By.CLASS_NAME, "event--summary")
    matches = summary[0].find_elements(By.CLASS_NAME, "event__match--twoLine")

    conn = connect_to_db()

    for match_element in matches:
        try:
            home_score = match_element.find_element(By.CLASS_NAME, "event__score--home").text
            away_score = match_element.find_element(By.CLASS_NAME, "event__score--away").text
            event_stage = match_element.find_element(By.CLASS_NAME, "event__stage").text
            home_team = match_element.find_element(By.CLASS_NAME, "event__participant--home").text
            away_team = match_element.find_element(By.CLASS_NAME, "event__participant--away").text
            print(
                f"{home_team}: {home_score} {away_team}: {away_score} - Status: {event_stage}"
            )

            event_status = get_status(event_stage)

            if event_status == EventStatus.FINISHED:
                match_result = match = MatchResult(
                    home_team=home_team,
                    away_team=away_team,
                    home_score=int(home_score),
                    away_score=int(away_score),
                    event_status=event_status,
                    match_stage=MatchStage.GROUP if datetime.now() < datetime(2023, 8, 5) else MatchStage.KNOCKOUT
                )
        except NoSuchElementException:
            continue

        print(f"Writing {match_result.home_team} vs {match_result.away_team} to db")
        write_match_to_db(match_result, conn)

    conn.commit()

    print("Done!")
