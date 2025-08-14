import playwright.sync_api as sync_api

from logger.logging_config import logger


COOKIES_AGREE_XPATH = "//button[./*[contains(text(), 'AGREE')]]"


class PlaywrightSetUp():


    FORBIDDEN_TYPES = ["image", "stylesheet", "font"]
    FORBIDDEN_STRINGS = [
        'google', 'clarity', 'analytics', 
        'RinksideWidget', 'facebook', 'twitter', 
        'reddit', 'linkedin', 'ad.doubleclick'
        'chrome', 'Endorsements', 'PlayerStatsAllTime',
        'PlayerTransactions', 'SubscriptionOffer', 'PlayerMedia',
        'PlayerGameLogs', 'DraftCoverage',
    ]


    def __init__(self):
        self.p = None
        self.browser = None
        self.page = None
        self.blocked_list = []
        self.initiate_sync_playwright()

    def initiate_sync_playwright(self):
        self.p = sync_api.sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.route("**/*", self.intercept_requests)

    def intercept_requests(self, route, request):
        if request.resource_type in PlaywrightSetUp.FORBIDDEN_TYPES:
            route.abort()
        elif any(forbidden_string in request.url 
                 for forbidden_string in PlaywrightSetUp.FORBIDDEN_STRINGS):
            route.abort()
        else:
            route.continue_()


def get_xpath(path: str) -> str:
    """
    transform xpath in the form it can be used in scrapy selector
     to the form used in playwright
     """

    xpath = 'xpath=' + path
    return xpath
    
def click_on_button_optional(page: sync_api.Page, path: str) -> None:
    """wait for button for a specified amount of time and then continue
    either click it or contineu if it does not exist
    """

    xpath = get_xpath(path)
    try:
        page.wait_for_selector(xpath, timeout=1000)
        page.click(xpath)
    except:
        return
    
def click_on_button(page: sync_api.Page, path: str, wait=10000) -> None:
    """wait for button for a specified amount of time and then continue
    either click it or contineu if it does not exist
    """

    xpath = get_xpath(path)
    page.wait_for_selector(xpath, timeout=wait)
    page.click(xpath)

def wait_click_wait(
        page: sync_api.Page, sel_click: str, sel_wait: str, wait=300, max_retries=3) -> None:
    for attempt in range(max_retries):
        try:
            page.wait_for_selector(sel_wait, timeout=wait)
            logger.info("Target selector appeared!")
            break
        except:
            logger.info(f"Attempt {attempt + 1}: Selector not found. Clicking"
                  f" fallback button...")
            try:
                # Click the fallback button
                page.click(sel_click)
            except Exception as e:
                logger.info(f"Error clicking fallback button: {e}")
                break
    else:
        logger.info(f"Failed to find the selector after maximum retries.")

def go_to_page_wait_selector(
        page: sync_api.Page, url: str, sel_wait: str) -> None:
    sel_wait = get_xpath(sel_wait)
    page.goto(url)
    page.wait_for_selector(sel_wait)

def go_to_page_wait_click_wait(
        page: sync_api.Page, url: str, sel_click: str, sel_wait: str,
        wait: int=None, max_retires: int=3) -> None:
    sel_click = get_xpath(sel_click)
    sel_wait = get_xpath(sel_wait)
    page.goto(url)
    wait_click_wait(
        page=page,
        sel_click=sel_click,
        sel_wait=sel_wait,
        wait=wait,
        max_retries=max_retires
        )


def click_optional_button(
        page: sync_api.Page, sel_click: str, button_type: str, 
        wait_time: int=2000):
    sel_click = get_xpath(sel_click)
    try:
        page.wait_for_selector(sel_click, timeout=wait_time, state="visible")
        page.click(sel_click)
    except:
        print("Optional button (%s) never became visible.", button_type)