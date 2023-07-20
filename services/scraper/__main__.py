import selenium

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == "__main__":
    url = "https://www.flashscore.co.uk/football/world/world-cup-women/#/plFV0LBD/live"
    driver = webdriver.Chrome()
    driver.get(url)
    summary = driver.find_elements(By.CLASS_NAME, "event--summary")
    matches = summary[0].find_elements(By.CLASS_NAME, "event__match--twoLine")

    for match in matches:
        try:
            home_score = match.find_element(By.CLASS_NAME, "event__score--home")
            away_score = match.find_element(By.CLASS_NAME, "event__score--away")
            event_stage = match.find_element(By.CLASS_NAME, "event__stage")
            home_team = match.find_element(By.CLASS_NAME, "event__participant--home")
            away_team = match.find_element(By.CLASS_NAME, "event__participant--away")
            print(f"{home_team.text}: {home_score.text} {away_team.text}: {away_score.text} - Status: {event_stage.text}")
        except NoSuchElementException:
            continue

    print("Done!")
