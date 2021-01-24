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
from colorama import Fore, Back, Style

import requests
from youtube_dl import YoutubeDL

import vvvvid_scraper
from utility import os_fix_filename

# Defining Download folder
current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
dl_dir = os.path.join(current_dir, "Downloads")


def dl_from_vvvvid(url, requests_obj, ffmpeg_local=""):
    """
    General function to process a given link from
    vvvvid website and start the download
    """
    # Retrieving datas about the given url
    show_id, url_name = vvvvid_scraper.parse_url(url)
    seasons = vvvvid_scraper.get_seasons(requests_obj, url, show_id, url_name)
    cont_title, cont_description = vvvvid_scraper.get_content_infos(
        requests_obj, show_id
    )

    # Printing content informations to the user
    print(
        "%sIn preparazione: %s\n%sDescrizione:     %s"
        % (
            Style.BRIGHT,
            Back.BLACK + Fore.WHITE + cont_title,
            Style.RESET_ALL + Style.BRIGHT,
            cont_description,
        )
    )

    # Iterate over the seasons obtained from the url in the txt
    for season_id, season in seasons.items():
        # Creating content directory if not existing
        content_dir = os.path.join(
            dl_dir, os_fix_filename(cont_title + " - " + season["name"])
        ).replace("%", "%%")
        if not os.path.exists(content_dir):
            os.makedirs(content_dir)

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
                    "\nL'episodio %s non è stato ancora reso disponibile.%s Lo sarà il: %s"
                    % (episode["number"], Style.BRIGHT, episode["availability_date"])
                )
                break

            # Build episode name
            ep_name = os_fix_filename(
                "%s - %s" % (episode["number"], episode["title"])
            ).replace("%", "%%")

            # If episode is already downloaded, skip it
            if ep_name in episodes_downloaded:
                print(
                    "\nEpisodio %s: %s già scaricato"
                    % (episode["number"], episode["title"] + Fore.YELLOW)
                )
                continue

            # Build url
            ep_url = "https://www.vvvvid.it/show/%s/%s/%s/%s/%s" % (
                show_id,
                url_name,
                season_id,
                episode["video_id"],
                vvvvid_scraper.convert_text_to_url_format(episode["title"]),
            )

            # Preparing options for youtube-dl
            ydl_opts = {
                "format": "best",
                "outtmpl": "%s/%s.%%(ext)s" % (content_dir, ep_name),
                "continuedl": True,
            }

            # If the script is running either from Windows or Mac, get ffmpeg locally if not available
            if ffmpeg_local:
                ydl_opts["ffmpeg_location"] = ffmpeg_local

            # Print information to the user: the episode is ready to be downloaded
            print(
                "\n%sEpisodio %s: %s%s - %sscaricando\n"
                % (
                    Style.BRIGHT,
                    episode["number"],
                    Style.RESET_ALL,
                    episode["title"],
                    Fore.GREEN,
                )
            )

            # Start to download the selected file
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([ep_url])


def sig_handler(_signo, _stack_frame):
    """Prints a goodbye message to the user before quitting program."""
    print(
        f"\n{Fore.RED}[Interrupt Handler]{Style.RESET_ALL} Esecuzione programma interrotta"
    )
    sys.exit(0)


def main():
    # Getting Colorama utility ready to work
    colorama_init(autoreset=True)

    # Set handler functions for SIGTERM and SIGINT
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # Printing warning if on Windows
    if system() == "Windows":
        print(
            Style.BRIGHT
            + "Nota Bene: "
            + Style.RESET_ALL
            + "siccome lo script è stato lanciato da Windows i nomi delle cartelle e dei file potrebbero subire delle variazioni.\n"
        )
    
    # Creating persistent session
    current_session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
    }

    # Getting conn_id token from vvvvid and putting it into a payload
    login_res = current_session.get("https://www.vvvvid.it/user/login", headers=headers)
    if "error" in login_res.text.lower():
        print(
            f"{Fore.RED}[ERROR]{Style.RESET_ALL} VVVVID è attualmente in manutenzione, controllare il suo stato sul sito e riprovare."
        )
        sys.exit(-1)
    conn_id = { "conn_id": login_res.json()["data"]["conn_id"] }

    # Creating requests object
    requests_obj = {"session": current_session, "headers": headers, "payload": conn_id}

    # Check if ffmpeg is available in PATH
    ffmpeg_local = ""
    if which("ffmpeg") is None:
        # If the user is running the script from Windows or Mac, ffmpeg's build can be inside dependency folder
        if system() in ["Windows", "Darwin"]:
            if os.path.isfile(os.path.join(current_dir, "ffmpeg", ".DS_Store")):
                os.remove(os.path.join(current_dir, "ffmpeg", ".DS_Store"))
            ffmpeg_dir_files = os.listdir(os.path.join(current_dir, "ffmpeg"))
            ffmpeg_dir_files.remove("readme.md")

            # If the directory is ambiguous stop the script
            if len(ffmpeg_dir_files) > 1:
                print(
                    "La tua directory di ffmpeg contiene troppi file/cartelle. Assicurati che contenga solo il readme e la cartella con la build di ffmpeg."
                )
                quit()
            elif len(ffmpeg_dir_files) == 0:
                print(
                    "Questo script ha una dipendenza da ffmpeg, che non risulta essere installato. Per maggiori informazioni, consulta il readme sulla pagina GitHub del progetto."
                )
                quit()

            ffmpeg_local = os.path.join(
                current_dir, "ffmpeg", ffmpeg_dir_files[0], "bin"
            )
        else:
            print(
                "Questo script ha una dipendenza da ffmpeg, che non risulta essere installato. Per maggiori informazioni, consulta il readme sulla pagina GitHub del progetto, nella sezione installazione per Ubuntu."
            )
            quit()

    # Get anime list from local file, ignoring commented lines and empty lines
    with open("downloads_list.txt", "r") as f:
        for line in f:
            line = line.strip() + "/"
            if not line.startswith("#") and line != "/":
                dl_from_vvvvid(line, requests_obj, ffmpeg_local)


if __name__ == "__main__":
    main()
