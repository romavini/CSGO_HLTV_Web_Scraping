import json
import os
import pandas as pd
from time import sleep
from typing import Dict, List
from selenium.webdriver import Chrome
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
)


class ExtractDetails:
    def __init__(self, browser):
        self.browser = browser

        self.to_close = False
        self.filename = "total_details.json"

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

    def get_pages(self, data: pd.DataFrame):
        """Return a list with matches url"""
        return list(data["match_url"])

    def get_date(self):
        """Return the date in the top of the page"""
        return {
            "date": self.browser.find_element_by_class_name("date").text,
            "time": self.browser.find_element_by_class_name("time").text,
        }

    def get_flexbox(self) -> Dict[str, str]:
        """Return Dict with teamnames, total scores, scores per side,
        mapnames and sides
        """
        flexbox_dict = {}

        box = self.browser.find_element_by_class_name("flexbox-column")

        # Team names
        team_names = box.find_elements_by_class_name("results-teamname")
        flexbox_dict["first_team"] = team_names[0].text
        flexbox_dict["second_team"] = team_names[1].text

        ranks = self.browser.find_elements_by_class_name("teamRanking")

        for idx_rank, rank in enumerate(ranks):
            rank_value = rank.get_attribute("textContent").split("#")[-1]
            try:
                rank_value = int(rank_value)

            except ValueError:
                rank_value = rank_value.split("\n")[1].lstrip().rstrip()

            flexbox_dict[
                f"{['first','second'][idx_rank]}_team_world_rank_#"
            ] = rank_value

        # Total Score
        t1 = self.browser.find_element_by_class_name("team1-gradient")
        flexbox_dict["first_team_total_score"] = int(
            t1.get_attribute("textContent").split("\n")[-2]
        )
        t2 = self.browser.find_element_by_class_name("team2-gradient")
        flexbox_dict["second_team_total_score"] = int(
            t2.get_attribute("textContent").split("\n")[-2]
        )

        if (
            flexbox_dict["first_team_total_score"]
            > flexbox_dict["second_team_total_score"]
        ):
            flexbox_dict["first_team_won"] = 1
        else:
            flexbox_dict["first_team_won"] = 0

        # Scores and Maps
        maps = box.find_elements_by_class_name("mapname")
        scores = box.find_elements_by_class_name("results-team-score")

        flexbox_dict["M1"] = maps[0].text
        flexbox_dict["first_team_score_M1"] = scores[0].text
        flexbox_dict["second_team_score_M1"] = scores[1].text

        flexbox_dict["M2"] = maps[1].text
        flexbox_dict["first_team_score_M2"] = scores[2].text
        flexbox_dict["second_team_score_M2"] = scores[3].text

        flexbox_dict["M3"] = maps[2].text
        flexbox_dict["first_team_score_M3"] = scores[4].text
        flexbox_dict["second_team_score_M3"] = scores[5].text

        flexbox_dict = self.get_sides(box, flexbox_dict)

        return flexbox_dict

    def get_sides(self, box, flexbox_dict: Dict[str, str]) -> Dict[str, str]:
        """Return the side played by each team"""
        sides = box.find_elements_by_class_name("results-center-half-score")

        for idx, side in enumerate(sides):
            ct = int(side.find_element_by_class_name("ct").text)
            score_first_team = int(side.text.strip("(").split(";")[0].split(":")[0])
            if ct == score_first_team:
                flexbox_dict[f"side_first_team_M{idx+1}"] = "CT"
                flexbox_dict[f"side_second_team_M{idx+1}"] = "T"
            else:
                flexbox_dict[f"side_first_team_M{idx+1}"] = "T"
                flexbox_dict[f"side_second_team_M{idx+1}"] = "CT"

            scores = side.text.split("(")[1]
            scores = scores.split(":")
            flexbox_dict[f"score_first_team_t1_M{idx+1}"] = scores[0]
            flexbox_dict[f"score_first_team_t2_M{idx+1}"] = scores[1].split("; ")[1]
            flexbox_dict[f"score_second_team_t1_M{idx+1}"] = scores[1].split("; ")[0]
            flexbox_dict[f"score_second_team_t2_M{idx+1}"] = scores[-1].strip(")")[0]

        if len(sides) < 3:
            flexbox_dict["side_first_team_M3"] = "-"
            flexbox_dict["side_second_team_M3"] = "-"
            flexbox_dict["score_first_team_t1_M3"] = "-"
            flexbox_dict["score_first_team_t2_M3"] = "-"
            flexbox_dict["score_second_team_t1_M3"] = "-"
            flexbox_dict["score_second_team_t2_M3"] = "-"

        return flexbox_dict

    def get_picks_bans(self, first_team: str) -> Dict[str, int]:
        """Return picks and bans"""
        picks_bans_dict = {}

        lcolumn = self.browser.find_element_by_class_name("col-6")
        picks_bans = lcolumn.find_elements_by_class_name("padding")[1]
        picks_bans = picks_bans.text.split("\n")

        first_ban = picks_bans[0].split(".")[-1].lstrip().split(" ")[0].lower()

        if first_ban == first_team.lower():
            picks_bans_dict["first_pick_by_first_team"] = 1
        else:
            picks_bans_dict["first_pick_by_first_team"] = 0

        picks_bans_dict["ban 1"] = picks_bans[0].split(" ")[-1]
        picks_bans_dict["ban 2"] = picks_bans[1].split(" ")[-1]
        picks_bans_dict["pick 1"] = picks_bans[2].split(" ")[-1]
        picks_bans_dict["pick 2"] = picks_bans[3].split(" ")[-1]
        picks_bans_dict["ban 3"] = picks_bans[4].split(" ")[-1]
        picks_bans_dict["ban 4"] = picks_bans[5].split(" ")[-1]
        picks_bans_dict["pick 3"] = picks_bans[6].split(" ")[1]

        return picks_bans_dict

    def get_stats(
        self, lineup_dict: Dict[str, str], idx_team: int, idx_player: int
    ) -> Dict[str, str]:
        """Return stats"""
        stats = self.browser.find_element_by_class_name("stats-content")
        tables = stats.find_elements_by_class_name("table")

        if idx_team == 0:
            tables = tables[1:3]
        else:
            tables = tables[4:]

        nicks_element = tables[0].find_elements_by_xpath(
            './/span[@class="player-nick"]'
        )
        nicks = [
            n.get_attribute("textContent").lstrip().rstrip() for n in nicks_element
        ]

        lineup_dict[f"{['first','second'][idx_team]}_team_P{idx_player+1}"] = nicks[
            idx_player
        ]

        for tab_idx, table in enumerate(tables):
            nicks_element = table.find_elements_by_xpath(
                './/span[@class="player-nick"]'
            )
            nicks = [
                n.get_attribute("textContent").lstrip().rstrip() for n in nicks_element
            ]

            # Locate Player
            nicks_idx_locate = nicks.index(
                lineup_dict[f"{['first','second'][idx_team]}_team_P{idx_player+1}"]
            )

            # Kills - Deaths
            kds = table.find_elements_by_class_name("kd")
            del kds[0]
            lineup_dict[
                f"{['first','second'][idx_team]}_team_P{idx_player+1}_"
                + f"{['CT','T'][tab_idx]}_KD"
            ] = kds[nicks_idx_locate].get_attribute("textContent")

            # +/-
            plus_minus = table.find_elements_by_class_name("plus-minus")
            del plus_minus[0]
            lineup_dict[
                f"{['first','second'][idx_team]}_team_P{idx_player+1}_"
                + f"{['CT','T'][tab_idx]}_+/-"
            ] = plus_minus[nicks_idx_locate].get_attribute("textContent")

            # ADR
            adr = table.find_elements_by_class_name("adr")
            del adr[0]
            lineup_dict[
                f"{['first','second'][idx_team]}_team_P{idx_player+1}_"
                + f"{['CT','T'][tab_idx]}_ADR"
            ] = adr[nicks_idx_locate].get_attribute("textContent")

            # Kast
            kast = table.find_elements_by_class_name("kast")
            del kast[0]
            lineup_dict[
                f"{['first','second'][idx_team]}_team_P{idx_player+1}_"
                + f"{['CT','T'][tab_idx]}_Kast"
            ] = kast[nicks_idx_locate].get_attribute("textContent")

            # Rating
            rating = table.find_elements_by_class_name("rating")
            del rating[0]
            lineup_dict[
                f"{['first','second'][idx_team]}_team_P{idx_player+1}_"
                + f"{['CT','T'][tab_idx]}_Rating"
            ] = rating[nicks_idx_locate].get_attribute("textContent")

        return lineup_dict

    def get_lineup(self) -> Dict[str, str]:
        """Return lineups, player names and stats"""
        lineup_dict = {}  # type: ignore

        # Lineup
        lu = self.browser.find_element_by_class_name("lineups")
        lineups = lu.find_elements_by_class_name("players")

        for idx_team, lineup in enumerate(lineups):
            players = lineup.find_elements_by_class_name("text-ellipsis")

            for idx_player in range(len(players)):
                lineup_dict = self.get_stats(lineup_dict, idx_team, idx_player)

        return lineup_dict

    def get_details(self, url_list: List, details: List):
        """Return details from the page"""
        for url in url_list:
            try:
                details_dict = {}
                self.browser.get(url)
                sleep(1)
                date_dict = self.get_date()
                flexbox_dict = self.get_flexbox()
                lineup_dict = self.get_lineup()
                picks_bans_dict = self.get_picks_bans(flexbox_dict["first_team"])

                details_dict = {
                    **date_dict,
                    **flexbox_dict,
                    **lineup_dict,
                    **picks_bans_dict,
                }
                details_dict["url"] = url
                details.append(details_dict)

            except KeyboardInterrupt:
                self.print_message("KeyboardInterrupt", "Saving data", "e")
                self.to_close = True

                return details

            except NoSuchElementException:
                self.print_message(
                    "NoSuchElementException",
                    f"Match disregarded for missing data.ulr: {url}",
                    "n",
                )

            except IndexError:
                self.print_message(
                    "IndexError",
                    f"Match disregarded for missing data.ulr: {url}",
                    "n",
                )

            except WebDriverException:
                self.print_message(
                    "WebDriverException",
                    f"Match disregarded for missing data.ulr: {url}",
                    "n",
                )

        return details

    def fix_data(self):
        with open(f"datacs/{self.filename}", "r") as f:
            d = f.read()

        if d[-4] == ",":
            d = d.strip(",\n]\n") + "\n]\n"
            self.print_message("Data fixed!", "Error found and fixed", "s")
        else:
            self.print_message("Error!", "Problem in Data not found", "e")

        with open(f"datacs/{self.filename}", "w") as f:
            f.write(d)

    def check_duplicates(self, url_list):
        if not (self.filename in os.listdir("datacs/")):
            return url_list

        else:
            try:
                data = pd.read_json("datacs/" + self.filename)
            except ValueError:
                self.print_message("ValueError", "Trying to fix data", "e")
                self.fix_data()
                data = pd.read_json("datacs/" + self.filename)

            url_list = list(set(url_list) - set(data["url"].tolist()))

        return url_list

    def write_file(self, details):
        """Write collected results in JSON file"""
        if not (self.filename in os.listdir("datacs/")):
            with open(
                f"datacs/{self.filename}",
                "w",
            ) as f:
                f.write("[")
                for i in range(len(details)):
                    json.dump(details[i], f)
                    if i < len(details) - 1:
                        f.write(",\n")
                    else:
                        f.write("\n")
                f.write("]\n")

            self.print_message("Success", "All matches have been saved", "s")

        else:
            with open(
                f"datacs/{self.filename}",
                "r",
            ) as f:
                data = f.read()

            with open(
                f"datacs/{self.filename}",
                "w",
            ) as f:
                f.write("[")
                f.write(data.strip("[").strip("\n]"))
                f.write(",\n")
                for i in range(len(details)):
                    json.dump(details[i], f)
                    if i < len(details) - 1:
                        f.write(",\n")
                    else:
                        f.write("\n")
                f.write("]\n")

            self.print_message("Success", "All matches have been saved", "s")

    def extract_players(self, url_list):
        """Return player details for each match"""
        details = []
        url_list = self.check_duplicates(url_list)

        if len(url_list) != 0:
            details = self.get_details(url_list, details)
            self.write_file(details)

        return self.to_close


if __name__ == "__main__":
    browser = Chrome()
    ext_details = ExtractDetails(browser)

    data = pd.read_csv("HTLV_results.csv", sep=";", index_col=0)
    ext_details.extract_players(list(data[data["type_of_match"] == "bo3"]["match_url"]))
