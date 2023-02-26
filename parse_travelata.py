from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup
import time

import datetime
import yaml
import json
import uuid

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger()

def hover_and_right_click(browser:  webdriver.Chrome, element):
    hover = ActionChains(browser).move_to_element(element).context_click(element)
    hover.perform()

def parse_country(
    browser: webdriver.Chrome,
    country_code: str,
    night_from: int,
    night_to: int,
    time_fmt: str='%Y-%m-%dT%H:%M:%SZ'
) -> None:
    
    parsing_id = str(uuid.uuid4())
    
    # TODO unify for different parsers
    meta = {
        "country_code": country_code,
        "night_from": night_from,
        "night_to": night_to,
        "parsing_started": datetime.datetime.now().strftime(time_fmt),
        "parsing_id": parsing_id,
    }

    logger.info(f"Parsing {country_code} nights {night_from} to {night_to}")
    with open("template_string.txt", "r") as ts:
        template_url = ts.read()

    today = datetime.date.today()
    fmt = "%d.%m.%Y"
    date_from = (today + datetime.timedelta(days=1)).strftime(fmt)
    date_to = (today + datetime.timedelta(days=31)).strftime(fmt)
    meta["date_from"] = date_from
    meta["date_to"] = date_to

    url = template_url.format(
        country=country_code, date_from=date_from, date_to=date_to,
        night_from=night_from, night_to=night_to
    )
    meta["search_url"] = url
    logger.info(f"Travelling to {url}")
    browser.get(url)
    logger.info("Sleeping")
    time.sleep(2)
    logger.info("Waking up")

    content = browser.page_source
    soup = BeautifulSoup(content, "html.parser")
    banner = soup.find("p", class_="marketing-banner__label")
    logger.info("Check if a banner is present")
    if banner is not None:
        logger.info("Clicking the banner")
        button = browser.find_element(
            By.CSS_SELECTOR, "div.btn.btnOrange.btnFlat.js-popup-close"
        )
        if button.is_displayed() and button.is_enabled():
            logger.info("Button is clickable")
            button.click()

    logger.info("Sleeping")
    time.sleep(10)
    logger.info("Waking up")

    logger.info("Scrolling")
    old_height = 0
    delta = 0.25 * browser.execute_script("return document.body.scrollHeight")
    second_chance = True
    while True:
        browser.execute_script(
            f"window.scrollTo(0, document.body.scrollHeight - {delta});"
        )
        time.sleep(3)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = browser.execute_script("return document.body.scrollHeight")
        logger.info(f"New height is {new_height}")
        time.sleep(3)
        if new_height == old_height:
            if second_chance:
                old_height = new_height
                browser.execute_script(
                    f"window.scrollTo(0, document.body.scrollHeight - {delta});"
                )
                logger.info("Second chance")
                second_chance = False
                time.sleep(6)
            else:
                logger.info("Scrolling finished!")
                break
        else:
            old_height = new_height

    time.sleep(4)
    logger.info("Trying to get links")

    elements = browser.find_elements(By.CSS_SELECTOR, "a.serpHotelCard__title.goToHotel")

    for element in elements:
        hover_and_right_click(browser, element)
        time.sleep(.2)
        href = element.get_attribute("href")
        logger.info(f"extracting url {href}")
    
    meta["parsing_ended"] = datetime.datetime.now().strftime(time_fmt)

    logger.info("Downloading page source")
    content = browser.page_source
    fp = f"data_html/collected_hotels_{country_code}_{night_from}to{night_to}.html"
    with open(fp, "w") as file:
        file.write(content)
        
    meta["path"] = fp
    with open(f"data_html/collected_hotels_{country_code}_{night_from}to{night_to}.json", "w") as file:
        json.dump(meta, file)


if __name__ == "__main__":
    options = Options()
    options.add_argument("window-size=1920,1080")
    options.add_argument("--headless")
    browser = webdriver.Chrome(
        "/opt/homebrew/bin/chromedriver", chrome_options=options)

    with open("meta.yaml", "r", encoding="utf-8") as file:
        meta = yaml.safe_load(file)

    codes = list(meta["countries"].values())

    for code in codes:
        parse_country(browser, country_code=code, night_from=7, night_to=7)
