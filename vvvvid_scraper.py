'''
VVVVID Downloader - VVVVID Scraper Utility Functions
Author: CoffeeStraw
GitHub: https://github.com/CoffeeStraw/VVVVID-Downloader
'''
import re
from copy import deepcopy


def parse_url(url):
    '''
    Parse a given link to extract show_id and content name (url formatted)
    '''
    # Compatibility with old link format
    url = url.replace("/#!show/", '/show/')
    # Parsing URL
    pattern = r"show/([0-9]+)/(.+?)/"
    return re.search(pattern, url).groups()


def convert_text_to_url_format(text):
    '''
    Format a text correctly for the url concatenation
    '''
    text = re.sub(r'[^a-zA-Zàèéìòù\s\-\']', '', text)

    text = text.replace("à", "a")
    text = re.sub("è|é", "e", text)
    text = text.replace("ì", "i")
    text = text.replace("ò", "o")
    text = text.replace("ù", "u")

    text = re.sub(r'[\s\']+', '-', text)
    return text.lower()


def get_content_infos(requests_obj, show_id):
    '''
    Retrieves some informations for the content to beautify output,
    specifically description and well formatted name
    '''
    infos_url = 'https://www.vvvvid.it/vvvvid/ondemand/' + show_id + '/info/'
    json_file = requests_obj['session'].get(
        infos_url,
        headers=requests_obj['headers'],
        params=requests_obj['payload']
    ).json()

    return json_file['data']['title'], json_file['data']['description']


def get_seasons(requests_obj, url, show_id, url_name):
    '''
    Returns a dictionary containing seasons with url
    '''
    # Downloading episodes informations
    json_file = requests_obj['session'].get(
        "https://www.vvvvid.it/vvvvid/ondemand/" + show_id + "/seasons/",
        headers=requests_obj['headers'],
        params=requests_obj['payload']
    ).json()

    # Extracting seasons from json
    seasons = {}
    for i, season in enumerate(json_file['data']):
        seasons[str(json_file['data'][i]['season_id'])] = {
            'name': json_file['data'][i]['name'],
            'episodes': json_file['data'][i]['episodes']
        }

    # Check if the link is a link to a single episode.
    # If it is, then return only a single season with episodes starting from the selected one
    # IMPROVABLE? IT IS A DIRTY SOLUTION
    pattern = url_name + "(.+)$"
    additional_infos = re.findall(pattern, url)[0]

    if additional_infos != "/":
        stop = False
        additional_infos = re.findall("/(.+)/(.+)/(.+)/", additional_infos)[0]

        seasons_c = deepcopy(seasons)
        for season_id, season in seasons_c.items():
            if not stop and season_id == additional_infos[0]:
                for j, episode in enumerate(season['episodes']):
                    if str(episode['video_id']) == str(additional_infos[1]):
                        stop = True
                        break
                    else:
                        del seasons[season_id]['episodes'][0]
            else:
                del seasons[season_id]

    return seasons
