from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


@dataclass
class WebLoadResult:
    url: str
    html: str


def create_headless_chrome() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    return driver


def load_dynamic_page(url: str, wait_css: Optional[str] = None, timeout: int = 20) -> WebLoadResult:
    driver = create_headless_chrome()
    try:
        driver.get(url)
        if wait_css:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_css))
            )
        html = driver.page_source
        return WebLoadResult(url=url, html=html)
    finally:
        driver.quit()
