from kivy.app import App
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from ScreenTools import *
from functools import partial

# Preference client configure screen
class Configure(Screen):

    coordinator_host = None
    coordinator_port = None
    id = None
    pos_x = None
    pos_y = None
    temp_offset_dropdown = None
    temp_offset_button = None

    def __init__(self, **kwargs):
        super(Configure, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_labels()
        self.setup_buttons()
        self.setup_layout()

    def on_pre_enter(self, *args):
        if self.app.coordinator.connected:
            self.temp_offset_button.text = str(self.app.coordinator.get_temp_offset())

    def setup_labels(self):
        self.coordinator_host = TextInput(
            multiline=False,
            text=self.app.store['coordinator_host'])
        self.coordinator_port = TextInput(
            multiline=False,
            text=str(self.app.store['coordinator_port']))
        self.id = TextInput(
            multiline=False,
            text=str(self.app.store['id']))
        self.pos_x = TextInput(
            multiline=False,
            text=str(self.app.store['pos_x']))
        self.pos_y = TextInput(
            multiline=False,
            text=str(self.app.store['pos_y']))

    def setup_buttons(self):
        self.temp_offset_button = Button(text='unknown')
        self.temp_offset_dropdown = DropDown()
        self.temp_offset_dropdown.max_height = 200
        self.temp_offset_button.bind(on_release=self.temp_offset_dropdown.open)
        self.temp_offset_dropdown.bind(on_select=lambda instance, x: setattr(
            self.temp_offset_button, 'text', x))
        for i in range(-11, 11):
            btn = Button(
                text='%d' % i,
                size_hint_y=None,
                height=30)
            btn.bind(on_press=lambda btn: self.temp_offset_dropdown.select(btn.text))
            self.temp_offset_dropdown.add_widget(btn)

    def setup_layout(self):
        # ================
        # Title layout
        # ================
        title_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        title_layout.add_widget(Label(
            font_size=Window.height*0.07,
            size_hint_y=None,
            text='Configure'))
        self.add_widget(title_layout)
        # ================
        # Center layout
        # ================
        center_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        center_grid = GridLayout(
            size_hint=(None, None),
            width=Window.width*0.6,
            height=Window.height*0.6,
            cols=3,
            spacing=10)
        center_grid.add_widget(Label(text='Coordinator IP'))
        center_grid.add_widget(self.coordinator_host)
        center_grid.add_widget(Button(text='Submit', on_release=self.change_coordinator_host))
        center_grid.add_widget(Label(text='Coordinator Port'))
        center_grid.add_widget(self.coordinator_port)
        center_grid.add_widget(Button(text='Submit', on_release=self.change_coordinator_port))
        center_grid.add_widget(Label(text='Node ID'))
        center_grid.add_widget(self.id)
        center_grid.add_widget(Button(text='Submit', on_release=self.change_id))
        center_grid.add_widget(Label(text='Position X'))
        center_grid.add_widget(self.pos_x)
        center_grid.add_widget(Button(text='Submit', on_release=self.change_pos_x))
        center_grid.add_widget(Label(text='Position Y'))
        center_grid.add_widget(self.pos_y)
        center_grid.add_widget(Button(text='Submit', on_release=self.change_pos_y))
        center_grid.add_widget(Label(text='Change Temp. Offset'))
        center_grid.add_widget(self.temp_offset_button)
        center_grid.add_widget(Button(text='Submit', on_release=self.change_temp_offset))
        center_grid.add_widget(Label(text='Exit'))
        center_grid.add_widget(Label(text=''))
        center_grid.add_widget(Button(text='Exit', on_release=self.app.stop))
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

    def change_coordinator_host(self, _):
        self.app.store['coordinator_host'] = self.coordinator_host.text
        self.app.coordinator.stop_node()
        self.app.init_coordinator()

    def change_coordinator_port(self, _):
        self.app.store['coordinator_port'] = int(self.coordinator_port.text)
        self.app.coordinator.stop_node()
        self.app.init_coordinator()

    def change_id(self, _):
        self.app.store['id'] = int(self.id.text)
        self.app.coordinator.stop_node()
        self.app.init_coordinator()
        popup = Popup(title='Warning',
                      content=Label(text='This action requires restarting '
                                         'the client.\nPlease unplug and '
                                         're-plug the Raspberry Pi.'),
                      size_hint=(None, None),
                      size=(400, 200))
        popup.open()

    def change_pos_x(self, _):
        self.app.store['pos_x'] = float(self.pos_x.text)
        self.app.coordinator.stop_node()
        self.app.init_coordinator()

    def change_pos_y(self, _):
        self.app.store['pos_y'] = float(self.pos_y.text)
        self.app.coordinator.stop_node()
        self.app.init_coordinator()

    def change_temp_offset(self, _):
        if not self.app.coordinator.connected:
            err_popup('Not connected to coordinator server')
            return
        if self.temp_offset_button.text == 'unknown':
            err_popup('Please select a temperature')
            return
        offset = int(self.temp_offset_button.text)
        response = self.app.coordinator.change_temp_offset(offset)
        if response:
            info_popup('Successfully changed temp offset')
        else:
            err_popup('Could not change temp offset')

