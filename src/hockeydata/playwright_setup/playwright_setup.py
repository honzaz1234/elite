from playwright.sync_api import sync_playwright


COOKIES_AGREE_XPATH = "//button[./*[contains(text(), 'AGREE')]]"


class PlaywrightSetUp():


    FORBIDDEN_TYPES = ["image", "stylesheet", "font"]
    FORBIDDEN_STRINGS = [
        'google', 'clarity', 'analytics', 
        'RinksideWidget', 'facebook', 'twitter', 
        'reddit', 'linkedin', 'ad.doubleclick'
        'chrome', 'Endorsements', 'PlayerStatsAllTime',
        'PlayerTransactions', 'SubscriptionOffer', 'PlayerMedia',
        'PlayerGameLogs', 'DraftCoverage'
    ]


    def __init__(self):
        self.p = None
        self.browser = None
        self.page = None
        self.blocked_list = []
        self.initiate_sync_playwright()

    def initiate_sync_playwright(self):
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=True)
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


def get_xpath(path):
    """
    transform xpath in the form it can be used in scrapy selector
     to the form used in playwright
     """

    xpath = 'xpath=' + path
    return xpath
    
def click_on_button_optional(page, path):
    """wait for button for a specified amount of time and then continue
    either click it or contineu if it does not exist
    """

    xpath = get_xpath(path)
    try:
        page.wait_for_selector(xpath, timeout=1000)
        page.click(xpath)
    except:
        return
    
def click_on_button(page, path, wait=500):
    """wait for button for a specified amount of time and then continue
    either click it or contineu if it does not exist
    """

    xpath = get_xpath(path)
    page.wait_for_selector(xpath, timeout=wait)
    page.click(xpath)

def wait_click_wait(page, path_click, path_wait, wait=300, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Wait for the selector with a timeout of 10 seconds
            page.wait_for_selector(path_wait, timeout=wait)
            print("Target selector appeared!")
            break
        except:
            print(f"Attempt {attempt + 1}: Selector not found. Clicking fallback button...")
            try:
                # Click the fallback button
                page.click(path_click)
            except Exception as e:
                print(f"Error clicking fallback button: {e}")
                break
    else:
        print("Failed to find the selector after maximum retries.")
