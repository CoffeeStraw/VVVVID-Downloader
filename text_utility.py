'''
VVVVID Downloader - Text Utility Functions
Author: CoffeeStraw
GitHub: https://github.com/CoffeeStraw/VVVVID-Downloader
'''
from platform import system
from re import sub as re_sub

def os_fix_filename(text):
	'''
	Correct the text if the script is running from Microsoft OS
	'''
	if system() == 'Windows':
		return re_sub(r'[\\\/\:\*\?\"\<\>\|]+', '', text)
	return text