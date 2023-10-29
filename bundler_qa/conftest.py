import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])
    if report.when == "call":
        xfail_state = hasattr(report, "wasxfail")
        if (report.skipped and xfail_state) or (report.failed and not xfail_state):
            driver = item.funcargs["driver"]
            driver.save_screenshot(f"failure_{item.name}.png")
    report.extras = extra
