from bundler_qa.common.driver import Driver
from bundler_qa.common.webpage import WebPage

from datetime import datetime
from pathlib import Path

import json

import pytest

TEST_DATA_PATH = Path(__file__).parent / "resources/data.json"


@pytest.fixture(scope="class")
def driver() -> Driver:
    driver = Driver()
    yield driver
    driver.quit()


with open(str(TEST_DATA_PATH), "r") as f:
    test_data = json.load(f)


class TestWebclient:
    @pytest.fixture(autouse=True)
    def setup_class(self, driver: Driver):
        assert driver.check_webclient() is True, "Web Client is not Running!"
        assert driver.check_webserver() is True, "Web Server is not Running!"

        for file in driver.DOWNLOAD_PATH.glob("*.zip"):
            file.unlink()

    @pytest.fixture(autouse=True)
    def setup_method(self, driver: Driver):
        driver.get(driver.base_url)

    def test_landing(self, driver: Driver):
        assert "LÖVEBrew" in driver.title(), f"Landing Page title was {driver.title()}"

    def resolve_file(self, filename: Path, suffix: str) -> str:
        if isinstance(filename, str):
            filename = Path(filename)

        return str(filename.with_suffix(suffix))

    def resolve_files(self, filenames: list[Path], suffix: str) -> list[str]:
        return [self.resolve_file(filename, suffix) for filename in filenames]

    @pytest.mark.parametrize("filename", test_data["validTextures"])
    def test_valid_texture_upload(self, filename: str, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file(filename).validate_toast(True, "Downloaded")
        home_page.validate_latest_bundle(self.resolve_files([filename], ".t3x"))

    @pytest.mark.parametrize("filename", test_data["largeTextureBoth"])
    def test_large_texture_dimensions_upload(self, filename: str, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file(filename).validate_toast(
            False, f"Image {filename} is too large!"
        )

    @pytest.mark.parametrize("filename", test_data["largeTextureWidth"])
    def test_large_texture_width_upload(self, filename: str, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file(filename).validate_toast(
            False, f"Image {filename} is too large!"
        )

    @pytest.mark.parametrize("filename", test_data["largeTextureHeight"])
    def test_large_texture_height_upload(self, filename: str, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file(filename).validate_toast(
            False, f"Image {filename} is too large!"
        )

    @pytest.mark.parametrize("filename", test_data["invalidTextures"])
    def test_invalid_texture_upload(self, filename: str, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file(filename).validate_toast(False, "Invalid file type.")

    @pytest.mark.parametrize("filename", test_data["validFonts"])
    def test_valid_font_upload(self, filename: str, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file(filename).validate_toast(True, "Downloaded")
        home_page.validate_latest_bundle(self.resolve_files([filename], ".bcfnt"))

    @pytest.mark.parametrize("filename", test_data["invalidFonts"])
    def test_invalid_font_upload(self, filename: str, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file(filename).validate_toast(False, "Invalid file type.")

    def test_empty_file_upload(self, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file("emptyfile").validate_toast(False, "Invalid file.")

    @pytest.mark.parametrize("filename", test_data["missingConfigs"])
    def test_missing_config_upload(self, filename: str, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file(filename).validate_toast(
            False, "Missing configuration file."
        )

    def test_missing_game_folder(self, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file("content-no-game.zip").validate_toast(
            False, "Source folder 'game' not found."
        )

    @pytest.mark.parametrize("filename", test_data["validContentBundles"])
    def test_valid_content_bundle_upload(self, filename: str, driver: Driver):
        home_page = WebPage(driver)

        home_page.upload_file(filename).validate_toast(True, "Downloaded")
        home_page.validate_latest_bundle(
            ["SuperGame.3dsx", "SuperGame.nro", "SuperGame.wuhb"]
        )
