from kivy.app import App
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from ScreenTools import *
from functools import partial
import re


class Login(Screen):

    name_input = None
    preference_guest_name = None

    def __init__(self, **kwargs):
        super(Login, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_layout()

    def find_and_login(self, user, notguest, *args):

        if notguest:
        	match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', user)
        	if match == None:
        		err_popup("Not a valid email address")
        		return
        for name in self.app.coordinator.get_user_names():
            if name == user:
                self.app.user = user
                self.app.coordinator.add_user_to_node(self.app.user)
                change_screen(self, 'left', 'UserMenu')
                return
        # If the guest account has never been used on this preference client, it must be created first.
        if user == self.preference_guest_name:
            preference = str(70) + " " + str(4000) + " K  " + str(self.app.store['id']) + " " + "1" + " " + self.preference_guest_name
            self.app.user = user
            self.app.coordinator.add_user(self.app.user, preference)
            self.app.coordinator.add_user_to_node(self.app.user)
            change_screen(self, 'left', 'UserMenu')
            return
        else:
            err_popup('Account does not exist') 

    def setup_layout(self):
        # ================
        # Title layout
        # ================
        title_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        title_layout.add_widget(Label(
            font_size=Window.height*0.07,
            size_hint_y=None,
            text='Login'))
        self.add_widget(title_layout)
        # ================
        # Center layout
        # ================
        center_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        center_box = BoxLayout(
            size_hint=(None, None),
            width=Window.width*0.35,
            height=Window.height*0.6,
            spacing=10,
            orientation='vertical')
        center_box.add_widget(Label(
            text=''))
        center_box.add_widget(Label(
            text='Login Email'))
        self.name_input = TextInput(multiline=False)
        center_box.add_widget(self.name_input)
        center_box.add_widget(Button(
            text='Login',
            on_press=self.login))
        center_box.add_widget(Label(
            text=''))
        center_box.add_widget(Button(
            text='Continue As Guest',
            on_press=self.guest_login))
        center_layout.add_widget(center_box)
        self.add_widget(center_layout)
        # ================
        # Lower layout
        # ================
        lower_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
        lower_layout.add_widget(Button(
            size_hint_y=None,
            height=Window.height*0.08,
            text='Home',
            on_press=partial(change_screen, self, 'right', 'Home')
        ))
        self.add_widget(lower_layout)

    def login(self, _):
        if not self.app.coordinator.connected:
            err_popup('Not connected to\ncoordinator server')
        else:
            self.find_and_login(self.name_input.text, True)

    def guest_login(self, _):
        if not self.app.coordinator.connected:
            err_popup('Not connected to\ncoordinator server')
            return
        else:
            self.preference_guest_name = "Guest on Preference Client " + str(self.app.store['id'])
            self.find_and_login(self.preference_guest_name, False)

