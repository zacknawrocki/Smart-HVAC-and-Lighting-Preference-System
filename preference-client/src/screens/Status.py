from kivy.app import App
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from ScreenTools import change_screen
from functools import partial

NUM_SENSORS = 5

# This file makes up the status tab/page of the preference client

class Status(Screen):

    coordinator_status = None
    hvac_status = None
    thermostat_temp = None
    estimated_temp = None
    temp_labels = []

    def __init__(self, **kwargs):
        super(Status, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_labels()
        self.setup_layout()

    def on_pre_enter(self, *args):
        self.coordinator_status.text = 'Online' if self.app.coordinator.connected else 'Offline'

    def update(self, thermostat_setting, estimated_temp, sensor_data):
        self.thermostat_temp.text = str(thermostat_setting)
        self.estimated_temp.text = str(estimated_temp)
        for i in range(len(sensor_data)):
            if sensor_data[i][3] > 0:
                self.temp_labels[i].text = str(sensor_data[i][3])
            else:
                self.temp_labels[i].text = 'Unknown'

    def setup_labels(self):
        self.coordinator_status = Label(text='Offline')
        self.thermostat_temp = Label(text='Unknown')
        self.estimated_temp = Label(text='Unknown')
        for i in range(NUM_SENSORS):
            self.temp_labels.append(Label(text='Unknown'))

    def setup_layout(self):
        # ================
        # Title layout
        # ================
        title_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        title_layout.add_widget(Label(
            font_size=Window.height*0.07,
            size_hint_y=None,
            text='Status'))
        self.add_widget(title_layout)
        # ================
        # Center layout
        # ================
        center_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        center_grid = GridLayout(
            size_hint=(None, None),
            width=Window.width*0.5,
            height=Window.height*0.5,
            cols=2,
            spacing=10)
        center_grid.add_widget(Label(text='Coordinator Server'))
        center_grid.add_widget(self.coordinator_status)
        center_grid.add_widget(Label(text='Themostat Temp.'))
        center_grid.add_widget(self.thermostat_temp)
        center_grid.add_widget(Label(text='Estimated Temp. Here'))
        center_grid.add_widget(self.estimated_temp)
        for i in range(1, NUM_SENSORS+1):
            center_grid.add_widget(Label(text='Sensor %d Temp.' % i))
            center_grid.add_widget(self.temp_labels[i-1])
        center_layout.add_widget(center_grid)

        center_grid2 = GridLayout(
            size_hint=(None, None),
            width=Window.width*0.5,
            height=Window.height*-0.58,
            cols=1,
            spacing=10)
        hvac_control_button_layout = BoxLayout(
            padding=(90, 0, 90, 0),
            size_hint_y=None,
            height=Window.height*0.06)        
        hvac_control_button_layout.add_widget(Button(
            text='HVAC Control',
            on_press=partial(change_screen, self, 'left', 'HvacControl')
        ))
        center_grid2.add_widget(hvac_control_button_layout)

        center_layout.add_widget(center_grid2)
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

    def hvac_control(self, _):
        change_screen(self, 'left', 'HvacControl')
