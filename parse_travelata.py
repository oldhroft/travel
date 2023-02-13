from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

logger = logging.getLogger()

if __name__ == "__main__":
    browser = webdriver.Chrome(
        "/opt/homebrew/bin/chromedriver"
    )

    travelata_temp_url = "https://travelata.ru/tury/egypt#?fromCity=2&dateFrom=27.02.2023&dateTo=27.02.2023&nightFrom=3&nightTo=10&adults=2&hotelClass=all&meal=all&sid=bsxr1619np&sort=priceUp&f_good=true&toCountries=29"

    logger.info(f"Travelling to {travelata_temp_url}")
    browser.get(travelata_temp_url)
    logger.info("Sleeping")
    time.sleep(2)
    logger.info("Waking up")
    content = browser.page_source
    soup = BeautifulSoup(content, "html.parser")
    banner = soup.find("p", class_="marketing-banner__label")
    logger.info("Check if a banner is present")
    if banner is not None:
        logger.info("Clickhing the banner")
        browser.find_element(By.CSS_SELECTOR, 
            "div.btn.btnOrange.btnFlat.js-popup-close").click()

    logger.info("Sleeping")
    time.sleep(20)
    logger.info("Waking up")
    logger.info("Scrolling")
    max_iter = 20
    old_height = 0
    for i in range(max_iter):
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

    with open("collected_hotels.html", "w") as file:
        file.write(content)
