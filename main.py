'''
VVVVID Downloader - VVVVID Scraper
Author: CoffeeStraw (clarantonio98@gmail.com)
'''

from platform import system
import os
import re
import requests
import youtube_dl
import copy

import colorama
from colorama import Fore, Back, Style

# Current Directory
dl_dir = os.path.dirname(os.path.realpath(__file__)) + "/Downloads/"

# Getting Colorama utility ready to work
colorama.init(autoreset=True)

# Starting...
if system() == 'Windows':
	print(Style.BRIGHT + "Attenzione, siccome lo script è stato lanciato da Windows i nomi delle cartelle e dei file potrebbero subire delle variazioni")

print(Style.DIM + "Inizializzando VVVVID Downloader...\n")

# Creating persistent session
current_session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'}

# Getting conn_id token from vvvvvvvvvvid and creating payload
login_page = 'https://www.vvvvid.it/user/login'
conn_id = current_session.get(login_page, headers=headers).json()['data']['conn_id']
payload = {'conn_id': conn_id}

def get_data(URL):
	'''
	Returns a dictionary containing the infos to
	generate the url and a list of the episodes
	'''
	# Getting info from given URL
	pattern = "#!show/([0-9]+)/"
	show_id = re.findall(pattern, URL)[0]

	pattern = show_id + "/(.+?)/"
	name = re.findall(pattern, URL)[0]

	# Downloading Episodes informations
	json_url = "https://www.vvvvid.it/vvvvid/ondemand/" + show_id + "/seasons/"
	json_file = current_session.get(json_url, headers=headers, params=payload).json()

	seasons = []
	for i, season in enumerate(json_file['data']):
		seasons.append({'name': json_file['data'][i]['name'], 'season_id': json_file['data'][i]['season_id'], 'episodes': json_file['data'][i]['episodes']})

	data = {'show_id': show_id, 'name': name}

	# Checking if the link is a link to the episodes. If that is true, we modify seasons list
	pattern = name + "(.+)$"
	additional_infos = re.findall(pattern, URL)[0]

	if additional_infos != "/":
		stop = False
		additional_infos = re.findall("/(.+)/(.+)/(.+)/", additional_infos)[0]

		seasons_c = copy.deepcopy(seasons)
		for i, season in enumerate(seasons_c):
			if not stop and str(season['season_id']) == str(additional_infos[0]):
				for j, episode in enumerate(season['episodes']):
					if str(episode['video_id']) == str(additional_infos[1]):
						stop = True
						break
					else:
						del seasons[0]['episodes'][0]
			else:
				del seasons[0]

	return data, seasons

def get_infos(conn_id, show_id):
	'''
	Returns the infos of the anime
	'''
	infos_url = 'https://www.vvvvid.it/vvvvid/ondemand/' + show_id + '/info/'
	json_file = current_session.get(infos_url, headers=headers, params=payload).json()
	return json_file

def win_correct_name(text):
	'''
	Correct the title if the script is run from Microsoft OS
	'''
	if system() == 'Windows':
		text = re.sub(r'[\\\/\:\*\?\"\<\>\|]+', '', text)
	return text

def convert_title(text):
	'''
	Format a title correctly for the url
	'''
	text = re.sub(r'[^a-zA-Zàèéìòù\s\-\']', '', text)

	text = text.replace("à","a")
	text = re.sub("è|é", "e", text)
	text = text.replace("ì","i")
	text = text.replace("ò","o")
	text = text.replace("ù","u")

	text = re.sub(r'[\s\']+', '-', text)
	return text.lower()

# Reading animelist file to get all the links
with open("animelist.txt", 'r') as file:
	for URL in [line for line in file if not line.strip().startswith('#')]:
		anime_data, seasons = get_data(URL.strip() + "/")
		anime_info = get_infos(conn_id, anime_data['show_id'])

		print(Style.BRIGHT + "In preparazione: %s\n%sDescrizione: %s" % (
			Back.BLACK + Fore.WHITE + anime_info['data']['title'],
			Style.RESET_ALL + Style.BRIGHT,
			anime_info['data']['description']))

		for season in seasons:
			anime_dir = dl_dir + win_correct_name(anime_info['data']['title']) + " - " + season['name']

			# Preventing Directory not found error
			if not os.path.exists(anime_dir):
				os.makedirs(anime_dir)

			# Checking episodes downloaded to accelerate a little bit youtube-dl checks
			episode_downloaded = []
			for episode in os.listdir(anime_dir):
				if ".part" not in episode:
					episode_downloaded.append(os.path.splitext(episode)[0])

			for episode in season['episodes']:
				print()
				if not episode['playable']:
					print("L'episodio %s non è stato ancora reso disponibile.%s Lo sarà il: %s" % (
						episode['number'],
						Style.BRIGHT,
						episode['availability_date']))
					break

				ep_name = "%s - %s" % (episode['number'], episode['title'])

				if ep_name not in episode_downloaded:
					# Constructing url
					ep_url = "https://www.vvvvid.it/#!show/%s/%s/%s/%s/%s" % (
							anime_data['show_id'],
							anime_data['name'],
							season['season_id'],
							episode['video_id'],
							convert_title(episode['title']))

					ydl_opts = {
						'format': "best",
						'outtmpl': "%s/%s.%%(ext)s" % (anime_dir, ep_name),
						'continuedl': True,
					}

					print(Style.BRIGHT + "Episodio %s: %s - %sscaricando\n" % (
						episode['number'],
						episode['title'],
						Fore.GREEN))

					with youtube_dl.YoutubeDL(ydl_opts) as ydl:
					    ydl.download([ep_url])
				else:
					print("Episodio %s: %s già scaricato" % (
						episode['number'],
						episode['title'] + Fore.YELLOW))
