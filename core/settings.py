'''
This module provides access to the configurations made in the game's Options
menu.  OBJECTS IN ALL CAPS are constants.
'''

from contextlib import closing
import shelve

SETTINGS_KEYS = ('resolution', 'fullscreen', 'color_blind', 'sound_volume', 'music_volume')
SETTINGS_FILE_NAME = 'settings.wtf'

#The current screen settings.
resolution = (640, 480)

#Whether we're currently in fullscreen mode.
fullscreen = False

#Whether colorblind mode is enabled.
color_blind = False

sound_volume = 0.5

music_volume = 0.5


def save_settings(path):
    with closing(shelve.open(path)) as settings_file:
        for i, j in zip(SETTINGS_KEYS, [resolution, fullscreen, color_blind, sound_volume, music_volume]):
            settings_file[i] = j

def load_settings(path):
    try:
        with closing(shelve.open(path)) as settings_file:
            for i in settings_file:
                locals()[i] = settings_file[i]
    except:
        return