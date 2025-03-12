import datetime as dt
import logging
from pathlib import Path
import random
import sys

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait


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


def set_up_driver(
    logger: logging.Logger,        
    headless: bool = False,
    ip_port: str = ""
    ) -> WebDriver:

    ua = UserAgent(browsers=["Firefox"])
    agent = ua.random 
    logger.info(f"User Agent used: {agent}")

    options = Options()
    options.set_preference("general.useragent.override", agent)
    options.set_preference("dom.webdriver.enabled", False)
    options.add_argument("--disable-blink-features=AutomationControlled") 

    if headless:
        options.add_argument("--headless")

    if ip_port:
        logger.info(f"Proxy used: {ip_port}")

        ip, port = ip_port.split(":")
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.http", ip)
        options.set_preference("network.proxy.http_port", int(port))
        options.set_preference("network.proxy.ssl", ip)
        options.set_preference("network.proxy.ssl_port", int(port))
        options.set_preference("network.proxy.no_proxies_on", "")

    driver = WebDriver(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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
    

def search_for(term: str, html: str, logger: logging.Logger):
    result = term in html
    logger.info(f"Found {term} in source? {result}")


def get_proxy(
    driver: WebDriver,
    proxy_list: str = "https://free-proxy-list.net/"
) -> str:

    driver.get(proxy_list)
    
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-responsive.fpl-list"))
    )
    rows = table.find_elements(By.TAG_NAME, "tr")
    
    data = list()
    for row in rows:
        cells = row.text.split(maxsplit=2)[:2]
        ip_port = cells[0] + ":" + cells[1]
        data.append(ip_port)
    data.pop(0)
    ip_port = random.choice(data)
    driver.close()
    return ip_port


if __name__ == "__main__":
    url = "https://www.efbet.com/"
    logger = supply_logger()
    proxy_getter = set_up_driver(logger, headless=True)
    #    ip_port = get_proxy(proxy_getter)
    ip_port = "13.37.89.201:80"
    driver = set_up_driver(logger, ip_port=ip_port)
    driver.get(url)
    write_to_file(driver.page_source)
    search_for("НБА", driver.page_source, logger)
    driver.close()
