from PreferencesApp import PreferencesApp
from kivy.config import Config
from kivy.core.window import Window
import os


def main():
    """ Start the preference client GUI program.
    This function changes the current directory of the program to the
      directory in which the main file exists. This is needed so that the
      database is created in the same directory, even when the program is
      executed on system startup. This function also sets the window size
      and sets the logging level.
    """
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    Window.size = (800, 480)  # Resolution of RasPi touch screen display
    Config.set('kivy', 'log_level', 'info')
    Config.write()
    PreferencesApp().run()


main()
