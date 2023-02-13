from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

import datetime
import yaml

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger()


def parse_country(
    browser: webdriver.Chrome,
    country_code: str,
) -> None:
    logger.info(f"Parsing {country_code}")
    with open("template_string.txt", "r") as ts:
        template_url = ts.read()

    today = datetime.date.today()
    fmt = "%d.%m.%Y"
    date_from = (today + datetime.timedelta(days=1)).strftime(fmt)
    date_to = (today + datetime.timedelta(days=31)).strftime(fmt)

    url = template_url.format(
        country=country_code, date_from=date_from, date_to=date_to
    )
    logger.info(f"Travelling to {url}")
    browser.get(url)
    logger.info("Sleeping")
    time.sleep(1)
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
    time.sleep(20)
    logger.info("Waking up")

    logger.info("Scrolling")
    max_iter = 20
    old_height = 0
    delta = 0.25 * browser.execute_script("return document.body.scrollHeight")
    for i in range(max_iter):
        browser.execute_script(
            f"window.scrollTo(0, document.body.scrollHeight - {delta});"
        )
        time.sleep(6)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = browser.execute_script("return document.body.scrollHeight")
        logger.info(f"New height is {new_height}")
        time.sleep(4)
        if new_height == old_height:
            logger.info("Scrolling finished!")
            break
        else:
            old_height = new_height

    time.sleep(4)
    logger.info("Downloading page source")
    content = browser.page_source

    with open(f"data_html/collected_hotels_{country_code}.html", "w") as file:
        file.write(content)


if __name__ == "__main__":
    browser = webdriver.Chrome("/opt/homebrew/bin/chromedriver")
    with open("meta.yaml", "r", encoding="utf-8") as file:
        meta = yaml.safe_load(file)

    codes = list(meta["countries"].values())
    for code in codes:
        parse_country(browser, country_code=code)
