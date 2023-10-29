from pathlib import Path
from typing import Self
import zipfile
from bundler_qa.common.driver import Driver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

import logging


class WebPage:
    ErrorToast = "//*[contains(@class, 'bg-red-600')]"
    SuccessToast = "//*[contains(@class, 'bg-green-600')]"
    UploadInput = "//input[@type='file']"

    FilesPath = Path(__file__).parent.parent / "resources/files"

    def __init__(self, driver: Driver):
        self.driver = driver

    def validate_toast(self, success: bool, message: str) -> Self:
        toast = self.SuccessToast if success else self.ErrorToast
        wait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, toast)))

        toast_element = self.driver.find(By.XPATH, toast)
        assert (
            message in toast_element.text
        ), f"Expected Toast message '{message}', got '{toast_element.text}'"

        return self

    def upload_file(self, filename: str) -> Self:
        filepath = f"{WebPage.FilesPath}/{filename}"

        wait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, WebPage.UploadInput))
        )

        upload = self.driver.find(By.XPATH, WebPage.UploadInput)
        upload.send_keys(filepath)

        return self

    def validate_latest_bundle(self, files: list[str]) -> Self:
        wait(self.driver, 10).until(
            lambda x: (Driver.DOWNLOAD_PATH / "bundle.zip").exists()
        )

        latest_file = max(
            self.driver.DOWNLOAD_PATH.glob("*.zip"),
            key=lambda f: f.stat().st_mtime,
        )

        assert latest_file.exists(), "Could not find latest bundle."
        logging.info(f"Found latest bundle: {latest_file}")

        with zipfile.ZipFile(latest_file.resolve(), "r") as zip:
            logging.info(f"Validating bundle contents: {zip.namelist()}")
            assert all(
                file in zip.namelist() for file in files
            ), f"Expected files {files} in bundle, got {zip.namelist()}"

        latest_file.unlink()
        return self
