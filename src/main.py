"""
VVVVID Downloader - Main
Author: CoffeeStraw
GitHub: https://github.com/CoffeeStraw/VVVVID-Downloader
"""
import os
import sys
import signal
from shutil import which
from platform import system

from colorama import init as colorama_init
from colorama import Fore, Style

import requests
from youtube_dl import YoutubeDL

import vvvvid
from utility import os_fix_filename, ffmpeg_dl

# Defining paths
current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # If executed on Windows release, we get current directory differently
    current_dir = os.path.dirname(os.getcwd())

dl_list_path = os.path.join(current_dir, "downloads_list.txt")
dl_path = os.path.join(current_dir, "Downloads")


def dl_from_vvvvid(url, requests_obj):
    """
    General function to process a given link from
    vvvvid website and start the download
    """
    # Retrieving datas about the given url
    show_id = vvvvid.parse_url(url)
    seasons = vvvvid.get_seasons(requests_obj, url, show_id)
    cont_title, cont_description = vvvvid.get_content_infos(requests_obj, show_id)

    # Printing content informations to the user
    print(
        f"\n{Style.BRIGHT}In preparazione: {Fore.BLUE + cont_title + Style.RESET_ALL}\n"
        + f"{Style.BRIGHT}Descrizione:     {Style.RESET_ALL + cont_description}"
    )

    # Check for empty seasons
    if not seasons:
        print(
            f'\n{Fore.YELLOW}[WARNING]{Style.RESET_ALL} L\'URL fornito ("{url}") non contiene alcun episodio scaricabile.\n'
            + "Si prega di controllarlo e riprovare.\n"
        )

    # Iterate over the seasons obtained from the url in the txt
    for season_id, season in seasons.items():
        print(f"\n{Style.BRIGHT}Stagione: {Fore.BLUE + season['name']}")

        # Creating content directory if not existing
        content_dir = os.path.join(
            dl_path, os_fix_filename(f'{cont_title} - {season["name"]}')
        )
        if not os.path.exists(content_dir):
            os.mkdir(content_dir)

        # Checking episodes downloaded to accelerate a little bit youtube-dl checks
        episodes_downloaded = []
        for episode in os.listdir(content_dir):
            if ".part" not in episode:
                episodes_downloaded.append(os.path.splitext(episode)[0])

        # Iterate over the episodes in the season
        for episode in season["episodes"]:
            # Check if episode is public released
            if not episode["playable"]:
                print(
                    f"- {Style.BRIGHT}Episodio {episode['number']}: {Style.RESET_ALL + Fore.RED} non ancora disponibile. "
                    + f"{Style.RESET_ALL}Lo sarà il: {episode['availability_date']}"
                )
                continue

            # Build episode name
            ep_name = os_fix_filename(f"{episode['number']} - {episode['title']}")

            # If episode is already downloaded, skip it
            if ep_name in episodes_downloaded:
                print(
                    f"- {Style.BRIGHT}Episodio {episode['number']}: {Style.RESET_ALL + episode['title'] + Fore.YELLOW} già scaricato"
                )
                continue

            # Build url
            ep_url = "https://www.vvvvid.it/show/%s/0/%s/%s/0" % (
                show_id,
                season_id,
                episode["video_id"],
            )

            # Print information to the user: the episode is ready to be downloaded
            print(
                f"- {Style.BRIGHT}Episodio {episode['number']}: {Style.RESET_ALL + episode['title']} {Fore.GREEN}in download"
            )

            # Get m3u8 link and HTTP headers
            with YoutubeDL({"quiet": True}) as ydl:
                r = ydl.extract_info(ep_url, download=False)

                media_url = r["url"]
                http_headers = "".join(
                    [f"{k}: {v}\n" for k, v in r["http_headers"].items()]
                )

            # Download the episode using ffmpeg
            ffmpeg_dl(
                media_url,
                http_headers,
                os.path.join(content_dir, f"{ep_name}.part.mkv"),
            )

            # Remove ".part" from end of file
            os.rename(
                os.path.join(content_dir, f"{ep_name}.part.mkv"),
                os.path.join(content_dir, f"{ep_name}.mkv"),
            )


def sig_handler(_signo, _stack_frame):
    """Prints a goodbye message to the user before quitting program."""
    print(
        f"\n\n{Fore.RED}[Interrupt Handler]{Style.RESET_ALL} Esecuzione programma interrotta\n"
    )
    sys.exit(0)


def main():
    # Getting Colorama utility ready to work
    colorama_init(autoreset=True)

    # Set handler functions for SIGTERM and SIGINT
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # Create downloads_list and Downloads folder (if missing)
    if not os.path.exists(dl_list_path):
        open(dl_list_path, "a").close()
        print(
            f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} "
            + "Il file downloads_list non era presente ed è stato creato.\n"
            + "Per cominciare ad usare il programma, inserire uno o più link.\n\n"
            + "Per ulteriori informazioni visitate la pagina ufficiale del progetto su GitHub:\nhttps://github.com/CoffeeStraw/VVVVID-Downloader.\n"
        )
        sys.exit(0)
    if not os.path.exists(dl_path):
        os.mkdir(dl_path)

    # Printing warning if on Windows
    if system() == "Windows":
        print(
            f"{Fore.YELLOW}NOTA BENE:{Style.RESET_ALL} "
            + "siccome lo script è stato lanciato da Windows i nomi delle cartelle e dei file creati potrebbero subire delle variazioni."
        )

    # Creating persistent session
    current_session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
    }

    # Getting conn_id token from vvvvid and putting it into a payload
    login_res = current_session.get("https://www.vvvvid.it/user/login", headers=headers)
    login_res_text = login_res.text.lower()

    # Check for errors
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
    requests_obj = {"session": current_session, "headers": headers, "payload": conn_id}

    # Get anime list from local file, ignoring commented lines and empty lines
    with open(dl_list_path, "r") as f:
        at_least_one = False
        for line in f:
            line = line.strip() + "/"
            if not line.startswith("#") and line != "/":
                dl_from_vvvvid(line, requests_obj)
                at_least_one = True

    if not at_least_one:
        print(
            f"\n{Fore.YELLOW}[WARNING]{Style.RESET_ALL} "
            + "Il file downloads_list è vuoto oppure contiene solo righe commentate.\n"
            + "Per cominciare ad usare il programma, inserire uno o più link.\n\n"
            + "Per ulteriori informazioni visitate la pagina ufficiale del progetto su GitHub:\nhttps://github.com/CoffeeStraw/VVVVID-Downloader.\n"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
