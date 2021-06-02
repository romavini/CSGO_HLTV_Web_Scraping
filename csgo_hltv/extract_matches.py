from csgo_hltv.extract_details import ExtractDetails
from typing import List
from random import random
from time import sleep

from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException


class Extract:
    def __init__(self, browser, n_page_start, n_page_end):
        self.browser = browser

        self.n_page_start = n_page_start
        self.n_page_end = n_page_end

    def print_message(self, status: str, text: str, message_type: str = "n"):
        """Print error given Exception

        Keyword argument:
        status -- message type
        message_type -- type of message print. can be 'e' for error, 's' for
        success, and 'n' for notification.
        """
        if message_type == "e":
            message_color = "\033[91m"
        elif message_type == "s":
            message_color = "\033[32m"
        elif message_type == "n":
            message_color = "\033[33m"

        print(
            "["
            + message_color
            + f"{status}"
            + "\033[0m"
            + "]"
            + message_color
            + " -> "
            + "\033[0m"
            + f"{text}"
        )

    def get_pages(self) -> List[str]:
        """Return DataFrame  with matches and record JSON file"""
        pages = ["https://www.hltv.org/results"]
        self.browser.get(pages[0])
        sleep(1 + random())

        pages_element = self.browser.find_element_by_class_name("pagination-data")
        max_pages = (
            int(int(pages_element.text.split(" of ")[-1].lstrip().rstrip()) / 100) - 1
        )

        if self.n_page_start != 1:
            pages = []

        for i in range(self.n_page_start - 2, min([self.n_page_end - 1, max_pages])):
            pages.append("https://www.hltv.org/results?offset=" + str((i + 1) * 100))

        return pages

    def get_matches(self, ext_details):
        pages = self.get_pages()

        for idx_page, page in enumerate(pages):
            match_links = []
            self.browser.get(page)
            sleep(1 + random())
            matches = self.browser.find_elements_by_class_name("a-reset")

            self.print_message(
                "Keeping",
                f"Collecting data from page {self.n_page_start + idx_page}",
                "s",
            )

            for match in matches:
                try:
                    match_type = match.find_element_by_class_name("map").text

                    if match_type == "bo3":
                        match_links.append(match.get_attribute("href"))

                except NoSuchElementException:
                    pass
            try:
                to_close = ext_details.extract_players(match_links)

                if to_close:
                    self.print_message("Stopped", "Exception in extraction", "e")
                    self.browser.quit()
                    return

            except ConnectionRefusedError or ConnectionRefusedError:
                self.print_message("Stopped", "Exception in connection", "e")
                self.browser.quit()
                return

        self.print_message("Success", "Extraction completed", "s")
        self.browser.quit()


if __name__ == "__main__":
    browser = Chrome()

    ext = Extract(browser, n_page_start=1, n_page_end=2)
    ext_details = ExtractDetails(browser)
    ext.get_matches(ext_details)
