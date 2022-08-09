"""
VVVVID Downloader - VVVVID Utility Functions
Author: CoffeeStraw
GitHub: https://github.com/CoffeeStraw/VVVVID-Downloader
"""
import re
import sys
import requests
from colorama import Fore, Style


def get_requests_obj():
    """Create a dictionary to manage a persistent session with the connection ID from VVVVID"""

    # Creating persistent session
    current_session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
    }

    # Getting conn_id token from vvvvid and putting it into a payload
    login_res = current_session.get("https://www.vvvvid.it/user/login", headers=headers)
    login_res_text = login_res.text.lower()

    if "error" in login_res_text:
        print(
            f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} VVVVID è attualmente in manutenzione, controllare il suo stato sul sito e riprovare."
        )
        sys.exit(-1)
    if "access denied" in login_res_text:
        print(
            f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} VVVVID è accessibile solo in Italia 🍕 \n\n... Pss, puoi usare una VPN 😏"
        )
        sys.exit(-1)

    conn_id = {"conn_id": login_res.json()["data"]["conn_id"]}

    # Creating requests object
    return {"session": current_session, "headers": headers, "payload": conn_id}


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
    infos_url = f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/info/"
    json_file = (
        requests_obj["session"]
        .get(infos_url, headers=requests_obj["headers"], params=requests_obj["payload"])
        .json()
    )

    return json_file["data"]["title"], json_file["data"]["description"]


def get_seasons(requests_obj, url, show_id, args):
    """
    Returns a dictionary containing seasons with url
    """
    # Downloading episodes informations
    json_file = (
        requests_obj["session"]
        .get(
            f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/seasons/",
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

    if args.verbose:
        print(json_file)

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

        for _ in range(len(seasons[season_id]["episodes"])):
            curr_ep = seasons[season_id]["episodes"][0]
            if str(curr_ep["video_id"]) != episode_id:
                del seasons[season_id]["episodes"][0]
            else:
                break

    # Check for invalid episodes and delete them (atm of writing, only "lives" are considered invalid)
    for season_id in list(seasons.keys()):
        for i in range(len(seasons[season_id]["episodes"]) - 1, -1, -1):
            if "live" in seasons[season_id]["episodes"][i]:
                del seasons[season_id]["episodes"][i]

        # Check if current season has any episode left
        if not len(seasons[season_id]["episodes"]):
            del seasons[season_id]

    return seasons


def get_subtitle(requests_obj, season_id, show_id, video_id):
    """
    Returns the link to the subtitle file, if exists, of a given episode 
    """
    json_file = (
        requests_obj["session"]
        .get(
            f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/season/{season_id}?video_id={video_id}",
            headers=requests_obj["headers"],
            params=requests_obj["payload"],
        )
        .json()
    )

    subtitles = json_file["data"][0]
    if "subtitles" not in subtitles:
        return None

    return [s["url"] for s in subtitles["subtitles"]]