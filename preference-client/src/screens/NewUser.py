from kivy.app import App
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from Utils import ftoc
from ScreenTools import *
from functools import partial
import re

class NewUser(Screen):

    temperature_button = None
    color_temperature_button = None
    temp_dropdown = None
    
    color_temp_dropdown = None
    
    name_input = None
    temperature = None
    color_temperature = None

    def __init__(self, **kwargs):
        super(NewUser, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_layout()

    def on_pre_enter(self, *args):
        self.temperature_button.text = 'Choose temperature'

        
        self.color_temperature_button.text = "Choose color temperature"
        

        self.name_input.text = ''

    def setup_layout(self):
        # ================
        # Title layout
        # ================
        title_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        title_layout.add_widget(Label(
            font_size=Window.height*0.07,
            size_hint_y=None,
            text='New User'))
        self.add_widget(title_layout)
        # ================
        # Center layout
        # ================
        center_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        center_box = BoxLayout(
            orientation='vertical',
            spacing=30,
            size_hint=(None, None),
            width=Window.width*0.8,
            height=Window.height*0.35)
        grid_layout = GridLayout(cols=3, spacing=20)
        grid_layout.add_widget(Label(
            text='Email'))

        grid_layout.add_widget(Label(

            
            text='Temperature'))
            


        grid_layout.add_widget(Label(
            text='Color Temperature'))


        self.name_input = TextInput(multiline=False)

        
        self.temperature_button = Button(text='Temperature')
        

        self.temp_dropdown = DropDown(max_height=200)
        for i in range(60, 80):
            btn = Button(
                text='%d F  (%.1f C)' % (i, ftoc(i)),
                size_hint_y=None,
                height=30)
            btn.bind(on_press=lambda btn: self.temp_dropdown.select(btn.text))
            self.temp_dropdown.add_widget(btn)
        self.temperature_button.bind(on_release=self.temp_dropdown.open)
        self.temp_dropdown.bind(on_select=lambda instance, x: setattr(
            self.temperature_button, 'text', x))


        
        self.color_temperature_button = Button(text='Color Temperature')
        self.color_temp_dropdown = DropDown(max_height=200)
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
            btn2.bind(on_press=lambda btn2: self.color_temp_dropdown.select(btn2.text))
            self.color_temp_dropdown.add_widget(btn2)
            i += 2000
        self.color_temperature_button.bind(on_release=self.color_temp_dropdown.open)
        self.color_temp_dropdown.bind(on_select=lambda instance, x: setattr(
            self.color_temperature_button, 'text', x))
        


        grid_layout.add_widget(self.name_input)
        grid_layout.add_widget(self.temperature_button)
        grid_layout.add_widget(self.color_temperature_button)
        
        center_box.add_widget(grid_layout)
        submit_button_layout = BoxLayout(
            padding=(90, 0, 90, 0),
            size_hint_y=None,
            height=Window.height*0.1)
        submit_button_layout.add_widget(Button(
            text='Submit',
            on_press=self.submit))
        center_box.add_widget(submit_button_layout)
        center_layout.add_widget(center_box)
        self.add_widget(center_layout)
        notice_layout = AnchorLayout(anchor_x='center', anchor_y='center')
	notice_layout.add_widget(Label(
            font_size=Window.height*0.025,
            size_hint_y=None,
            text="\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nDon't worry, you won't receive any emails from us. We ask for your email, so when you schedule a meeting via email, the SCR\n  Schedule Website can reference your account, and set this room to your account's preferences before your meeting starts."))
        self.add_widget(notice_layout)

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

    def submit(self, _):
        if self.temperature_button.text != 'Choose temperature':
            self.temperature = re.search('^\d\d', self.temperature_button.text).group(0)
        if self.color_temperature_button.text != 'Choose color temperature':
            self.color_temperature = str(int(re.search('^\d\d', self.color_temperature_button.text).group(0)) * 100)
        self.app.user = self.name_input.text

        if not self.app.coordinator.connected:
            err_popup('Not connected to\ncoordinator server')
            return
        if len(self.name_input.text) == 0:
            err_popup('Please enter an email.')
            return

        if self.temperature_button.text == 'Choose temperature':
            err_popup('Please choose a\ntemperature preference.')
            return
       
        if self.color_temperature_button.text == 'Choose color temperature':
            err_popup('Please choose a\ncolor temperature\npreference.')
            return

        if self.name_input.text in self.app.coordinator.get_user_names():
            err_popup('Email already has\naccount.')
            return

        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.name_input.text)
        if match == None:
            err_popup("Not a valid email address")
            return

        # clientnumber's value varies, depending on preference client
        client_number = str(self.app.store['id'])


        preference = self.temperature + " " + self.color_temperature + " " + client_number + " " + "1" + " " + self.app.user
        print(preference)

        self.app.coordinator.add_user(self.app.user, preference)
        self.app.coordinator.add_user_to_node(self.app.user)
        change_screen(self, 'left', 'UserMenu')
