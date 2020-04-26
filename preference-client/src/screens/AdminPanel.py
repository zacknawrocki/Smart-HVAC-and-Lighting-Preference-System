from kivy.app import App
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from ScreenTools import *
from functools import partial
from Utils import ftoc
import re

'''
Admin Panel of Preference Client

This screen is only available on preference client one, and provides administrator privelages
for users who know the password.
'''

class AdminPanel(Screen):

    name_button = None
    name_dropdown = None
    default_temp_dropdown = None
    default_temp_button = None
    temp_offset_dropdown = None
    temp_offset_button = None

    def __init__(self, **kwargs):
        super(AdminPanel, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_buttons()
        self.setup_layout()

    def on_pre_enter(self):
        self.name_dropdown.clear_widgets()
        if self.app.coordinator.connected:
            for name in self.app.coordinator.get_user_names():
                btn = Button(text=name, size_hint_y=None, height=30)
                btn.bind(on_press=lambda b: self.name_dropdown.select(b.text))
                self.name_dropdown.add_widget(btn)
            default_temp = int(self.app.coordinator.get_default_temp())
            self.default_temp_button.text = '%d F  (%.1f C)' % (default_temp, ftoc(default_temp))
        self.name_button.text = 'Select Name'

    def setup_buttons(self):
        self.name_button = Button(text='Select Name')
        self.name_dropdown = DropDown()
        self.name_dropdown.max_height = 200
        self.name_button.bind(on_release=self.name_dropdown.open)
        self.name_dropdown.bind(on_select=lambda instance, x: setattr(
            self.name_button, 'text', x))
        self.default_temp_button = Button(text='unknown')
        self.default_temp_dropdown = DropDown()
        self.default_temp_dropdown.max_height = 200
        self.default_temp_button.bind(on_release=self.default_temp_dropdown.open)
        self.default_temp_dropdown.bind(on_select=lambda instance, x: setattr(
            self.default_temp_button, 'text', x))
        for i in range(60, 80):
            btn = Button(
                text='%d F  (%.1f C)' % (i, ftoc(i)),
                size_hint_y=None,
                height=30)
            btn.bind(on_press=lambda btn: self.default_temp_dropdown.select(btn.text))
            self.default_temp_dropdown.add_widget(btn)

    def setup_layout(self):
        # ================
        # Title layout
        # ================
        title_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        title_layout.add_widget(Label(
            font_size=Window.height*0.07,
            size_hint_y=None,
            text='Admin Panel'))
        self.add_widget(title_layout)
        # ================
        # Center layout
        # ================
        center_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        center_grid = GridLayout(
            size_hint=(None, None),
            width=Window.width*0.7,
            height=Window.height*0.3,
            cols=3,
            spacing=20)
        center_grid.add_widget(Label(text='Remove User'))
        center_grid.add_widget(self.name_button)
        center_grid.add_widget(Button(text='Submit', on_release=self.remove_user))
        center_grid.add_widget(Label(text='Change Default Temp.'))
        center_grid.add_widget(self.default_temp_button)
        center_grid.add_widget(Button(text='Submit', on_release=self.change_default_temp))
        center_layout.add_widget(center_grid)
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

    # Remove users from the preference coordinator server database
    def remove_user(self, _):
        if not self.app.coordinator.connected:
            err_popup('Not connected to coordinator server')
            return
        if self.name_button.text == 'Select Name':
            err_popup('Please select a username')
            return
        response = self.app.coordinator.remove_user(self.name_button.text)
        if response:
            info_popup('Successfully removed user')
        else:
            err_popup('Could not remove user')

    def change_default_temp(self, _):
        if not self.app.coordinator.connected:
            err_popup('Not connected to coordinator server')
            return
        if self.default_temp_button.text == 'unknown':
            err_popup('Please select a temperature')
            return
        temperature = int(re.search('^\d\d', self.default_temp_button.text).group(0))
        response = self.app.coordinator.change_default_temp(temperature)
        if response:
            info_popup('Successfully changed default temp')
        else:
            err_popup('Could not change default temp')

