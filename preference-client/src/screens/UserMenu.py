from kivy.app import App
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from ScreenTools import *
from Utils import ftoc
import re

'''
This file/screen is the greeting page, when a user logs into their account/creates an account.
Using the menu, they can update their temperature preferences.
'''

class UserMenu(Screen):

    name_label = None
    preference_f = None
    preference_c = None
    estimated_f = float(70)
    estimated_c = ftoc(float(70))
    thermostat_f = None
    thermostat_c = None
    color_temperature = None
    color_temperature_c = None
    temperature_button = None
    temperature_dropdown = None
    color_temperature_button = None
    color_temperature_dropdown = None
    client_number = None
    flag = None
    user = None
    temperature = None
    colortemp = None


    def __init__(self, **kwargs):
        super(UserMenu, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_layout()

    def on_pre_enter(self, *args):
        self.name_label.text = self.app.user
        preference = self.app.coordinator.get_user_preference(self.app.user)
        plist = preference.split(" ")
        self.temperature = float(plist[0])
        self.preference_f.text = '%.1f F' % self.temperature
        self.preference_c.text = '%.1f C' % ftoc(self.temperature)
        self.color_temperature.text = '%.0f K' % (int(plist[1]))
        self.colortemp = int(plist[1])
        celsius_ct = int(plist[1]) - 273
        self.color_temperature_c.text = '%.1f C' % celsius_ct
        self.client_number = plist[2]
        self.flag = plist[3]
        self.user = plist[4]
        self.estimated_f.text = '%.1f F' % float(70)
        self.estimated_c.text = '%.1f C' % ftoc(float(70))


    def update(self, thermostat_temp, estimated_temp):
        print("Thermostat: %s" % str(thermostat_temp))
        print("Estimated: %s" % str(estimated_temp))

        if not thermostat_temp or thermostat_temp == 'None':
            self.thermostat_f.text = '... F'
            self.thermostat_c.text = '... C'
        else:
            self.thermostat_f.text = '%.1f F' % float(thermostat_temp)
            self.thermostat_c.text = '%.1f C' % ftoc(float(thermostat_temp))
        if not estimated_temp or estimated_temp == 'None':
            self.estimated_f.text = '... F'
            self.estimated_c.text = '... C'
        else:
            self.estimated_f.text = '%.1f F' % float(70)
            self.estimated_c.text = '%.1f C' % ftoc(float(70))

    def setup_layout(self):
        # ================
        # Title layout
        # ================
        self.name_label = Label(
            font_size=Window.height*0.07,
            size_hint_y=None,
            text='Menu')
        title_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        title_layout.add_widget(self.name_label)
        self.add_widget(title_layout)
        # ================
        # Center layout
        # ================
        temperature_button_layout = AnchorLayout(anchor_x='left', anchor_y='center')
        temperature_button_box = BoxLayout(
            padding=(0, 200, 0, 0),
            size_hint=(None, None),
            width=Window.width*0.25,
            height=250)
        self.temperature_button = Button(text='Change Temperature')
        self.temperature_dropdown = DropDown(max_height=100)
        for i in range(60, 80):
            btn = Button(
                text='%d F  (%.1f C)' % (i, ftoc(i)),
                size_hint_y=None,
                height=30)
            btn.bind(on_press=lambda btn: self.temperature_dropdown.select(btn.text))
            self.temperature_dropdown.add_widget(btn)
        self.temperature_button.bind(on_release=self.temperature_dropdown.open)
        self.temperature_dropdown.bind(on_select=lambda instance, x: self.change_temperature(x, instance))
        temperature_button_box.add_widget(self.temperature_button)
        temperature_button_layout.add_widget(temperature_button_box)
        self.add_widget(temperature_button_layout)
        color_temperature_button_layout = AnchorLayout(anchor_x='right', anchor_y='center')
        color_temperature_button_box = BoxLayout(
            padding=(0, 200, 0, 0),
            size_hint=(None, None),
            width=Window.width*0.25,
            height=250)
        self.color_temperature_button = Button(text='Change Color Temperature')
        self.color_temperature_dropdown = DropDown(max_height=100)
        i = 2000
        while i <= 9000:
            # Conditional added to remove 6500 preference
            if i == 6000:
                i += 3000
                continue
                ''' The following two formulas (colored RGB codes from a given color temperature) 
                were created by plotting and curving the color temperatures to their
                corresponding RGB values (divided bt 255) on a graph using mycurvefit.com '''
            red = 0.8921777 + (1.10058 - 0.8921777)/(1 + (i/2336.671)**2.32823)
            if i == 2000:
                red = 1
            blue = 0.9125559 + (-0.2750087 - 0.9125559)/(1 + (i/1447.539)**1.641898)
            # Green is consistent throughout the spectrum (254)
            btn2 = Button(
                text= str(i) + " K",
                color=[red, 0.996, blue, 1],
                size_hint_y=None,
                height=30)
            btn2.bind(on_press=lambda btn2: self.color_temperature_dropdown.select(btn2.text))
            self.color_temperature_dropdown.add_widget(btn2)
            i += 2000
        self.color_temperature_button.bind(on_release=self.color_temperature_dropdown.open)
        self.color_temperature_dropdown.bind(on_select=lambda instance, x: self.change_color_temperature(x, instance))
        color_temperature_button_box.add_widget(self.color_temperature_button)
        color_temperature_button_layout.add_widget(color_temperature_button_box)
        self.add_widget(color_temperature_button_layout)


        # ================
        # Floating layouts
        # ================
        self.add_widget(Label(text='Estimated Position Temp.', pos=(-290, 100)))
        self.add_widget(Label(text='Your Temperature', pos=(-87, 100)))
        self.add_widget(Label(text='Thermostat Setting', pos=(94, 100)))
        self.add_widget(Label(text='Your Color Temperature', pos=(298, 100)))
        self.preference_f = Label(text='... F', font_size=50, pos=(-86, 50))
        self.preference_c = Label(text='... C', font_size=20, pos=(-85, 0))
        self.estimated_f = Label(text='... F', font_size=50, pos=(-285, 50))
        self.estimated_c = Label(text='... C', font_size=20, pos=(-285, 0))
        self.thermostat_f = Label(text='... F', font_size=50, pos=(98, 50))
        self.thermostat_c = Label(text='... C', font_size=20, pos=(96, 0))
        self.color_temperature = Label(text='...K', font_size=50, pos=(296, 50))
        self.color_temperature_c = Label(text='...K', font_size=20, pos=(300, 0))


        self.add_widget(self.preference_f)
        self.add_widget(self.preference_c)
        self.add_widget(self.estimated_f)
        self.add_widget(self.estimated_c)
        self.add_widget(self.thermostat_f)
        self.add_widget(self.thermostat_c)
        self.add_widget(self.color_temperature)
        self.add_widget(self.color_temperature_c)


        # ================
        # Lower layout
        # ================
        lower_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
        lower_layout.add_widget(Button(
            size_hint_y=None,
            height=Window.height*0.08,
            text='Logout',
            on_press=self.logout))
        self.add_widget(lower_layout)

    def change_temperature(self, text, _):
        temperature = int(re.search('^\d\d', text).group(0))
        self.preference_f.text = '%.1f F' % temperature
        self.preference_c.text = '%.1f C' % ftoc(temperature)
        preference = str(temperature) + " " + str(self.colortemp) + " " + self.client_number + " " + self.flag + " " + self.user
        print("Change temperature")
        print(preference)
        self.app.coordinator.update_preference(self.app.user, preference)

    def change_color_temperature(self, text, _):
        color_temperature = int(re.search('^\d\d', text).group(0)) * 100
        self.color_temperature.text = '%.0f K' % color_temperature
        print("Change Color Temperature")
        self.color_temperature_c.text = '%.1f C' % ftoc(color_temperature)
        preference = str(self.temperature) + " " + str(color_temperature) + " " + self.client_number + " " + self.flag + " " + self.user
        print(preference)
        self.app.coordinator.update_preference(self.app.user, preference)
    
    def logout(self, _):
        self.app.coordinator.remove_user_from_node(self.app.user)
        self.app.user = None
        change_screen(self, 'right', 'Home')
