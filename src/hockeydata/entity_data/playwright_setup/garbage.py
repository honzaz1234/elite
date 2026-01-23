from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
import playwright.sync_api as sync_api
import playwright.async_api as async_api

from hockeydata.logger.logging_config import logger


COOKIES_AGREE_XPATH = "//button[./*[contains(text(), 'AGREE')]]"
FORBIDDEN_TYPES = ["image", "stylesheet", "font"]
FORBIDDEN_STRINGS = [
        'google', 'clarity', 'analytics', 
        'RinksideWidget', 'facebook', 'twitter', 
        'reddit', 'linkedin', 'ad.doubleclick'
        'chrome', 'Endorsements', 'PlayerStatsAllTime',
        'PlayerTransactions', 'SubscriptionOffer', 'PlayerMedia',
        'PlayerGameLogs', 'DraftCoverage',
    ]


def get_new_page(browser: sync_api.Browser) -> sync_api.Page:
        page = browser.new_page()
        page.route("**/*", intercept_requests)

        return page


def intercept_requests(
            route: sync_api.Route, request: sync_api.Request) -> None:
        if request.resource_type in FORBIDDEN_TYPES:
            route.abort()
        elif any(forbidden_string in request.url 
                 for forbidden_string in FORBIDDEN_STRINGS):
            route.abort()
        else:
            route.continue_()


class PlaywrightManager():


    def __init__(self):
        self.p: sync_api.Playwright = None
        self.browsers: list[sync_api.Browser] = []
        self.initiate_sync_playwright()


    def initiate_sync_playwright(self) -> None:
        self.p = sync_playwright().start()


    def get_browser(self) -> tuple[sync_api.Browser, int]:
        browser = self.p.chromium.launch(headless=False)
        self.browsers.append(browser)
        position = len(self.browsers) - 1

        return browser, position
    

    def get_new_page(self, browser: sync_api.Browser) -> sync_api.Page:
        page = browser.new_page()
        page.route("**/*", self.intercept_requests)

        return page
    

    def close(self) -> None:
        self.close_all_browsers()
        self.close_controller()


    def close_all_browsers(self) -> None:
        for browser in self.browsers:
            browser.close()


    def close_browser(self, position: int) -> None:
        self.browsers[position].close()


    def close_controller(self) -> None:
        self.p.stop()


    def intercept_requests(
            self, route: sync_api.Route, request: sync_api.Request) -> None:
        if request.resource_type in FORBIDDEN_TYPES:
            route.abort()
        elif any(forbidden_string in request.url 
                 for forbidden_string in FORBIDDEN_STRINGS):
            route.abort()
        else:
            route.continue_()


class AsyncPlaywrightSetUp:


    def __init__(self):
        self.p = None
        self.browser = None
        self.page = None


    async def initiate_async_playwright(self):
        self.p = await async_playwright().start()
        self.browser = await self.p.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        await self.page.route("**/*", self.intercept_requests)


    async def intercept_requests(
            self, route: async_api.Route, request: async_api.Request):
        if request.resource_type in FORBIDDEN_TYPES:
            await route.abort()
        elif any(
            forbidden_string in request.url
            for forbidden_string in FORBIDDEN_STRINGS
        ):
            await route.abort()
        else:
            await route.continue_()


async def click_on_button_optional(page: async_api.Page, path: str) -> None:
    """
    wait for button for a specified amount of time and then continue
    either click it or continue if it does not exist
    """
    xpath = get_xpath(path)
    try:
        await page.wait_for_selector(xpath, timeout=1000)
        await page.click(xpath)
    except Exception:
        return


async def click_on_button(
        page: async_api.Page, path: str, wait: int = 10000) -> None:
    """
    wait for button for a specified amount of time and then continue
    either click it or continue if it does not exist
    """
    xpath = get_xpath(path)
    await page.wait_for_selector(xpath, timeout=wait)
    await page.click(xpath)


async def wait_click_wait(
    page: async_api.Page,
    sel_click: str,
    sel_wait: str,
    wait: int = 300,
    max_retries: int = 3,
) -> None:
    for attempt in range(max_retries):
        try:
            await page.wait_for_selector(sel_wait, timeout=wait)
            logger.info("Target selector appeared!")
            break
        except Exception:
            logger.info(
                f"Attempt {attempt + 1}: Selector not found. Clicking fallback button..."
            )
            try:
                await page.click(sel_click)
            except Exception as e:
                logger.info(f"Error clicking fallback button: {e}")
                break
    else:
        logger.info("Failed to find the selector after maximum retries.")


async def go_to_page_wait(
        page: async_api.Page, url: str, sel_wait: str) -> None:
    sel_wait = get_xpath(sel_wait)
    await page.goto(url)
    await page.wait_for_selector(sel_wait)


async def go_to_page_wait_click_wait(
    page: async_api.Page,
    url: str,
    sel_click: str,
    sel_wait: str,
    wait: int = None,
    max_retires: int = 3,
) -> None:
    sel_click = get_xpath(sel_click)
    sel_wait = get_xpath(sel_wait)
    await page.goto(url)
    await wait_click_wait(
        page=page,
        sel_click=sel_click,
        sel_wait=sel_wait,
        wait=wait,
        max_retries=max_retires,
    )


async def click_optional_button(
    page: async_api.Page,
    sel_click: str,
    button_type: str,
    wait_time: int = 2000,
):
    sel_click = get_xpath(sel_click)
    try:
        await page.wait_for_selector(sel_click, timeout=wait_time, state="visible")
        await page.click(sel_click)
    except Exception:
        logger.info(f"Optional button ({button_type}) never became visible.")