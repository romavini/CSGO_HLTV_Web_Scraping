from botcsgo.extract_details import ExtractDetails
from botcsgo.extract_matches import Extract

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

if __name__ == "__main__":
    print("\nMatches Extractor\n")

    n_pages_start = int(input("Start in wich page? -> "))
    n_pages_end = int(input("End in wich page? -> "))
    mode = input("Press 's' to silent mode and 'Enter' to start. -> ")

    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")

    if mode.lower() == "s":
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-software-rasterizer")

    browser = Chrome(options=chrome_options)

    if n_pages_start > n_pages_end:
        n_pages_end = n_pages_start

    ext = Extract(browser, n_pages_start, n_pages_end)
    ext_details = ExtractDetails(browser)
    ext.get_matches(ext_details)
