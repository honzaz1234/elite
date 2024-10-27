from playwright.sync_api import sync_playwright


COOKIES_AGREE_XPATH = "//button[./*[contains(text(), 'AGREE')]]"

class PlaywrightSetUp():

    def __init__(self, blocked_types=["image", "stylesheet", "font"]):
        self.p = None
        self.blocked_types = blocked_types
        self.browser = None
        self.page = None
        self.initiate_sync_playwright()

    def initiate_sync_playwright(self):
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.route("**/*", self.block_non_essential)

    def block_non_essential(self, route, request):
        if request.resource_type in self.blocked_types:
            route.abort()
        else:
            route.continue_()


def get_all_result_texts(page, xpath):
    # Using query_selector_all to get a list of elements, then retrieving inner_text for each
    print(xpath)
    result_elements = page.query_selector_all(xpath)
    results =  [element.inner_text() for element in result_elements]
    striped_results = [string.strip() for string in results]
    return striped_results

def get_all_result_attribute(page, xpath, attribute_type):
    # Using query_selector_all to get a list of elements, then retrieving inner_text for each
    print(xpath)
    result_elements = page.query_selector_all(xpath)
    results =  [element.get_attribute(attribute_type) 
                for element in result_elements]
    striped_results = [string.strip() for string in results]
    return striped_results


def get_xpath(path):
    """
    transform xpath in the form it can be used in scrapy selector
     to the form used in playwright
     """

    xpath = 'xpath=' + path
    return xpath
    
def click_on_button(page, path):

    xpath = get_xpath(path)
    page.click(xpath)
