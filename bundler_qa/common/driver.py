import datetime
import sys
import logging
import tomllib
import http

from pathlib import Path
import requests

from selenium import webdriver

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

CHROME_DRIVER_VERSION_URL = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"


class Driver:
    BIN_DIR = (Path(__file__).parent.parent / "bin").resolve()
    CONFIG_PATH = (Path(__file__).parent.parent / "config.toml").resolve()
    DOWNLOAD_PATH = (Path(__file__).parent.parent / "downloads").resolve()
    SCREENSHOTS_PATH = (Path(__file__).parent.parent / "screenshots").resolve()
    LOG_DIR = (Path(__file__).parent.parent / "logs").resolve()

    def __init__(self):
        Driver.LOG_DIR.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    f"bundler_qa-{datetime.datetime.now().timestamp()}.log"
                ),
            ],
            force=True,
        )

        config = dict()
        with open(Driver.CONFIG_PATH) as f:
            config = tomllib.loads(f.read())

        driver = None
        driver_type = config["driver"]["browser"]

        match driver_type:
            case "chrome":
                driver = self.__init_chromedriver__()
            case "firefox":
                driver = self.__init__geckodriver__(Driver.BIN_DIR / "geckodriver")
            case _:
                raise Exception("Invalid driver type")

        logging.info(f"Initialized {type} driver")

        self.driver = driver

        self.base_url = config["driver"]["base_url"]
        self.data_url = config["driver"]["data_url"]

    def __init_chromedriver__(self):
        options = ChromeOptions()

        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": f"{Driver.DOWNLOAD_PATH}",
                "download.prompt_for_download": False,
                "savefile.default_directory": f"{Driver.DOWNLOAD_PATH}",
            },
        )

        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        return webdriver.Chrome(options)

    def __init__geckodriver__(self, driver_path: Path):
        options = FirefoxOptions()

        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", f"{Driver.DOWNLOAD_PATH}")
        options.set_preference("browser.helperApps.alwaysAsk.force", False)

        if not Path(driver_path).exists():
            logging.info("Downloading geckodriver")

        return webdriver.Firefox(driver_path, options=options)

    def check_webclient(self) -> bool:
        try:
            request = requests.get(self.base_url)
            return request.status_code == http.HTTPStatus.OK
        except requests.exceptions.RequestException:
            return False

    def check_webserver(self) -> bool:
        try:
            request = requests.get(self.data_url)
            return request.status_code == http.HTTPStatus.OK
        except requests.exceptions.RequestException:
            return False

    def save_screenshot(self, filename: str):
        Driver.SCREENSHOTS_PATH.mkdir(exist_ok=True)
        self.driver.save_screenshot(f"{Driver.SCREENSHOTS_PATH}/{filename}")

    def get_screenshot_as_base64(self) -> str:
        return self.driver.get_screenshot_as_base64()

    def get(self, url: str):
        logging.info(f"Getting {url}")
        self.driver.get(url)

    def title(self) -> str:
        return self.driver.title

    def find(self, by: str, value: str):
        return self.driver.find_element(by, value)

    def find_element(self, by: str, value: str):
        return self.find(by, value)

    def quit(self):
        if self.driver:
            self.driver.quit()
