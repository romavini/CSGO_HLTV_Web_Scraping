import json
import pandas as pd
from random import random
from time import sleep
from selenium.webdriver import Chrome


class Extract:
    def __init__(self):
        self.browser = Chrome()
        self.check_files()


    def check_files(self):
        """check date of recorded matches"""
        updated = False

        if not updated:
            self.update_files


    def update_files(self):
        """Update matches files"""
        pages = self.get_matches()
        details = self.get_matches_details(pages)
        self.record_new_matches(details)


    def get_matches(self):
        """Return DataFrame with matches and record JSON file

        Key arguments:

        """
        pass


    def get_matches_details(self, pages):
        """Return DataFrame with details of matches and record JSON file

        Key arguments:

        """
        pass


    def record_new_matches(self, details):
        """Add new data to files"""
        pass
