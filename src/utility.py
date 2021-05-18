"""
VVVVID Downloader - Utility Functions
Author: CoffeeStraw
GitHub: https://github.com/CoffeeStraw/VVVVID-Downloader
"""
import re
import os
import sys
import subprocess
from tqdm import tqdm
from platform import system
from functools import reduce


def os_fix_filename(filename):
    """Alter filenames containing illegal characters, depending on the OS.

    Ref: https://stackoverflow.com/questions/1976007/what-characters-are-forbidden-in-windows-and-linux-directory-names/31976060#31976060
    """
    if system() == "Windows":
        filename = re.sub(r"[\<\>\:\"\/\\\|\?\*]+", "", filename)
    else:
        filename = re.sub(r"[\/]+", r"\\", filename)
    return filename.replace("%", "%%")


class ProgressBar:
    """ProgressBar using tqdm to visualize ffmpeg's outputs."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.tqdm_pbar is not None:
            self.tqdm_pbar.close()

    def __init__(self):
        # e.g.: "Duration: 00:29:25.23, start: 0.100667, bitrate: 0 kb/s"
        self._INPUT_INFO_REGEX = re.compile(r"Duration: (\d\d):(\d\d):(\d\d)\.\d\d")
        # e.g.: "frame=  250 fps=0.0 q=-1.0 size=    1024kB time=00:00:09.98 bitrate= 840.2kbits/s speed=14.9x"
        self._PROGRESS_REGEX = re.compile(
            r"size=\s*?(\d+)(\D+?)\s+?time=(\d\d):(\d\d):(\d\d).\d\d\s*?bitrate=\s*?([\d|\.]+)(\D+?) speed"
        )
        self.total_time = None
        self.tqdm_pbar = None

    @staticmethod
    def hms_to_s(hms):
        return reduce(lambda x, y: x * 60 + y, [int(i) for i in hms])

    def update(self, line):
        # Do we have total time?
        if not self.total_time:
            info = self._INPUT_INFO_REGEX.search(line)
            if info:
                self.total_time = self.hms_to_s(info.groups())
                self.tqdm_pbar = tqdm(
                    total=self.total_time,
                    desc="Size: 0 kB",
                    unit="0.0 kbit/s",
                    bar_format="{percentage:3.0f}% |{bar}| {desc} [{unit}] [{elapsed}, ETA: {remaining}]",
                )

            return None

        # Do we have an update?
        progress = self._PROGRESS_REGEX.search(line)
        if progress:
            progress = progress.groups()

            # Update filesize (in MB if possible)
            if progress[1] == "kB":
                self.tqdm_pbar.desc = f"Size: {float(progress[0]) / 1024:.2f} MB"
            else:
                self.tqdm_pbar.desc = f"Size: {float(progress[0]):.2f} {progress[1]}"

            # Update speed (in MB/s if possible)
            if progress[6] == "kbits/s":
                self.tqdm_pbar.unit = f"{float(progress[5]) / 1024:.2f} MB/s"
            else:
                self.tqdm_pbar.unit = f"{float(progress[5]):.2f} {progress[6]}"

            # Update progress bar
            current_time = self.hms_to_s(progress[2:5])
            self.tqdm_pbar.update(current_time - self.tqdm_pbar.n)


def ffmpeg_dl(media_url, http_headers, output_path, verbose=False):
    """Download a video using ffmpeg. If not verbose, it visualizes its outputs with a progress bar."""
    # Build command
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-y",
        "-loglevel",
        "verbose",
        "-headers",
        http_headers,
        "-i",
        media_url,
        "-c",
        "copy",
        "-bsf:a",
        "aac_adtstoasc",
        output_path,
    ]

    # Execute ffmpeg and visualize its outputs
    with subprocess.Popen(
        cmd, stderr=subprocess.PIPE, bufsize=1, text=True, encoding="utf-8"
    ) as p, ProgressBar() as pbar:
        for line in p.stderr:
            if verbose:
                print(line, end="")

            if "access denied" in line.lower():
                return "Il server ha rifiutato l'accesso al file. Si ricorda che con il presente software non è possibile scaricare contenuti a pagamento. Se pensi si tratti di un errore, puoi aprire una issue su GitHub."

            if not verbose:
                pbar.update(line)