from kivy.uix.popup import Popup
from kivy.uix.label import Label


def change_screen(screen, direction, next_screen_name, _=None):
    screen.manager.transition.direction = direction
    screen.manager.current = next_screen_name


def err_popup(message):
    """ Show an error pop-up message.
    :param message: message to be displayed
    """
    popup = Popup(title='Error',
                  size_hint=(None, None),
                  size=(200, 200),
                  content=Label(text=message))
    popup.open()


def info_popup(message):
    """ Show an information pop-up message.
    :param message: message to be displayed
    """
    popup = Popup(title='Info',
                  size_hint=(None, None),
                  size=(200, 200),
                  content=Label(text=message))
    popup.open()
