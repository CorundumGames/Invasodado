'''
This module provides access to the configurations made in the game's Options
menu.  OBJECTS IN ALL CAPS are constants.
'''

from contextlib import closing
import shelve

### Constants ##################################################################
'''
@var LANGUAGES: Two-character language codes for internal identification.
@var LANGUAGE_NAMES: Tuple of language names in their respective languages.
@var LANGUAGE_DICT: Dictionary mapping LANGUAGES to LANGUAGE_NAMES
@var SETTINGS_KEYS: Internally-used names for settings types.
@var SETTINGS_FILE_NAME: Path to the file that contains the game's configuration.
'''
LANGUAGES          = (     'en',      'es')
LANGUAGE_NAMES     = ("English", "Español")
LANGUAGE_DICT      = dict(zip(LANGUAGES, LANGUAGE_NAMES))
SETTINGS_KEYS      = (
    'resolution'  ,
    'fullscreen'  ,
    'color_blind' ,
    'language'    ,
    'sound_volume',
    'music_volume',
)
SETTINGS_FILE_NAME = 'settings.wtf'
################################################################################

### Globals ####################################################################
'''
@var color_blind: True if we're playing the game in colorblind mode
@var fullscreen: True if we're playing the game in fullscreen mode
@var language_id: Ordinal ID for the languages
@var music_volume: Volume, from 0-1, of the music (0 is silent, 1 is max)
@var resolution: x and y resolution of the screen, in pixels
@var sound_volume: Volume, from 0-1, of the sound effects (0 is silent, 1 is max)
'''
color_blind  = False
fullscreen   = False
language_id  = 0
music_volume = 0.5
resolution   = (640, 480)
sound_volume = 0.5
################################################################################

### Functions ##################################################################
def toggle_color_blind_mode():
    '''
    Toggles color-blind mode on or off.
    '''
    global color_blind
    color_blind = not color_blind

def save_settings(path):
    '''
    Saves the game's settings to a file for loading in later sessions.
    
    @param path: The path to save the file to.
    '''
    with closing(shelve.open(path)) as settings_file:
    #Opening the settings file...
        for i, j in zip(SETTINGS_KEYS, (resolution, fullscreen, color_blind, sound_volume, music_volume)):
        #For each setting we have...
            settings_file[i] = j

def load_settings(path):
    '''
    Loads settings from a file, or does nothing if there is no file to load from.
    
    @param path: The path to load the file from.
    '''
    try:
    #Let's try and load the settings...
        with closing(shelve.open(path)) as settings_file:
        #Loading the settings file...
            for i in settings_file:
            #For each setting in the file...
                locals()[i] = settings_file[i]
    except:
    #Whoops, not found!
        return
    
def set_language(lang):
    '''
    Sets the language the game's text is displayed in.
    
    @param lang: The language to set the game to
    '''
    global language
    language = lang if lang in LANGUAGES else 'en'

def get_language_code():
    '''
    Get the language code of the current language.
    '''
    return LANGUAGES[language_id]

def get_language_name():
    '''
    Get the language name of the current language.
    '''
    return LANGUAGE_NAMES[language_id]
    
################################################################################
