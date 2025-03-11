from scraper import supply_logger, set_up_driver

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

url = "https://free-proxy-list.net/"
logger = supply_logger()
driver = set_up_driver(logger)
driver.get(url)

try:
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-responsive.fpl-list"))
    )
except TimeoutException as e:
    import sys
    driver.close()
    logger.error(e)
    sys.exit()

table_body = table.find_element(By.TAG_NAME, "tbody")
soup = BeautifulSoup(str(table_body.get_attribute("outerHTML")))
print(soup.prettify())

driver.close()
