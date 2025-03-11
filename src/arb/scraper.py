import datetime as dt
import logging
from pathlib import Path
import requests
import sys

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver


def supply_logger() -> logging.Logger:
    if '__file__' in globals():
        current_file = Path(__file__).resolve()
        logger_name = current_file.stem
        log_file_path = current_file.with_suffix('.log')
    else:
        logger_name = 'default'
        log_file_path = Path('default.log')
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt="%y-%m-%d %H:%M")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
    
    return logger


logger = supply_logger()


def check_ip():
    ip = requests.get("https://httpbin.org/ip").json()["origin"]
    logger.info(f"Using IP: {ip}")


def set_up_driver(
        headless: bool = False,
        iwait: int = 0) -> WebDriver:

    ua = UserAgent(browsers=["Firefox"])
    agent = ua.random 

    options = Options()

    options.set_preference("general.useragent.override", agent)
    options.set_preference("dom.webdriver.enabled", False)

    options.add_argument("--disable-blink-features=AutomationControlled") 

    if headless:
        options.add_argument("--headless")

    driver = WebDriver(options=options)
    
    if iwait:
        driver.implicitly_wait(iwait)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    agent = driver.execute_script("return navigator.userAgent")
    logger.info(f"User Agent used: {agent}")

    return driver


def write_to_file(html: str): 

    output = Path("~/cod/arb/src/arb/output.html").expanduser()
    if output.exists():
        for file in Path(output.parent).glob(output.stem + "_*"):
            file.unlink()
    
        tag = dt.datetime.now().strftime("_%y-%m-%d_%H:%M")
        tagged_stem = output.stem + tag
        output.rename(output.with_stem(tagged_stem))
    
    with open(output, "w") as f:
        soup = BeautifulSoup(html, "html.parser")
        f.write(str(soup.prettify()))
    

def search_for(term: str, html: str):
    result = term in html
    logger.info(f"Found {term} in source? {result}")


if __name__ == "__main__":
    url = "https://www.efbet.com/BG/sports#bo-navigation=281982.1&action=market-group-list"
    check_ip()
    driver = set_up_driver(iwait=10)
    driver.get(url)
    write_to_file(driver.page_source)
    search_for("НБА", driver.page_source)
    driver.close()
