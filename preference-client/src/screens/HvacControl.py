# Not currently being used.


from kivy.app import App
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from ScreenTools import *
import re
from functools import partial

import paho.mqtt.client as mqtt
import time, json

import threading



class HvacControl(Screen):


    co2 = "---"
    ep1 = "---"
    ep2 = "---"
    ep3 = "---"
    ep4 = "---"
    temp1 = "---"
    temp2 = "---"
    temp3 = "---"
    temp4 = "---"
    temp5 = "---"
    humidity = "---"


    def __init__(self, **kwargs):
        super(HvacControl, self).__init__(**kwargs)
        self.app = App.get_running_app()


        num = "P" + str(self.app.store['id'] + 59)
        print("num")
        print(num)
        broker_address="192.168.0.2"
        print("test1")
        client = mqtt.Client(num, True, None, mqtt.MQTTv31)
        print("test2")
        client.on_message=self.on_message
        print("test3")
        client.on_log=self.on_log
        client.connect(broker_address)
        client.loop_start()
        print("test4")
        client.subscribe("HVAC_data")
        self.setup_layout()

    def setup_layout(self):
        title_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        title_layout.add_widget(Label(
            font_size=Window.height*0.07,
            size_hint_y=None,
            text='HVAC Control'))
        self.add_widget(title_layout)

        center_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        grid_layout = GridLayout(
            size_hint=(None, None),
            width=Window.width*0.8,
            height=Window.height*0.5,
            cols=17)

        for i in range(119):
            if i == 2:
                grid_layout.add_widget(Button(text=self.temp1, background_color = (1.0, 1.0, 1.0, 1.0), size_hint_x=None, width=37))
                continue        
            if i == 7:
                grid_layout.add_widget(Button(text=self.temp2, background_color = (1.0, 1.0, 1.0, 1.0), size_hint_x=None, width=37))
                continue
            if i == 10:
                grid_layout.add_widget(Button(text=self.humidity, background_color = (1.0, 1.0, 1.0, 1.0), size_hint_x=None, width=37))
                continue
            if i == 11:
                grid_layout.add_widget(Button(text=self.co2, background_color = (1.0, 1.0, 1.0, 1.0), size_hint_x=None, width=37))
                continue
            if i == 15:
                grid_layout.add_widget(Button(text=self.temp3, background_color = (1.0, 1.0, 1.0, 1.0), size_hint_x=None, width=37))
                continue    
            if i == 17 or i == 34 or i == 51 or i == 68 or i == 85:
                if i == 51:
                    grid_layout.add_widget(Button(text=self.ep1, background_color = (0.83, 0.1, 0.22, 1.0), size_hint_x=None, width=37))
                    continue
                else:
                    grid_layout.add_widget(Button(background_color = (0.83, 0.1, 0.22, 1.0), size_hint_x=None, width=37))
                    continue
            if i == 37 or i == 41 or i == 44 or i == 48 or i == 56 or i == 63 or i == 71 or i == 75 or i == 78 or i == 82:
                grid_layout.add_widget(Button(background_color = (0.74, 0.52, 0.24, 1.0), size_hint_x=None, width=37))
                continue
            if i > 56 and i < 60:
                if i == 58:
                    grid_layout.add_widget(Button(text=self.ep2, background_color = (0.83, 0.1, 0.22, 1.0), size_hint_x=None, width=37))
                    continue
                else:
                    grid_layout.add_widget(Button(background_color = (0.83, 0.1, 0.22, 1.0), size_hint_x=None, width=37))
                    continue
            if i > 59 and i < 63:
                if i == 61:
                    grid_layout.add_widget(Button(text=self.ep3, background_color = (0.1, 0.44, 0.7, 1.0), size_hint_x=None, width=37))
                    continue
                else:
                    grid_layout.add_widget(Button(background_color = (0.1, 0.44, 0.7, 1.0), size_hint_x=None, width=37))
                    continue
            if i == 109:
                grid_layout.add_widget(Button(text=self.temp4, background_color = (1.0, 1.0, 1.0, 1.0), size_hint_x=None, width=37))
                continue
            if i == 112:
                grid_layout.add_widget(Button(text=self.temp5, background_color = (1.0, 1.0, 1.0, 1.0), size_hint_x=None, width=37))
                continue
            if i > 114:
                if i == 116:
                    grid_layout.add_widget(Button(text=self.ep4, background_color = (0.83, 0.1, 0.22, 1.0), size_hint_x=None, width=37))
                    continue
                else:
                    grid_layout.add_widget(Button(background_color = (0.83, 0.1, 0.22, 1.0), size_hint_x=None, width=37))
                    continue

            else:
                grid_layout.add_widget(Button(background_color = (1.0, 1.0, 1.0, 1.0), size_hint_x=None, width=37))

        center_layout.add_widget(grid_layout)
        self.add_widget(center_layout)

        lower_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
        lower_layout.add_widget(Button(
            size_hint_y=None,
            height=Window.height*0.08,
            text='Back',
            on_press=partial(change_screen, self, 'right', 'Status')
            ))
        self.add_widget(lower_layout)


    def on_message(self, client, userdata, message):
        print("ran")
        message = json.loads(message.payload.decode("utf-8"))
        (self.temp1, self.temp2, self.temp3, self.temp4, self.temp5) = (message.get('temp')[0], message.get('temp')[1], message.get('temp')[2], message.get('temp')[3], message.get('temp')[4])
        self.co2 = message.get('co2')
        (self.ep1, self.ep2, self.ep3, self.ep4) = (message.get('ep')[0], message.get('ep')[1], message.get('ep')[2], message.get('ep')[3])
        self.humidity = message.get('humidity')
        print(message)

    def on_log(self, cient, userdata, level, buf):
        print("log: ", buf)




