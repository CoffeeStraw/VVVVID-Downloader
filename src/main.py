"""
VVVVID Downloader - Main
Author: CoffeeStraw
GitHub: https://github.com/CoffeeStraw/VVVVID-Downloader
"""
import os
import sys
import signal
import argparse
import subprocess
from platform import system

from colorama import init as colorama_init
from colorama import Fore, Style

from youtube_dl import YoutubeDL

import vvvvid
from utility import os_fix_filename, ffmpeg_dl


def get_arguments():
    """Define and retrieve CLI options"""
    # Paths definition
    current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # If executed on Windows release, we get current directory differently
        current_dir = os.path.dirname(os.getcwd())

    batch_file = os.path.join(current_dir, "downloads_list.txt")
    output_dir = os.path.join(current_dir, "Downloads")

    # Arguments definition
    parser = argparse.ArgumentParser(
        description="Un piccolo script in Python3 per scaricare contenuti multimediali (non a pagamento) offerti da VVVVID.",
        epilog="Homepage del progetto: https://github.com/CoffeeStraw/VVVVID-Downloader",
        add_help=False,
    )
    parser.add_argument(
        "-f",
        "--batch-file",
        metavar="PATH",
        default=batch_file,
        help="file contenente gli URL da scaricare, un URL per riga (le righe che cominciano con il carattere '#' verranno ignorate)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        metavar="PATH",
        default=output_dir,
        help="cartella che conterrà i download",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="arricchisce i messaggi stampati a schermo con log utili al debugging",
    )
    parser.add_argument(
        "-h", "--help", action="help", help="mostra questa schermata di aiuto ed esce"
    )
    return parser.parse_args()


def dl_from_vvvvid(url, args):
    """
    General function to process a given link from
    vvvvid website and start the download
    """
    # Create a requests object to manage a persistent session with the connection ID from VVVVID
    requests_obj = vvvvid.get_requests_obj()

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
        dir_name = os_fix_filename(f'{cont_title} - {season["name"]}')
        content_dir = os.path.join(args.output_dir, dir_name)
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

            # Get m3u8 link and HTTP headers
            try:
                ydl_opts = (
                    {"verbose": True}
                    if args.verbose
                    else {
                        "quiet": True,
                        "no_warnings": True,
                        "ignoreerrors": True,
                        "logger": type(  # Create a class on-the-fly with three methods doing nothing, to suppress any youtube-dl output
                            "FakeLogger",
                            (object,),
                            {
                                **dict.fromkeys(
                                    ["warning", "error", "debug"], lambda x, y: None
                                )
                            },
                        )(),
                    }
                )

                with YoutubeDL(ydl_opts) as ydl:
                    infos = ydl.extract_info(ep_url, download=False)

                if args.verbose:
                    print(f"\n{infos}\n")

                infos = infos["formats"][-1]
                media_url = infos["url"]
                http_headers = "".join(
                    [f"{k}: {v}\n" for k, v in infos["http_headers"].items()]
                )
            except (TypeError, KeyError):
                print(
                    f"- {Style.BRIGHT}Episodio {episode['number']}: {Style.RESET_ALL + Fore.RED}il contenuto non è scaricabile.\n"
                    + f"{Style.RESET_ALL}È possibile che il contenuto venga fornito da un servizio esterno e/o abbia restrizioni sull'età. Il download verrà saltato."
                )
                continue

            # Print information to the user: the episode is ready to be downloaded
            print(
                f"- {Style.BRIGHT}Episodio {episode['number']}: {Style.RESET_ALL + episode['title']} {Fore.GREEN}in download"
            )

            # Download the episode using ffmpeg
            file_path = os.path.join(content_dir, ep_name)
            error = ffmpeg_dl(
                media_url,
                http_headers,
                os.path.join(content_dir, f"{ep_name}.part.mkv"),
                args.verbose,
            )
            if error:
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL}", error)
                continue

            # Get subtitles (if any)
            subtitles = vvvvid.get_subtitle(requests_obj, season_id, show_id, episode["video_id"])

            if subtitles:
                print(f"Aggiungo i sottotitoli al file...")
                content_dir = os.path.join(content_dir, "Sottotitoli")
                
                # Download every subtitle found
                for sub_url in subtitles:
                    r = requests_obj["session"].get(
                        sub_url,
                        headers=requests_obj["headers"],
                        params=requests_obj["payload"],
                    )
                    
                    sub_filename = sub_url.split("/")[-1]
                    sub_path = os.path.join(content_dir, sub_filename)
                    
                    if not os.path.exists(content_dir):
                        os.mkdir(content_dir)
                    open(sub_path, "wb").write(r.content)

                    # Merge subtitles and .mkv
                    mkvmerge_cmd = ["mkvmerge", "-o", f"{file_path}.part1.mkv", f"{file_path}.part.mkv", sub_path]
                    if args.verbose:
                        subprocess.run(mkvmerge_cmd)
                    else:
                        subprocess.run(mkvmerge_cmd, stdout=subprocess.DEVNULL)

                    os.rename(f"{file_path}.part1.mkv", f"{file_path}.part.mkv")

            # Remove ".part" from end of file
            os.rename(f"{file_path}.part.mkv", f"{file_path}.mkv")

        # It is possible that no episode has been downloaded for the season.
        # In that case, delete the folder as well.
        if not os.listdir(content_dir):
            print(
                f'\n{Fore.YELLOW}NOTA:{Style.RESET_ALL} Rimozione della cartella creata per "{dir_name}" (non è stato scaricato alcun contenuto).'
            )
            os.rmdir(content_dir)


def sig_handler(_signo, _stack_frame):
    """Prints a goodbye message to the user before quitting program."""
    print(
        f"\n\n{Fore.RED}[Interrupt Handler]{Style.RESET_ALL} Esecuzione programma interrotta\n"
    )
    sys.exit(0)


def main():
    # Getting Colorama utility ready to work
    colorama_init(autoreset=True)

    # Get possible CLI options
    args = get_arguments()

    # Set a pretty goodbye message for the exit
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # Create downloads_list.txt and Downloads folder (if missing)
    if not os.path.exists(args.batch_file):
        open(args.batch_file, "a").close()
        print(
            f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} "
            + "Il file downloads_list non era presente ed è stato creato.\n"
            + "Per cominciare ad usare il programma, inserire uno o più link.\n\n"
            + "Per ulteriori informazioni visitate la pagina ufficiale del progetto su GitHub:\nhttps://github.com/CoffeeStraw/VVVVID-Downloader.\n"
        )
        sys.exit(0)
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    # Printing warning if on Windows
    if system() == "Windows":
        print(
            f"{Fore.YELLOW}NOTA BENE:{Style.RESET_ALL} "
            + "siccome lo script è stato lanciato da Windows i nomi delle cartelle e dei file creati potrebbero subire delle variazioni."
        )

    # Get anime list from local file, ignoring commented lines and empty lines
    with open(args.batch_file, "r") as f:
        at_least_one = False
        for line in f:
            line = line.strip() + "/"
            if not line.startswith("#") and line != "/":
                dl_from_vvvvid(line, args)
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
