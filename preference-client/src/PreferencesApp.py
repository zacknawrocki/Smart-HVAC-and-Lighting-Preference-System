from kivy.app import App
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager
from screens.Home import Home
from screens.Configure import Configure
from screens.Login import Login
from screens.NewUser import NewUser
from screens.UserMenu import UserMenu
from screens.Status import Status
from screens.AdminPanel import AdminPanel
from screens.HvacControl import HvacControl
from coordinator import Coordinator
import shelve


class PreferencesApp(App):
    """
    PreferencesApp is the main Kivy Application class for the GUI. It holds
      the coordinator proxy object and the HVAC server object.
    """
    exited = False  # Prevents on_stop from executing twice
    sm = None  # Screen manager
    store = None  # Persistent storage
    coordinator = None  # Coordinator server object
    user = None

    def build(self):
        self.exited = False
        self.setup_store()
        self.init_coordinator()
        self.setup_screens()
        return self.sm

    def setup_store(self):
        self.store = shelve.open('preference_client.shelf')
        if 'id' not in self.store:
            print('initializing store')
            self.store['id'] = 3
            self.store['pos_x'] = 190
            self.store['pos_y'] = 111
            self.store['coordinator_host'] = '192.168.0.2'
            self.store['coordinator_port'] = 3000

    def init_coordinator(self):
        self.coordinator = Coordinator(
            self,
            self.store['coordinator_host'],
            self.store['coordinator_port'],
            self.store['id'],
            self.store['pos_x'],
            self.store['pos_y'])
        self.coordinator.start_node()

    def setup_screens(self):
        self.sm = ScreenManager()
        self.sm.add_widget(Home(name='Home'))
        self.sm.add_widget(Configure(name='Configure'))
        self.sm.add_widget(Login(name='Login'))
        self.sm.add_widget(NewUser(name='NewUser'))
        self.sm.add_widget(UserMenu(name='UserMenu'))
        self.sm.add_widget(Status(name='Status'))
        self.sm.add_widget(HvacControl(name='HvacControl'))
        self.sm.add_widget(AdminPanel(name='AdminPanel'))

    def on_stop(self):
        if self.exited:
            return
        Logger.info('Shutting down...')
        self.store.close()
        self.coordinator.stop_node()
        self.exited = True
