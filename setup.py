from os import listdir
from os.path import join

from cx_Freeze import setup, Executable

includes     = [
                'dbm',
                'dbm.dumb',
                'dbm.gnu',
                'pygame._view',
                'pygame.display',
                'pygame.event',
                'pygame.mixer',
                'shelve',
                'zlib',
                ]
excludes     = [
                '__future__',
                '_codecs',
                '_codecs_cn',
                '_codecs_hk',
                '_codecs_iso2022',
                '_codecs_jp',
                '_codecs_kr',
                '_codecs_tw',
                '_json',
                '_lsprof',
                '_multibytecodec',
                '_ssl',
                'bz2',
                'cProfile',
                'codecs',
                'ctypes',
                'distutils',
                'doctest',
                'dummy_threading',
                'fnmatch',
                'ftplib',
                'getpass',
                'gzip',
                'highscoretest',
                'hmac',
                'inspect',
                'lib2to3',
                'logging',
                'mimetypes',
                'mmap',
                'multiprocessing.connection',
                'multiprocessing.dummy',
                'multiprocessing.forking',
                'multiprocessing.managers',
                'multiprocessing.pool',
                'multiprocessing.queues',
                'multiprocessing.reduction',
                'multiprocessing.sharedctypes',
                'multiprocessing.synchronize',
                'numpy',
                'pkg_resources',
                'platform',
                'plistlib',
                'pstats',
                'pydoc',
                'pydoc_data',
                'pygame._numpysndarray',
                'pygame._numpysurfarray',
                'pygame.camera', 
                'pygame.fastevent',
                'pygame.mac_scrap',
                'pygame.macosx',
                'pygame.mask',
                'pygame.movie',
                'pygame.overlay',
                'pygame.pixelarray',
                'pygame.pkgdata',
                'pygame.scrap',
                'pygame.surfarray',
                'readline',
                'scipy',
                'shutil',
                'ssl',
                'tarfile',
                'tempfile',
                'termios',
                'tkinter',
                'unittest',
                'zipfile',
                ]

include_files = [join('sfx' , j) for j in listdir('sfx' ) if 'bfxr' not in j] + \
                [join('gfx' , k) for k in listdir('gfx' )                   ] + \
                [join('text', m) for m in listdir('text')]


build_options = {
                 'append_script_to_exe':True,
                 'bin_excludes':excludes,
                 'compressed':True,
                 'excludes': excludes,
                 'include_files': include_files,
                 'includes': includes,
                 'optimize':2,
                 'packages': ['core', 'game'],
                 }

common_exe_options = {
                      'appendScriptToExe'  : True,
                      'appendScriptToLibrary':True,
                      'compress'           : True,
                      'copyDependentFiles' : True,
                      'excludes'           : excludes,
                      'includes'           : includes,
                      'script'             : '__init__.py',
                     }

linux = Executable(
                   **common_exe_options
                   )

windows = Executable(
                     **common_exe_options
                     )

setup(name='Invasodado',
      version='0.8',
      description='wowza!',
      options = {'build_exe': build_options,
                 'bdist_msi': build_options},
      executables=[linux, windows])