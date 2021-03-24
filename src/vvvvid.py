"""
VVVVID Downloader - VVVVID Utility Functions
Author: CoffeeStraw
GitHub: https://github.com/CoffeeStraw/VVVVID-Downloader
"""
import re
import sys
from copy import deepcopy
from colorama import Fore, Back, Style


def parse_url(url):
    """
    Parse a given link to extract show_id and content name (url formatted)
    """
    # Parsing URL (and checks validity)
    pattern = r"show/([0-9]+)/"
    res = re.search(pattern, url)
    if not res:
        print(
            f'{Fore.RED}[ERRORE]{Style.RESET_ALL} L\'URL fornito ("{url}") non è valido. Si prega di controllarlo e riprovare.'
        )
        sys.exit(-1)
    return res.group(1)


def get_content_infos(requests_obj, show_id):
    """
    Retrieves some informations for the content to beautify output,
    specifically description and well formatted name
    """
    infos_url = "https://www.vvvvid.it/vvvvid/ondemand/" + show_id + "/info/"
    json_file = (
        requests_obj["session"]
        .get(infos_url, headers=requests_obj["headers"], params=requests_obj["payload"])
        .json()
    )

    return json_file["data"]["title"], json_file["data"]["description"]


def get_seasons(requests_obj, url, show_id):
    """
    Returns a dictionary containing seasons with url
    """
    # Downloading episodes informations
    json_file = (
        requests_obj["session"]
        .get(
            "https://www.vvvvid.it/vvvvid/ondemand/" + show_id + "/seasons/",
            headers=requests_obj["headers"],
            params=requests_obj["payload"],
        )
        .json()
    )

    if json_file["result"] == "error":
        print(
            f'{Fore.RED}[ERRORE]{Style.RESET_ALL} L\'URL fornito ("{url}") non è valido. Si prega di controllarlo e riprovare.'
        )
        sys.exit(-1)

    # Extracting seasons from json
    seasons = {}
    for season in json_file["data"]:
        seasons[str(season["season_id"])] = {
            "name": season["name"],
            "episodes": season["episodes"],
        }

    # Check if the link is a link to a single episode.
    # If it is, then return only a single season with episodes starting from the selected one
    pattern = f"show/{show_id}/" + r".+?/(.+?)/(.+?)/.*"
    additional_infos = re.search(pattern, url)

    if additional_infos:
        season_id, episode_id = additional_infos.groups()

        seasons = {season_id: seasons[season_id]}
        episodes = deepcopy(seasons[season_id]["episodes"])

        for e in episodes:
            if str(e["video_id"]) != episode_id:
                del seasons[season_id]["episodes"][0]
            else:
                break

    return seasons
