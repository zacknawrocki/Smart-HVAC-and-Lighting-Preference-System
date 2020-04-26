from kivy.app import App
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from functools import partial
from kivy.uix.textinput import TextInput
from ScreenTools import change_screen

ADMIN_PASSWORD = 'lesa'

# Home screen of the preference clients

class Home(Screen):

    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_layout()

    def setup_layout(self):
        # Title
        title_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        title_layout.add_widget(Label(
            font_size=Window.height*0.07,
            size_hint_y=None,
            text='HVAC Preference Client'))
        self.add_widget(title_layout)
        # Center Buttons
        center_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        center_box = BoxLayout(
            size_hint=(None, None),
            width=Window.width*0.7,
            height=Window.height*0.15,
            orientation='horizontal',
            spacing=20)
        center_box.add_widget(Button(
            text='New User',
            on_press=partial(change_screen, self, 'left', 'NewUser')))
        center_box.add_widget(Button(
            text='Login',
            on_press=partial(change_screen, self, 'left', 'Login')))
        center_layout.add_widget(center_box)
        self.add_widget(center_layout)
        # Lower Buttons
        lower_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
        lower_box = BoxLayout(
            size_hint_y=None,
            height=Window.height*0.08,
            orientation='horizontal')
        if self.app.store['id'] == 1:
            lower_box.add_widget(Button(
                text='Admin Panel',
                on_press=self.authenticate_admin_popup))
        lower_box.add_widget(Button(
            text='Configure',
            on_press=self.authenticate_configure_popup))
        lower_box.add_widget(Button(
            text='Status',
            on_press=partial(change_screen, self, 'left', 'Status')))
        lower_layout.add_widget(lower_box)
        self.add_widget(lower_layout)

    def authenticate_configure_popup(self, _):
        layout = BoxLayout(
            orientation='vertical',
            spacing=20
        )
        password_field = TextInput(multiline=False)
        submit_button = Button(text='Submit')
        layout.add_widget(password_field)
        layout.add_widget(submit_button)
        popup = Popup(title='Enter Password',
                      content=layout,
                      size_hint=(None, None),
                      size=(400, 160),
                      pos_hint={
                          'y': 300.0 / Window.height
                      })
        submit_button.bind(on_release=partial(
            self.authenticate_configure,
            password_field,
            popup
        ))
        popup.open()

    def authenticate_configure(self, password_field, popup, _):
        popup.dismiss()
        if password_field.text == ADMIN_PASSWORD:
            change_screen(self, 'left', 'Configure')

    def authenticate_admin_popup(self, _):
        layout = BoxLayout(
            orientation='vertical',
            spacing=20
        )
        password_field = TextInput(multiline=False)
        submit_button = Button(text='Submit')
        layout.add_widget(password_field)
        layout.add_widget(submit_button)
        popup = Popup(title='Enter Password',
                      content=layout,
                      size_hint=(None, None),
                      size=(400, 160),
                      pos_hint={
                          'y': 300.0 / Window.height
                      })
        submit_button.bind(on_release=partial(
            self.authenticate_admin,
            password_field,
            popup
        ))
        popup.open()

    def authenticate_admin(self, password_field, popup, _):
        popup.dismiss()
        if password_field.text == ADMIN_PASSWORD:
            change_screen(self, 'left', 'AdminPanel')

