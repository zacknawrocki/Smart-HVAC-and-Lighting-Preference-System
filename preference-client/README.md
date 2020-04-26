## Preference Client

This code runs on a client with a display. It handles user input and communicates with the HVAC system in CII 7003. It also communicates with the coordinator server to handle saved users and temperature optimization.

**Running preference client**

    $ python main.py

**Dependencies**

| Name | Version |
| ---- | ------- |
| Python |  2.7.x |
| kivy | >= 1.10.x |
| requests | >= 2.18.x |

**Directory contents**

* **src**: directory containing source code
  * **server**: directory containing Toufiq's HVAC server library
    * **__init__.py**: Python package init
    * **HVACLib.py**: Toufiq's HVAC serveAbbreviation
  * **screens**: directory containing all the screen layouts and interfaces used in the preference client
    * **__init__.py**: Python package init
    * **AdminPanel.py**: admin screen
    * **Configure.py**: configure screen
    * **Home.py**: home screen
    * **HvacControl.py**: HVAC control screen
    * **Login.py**: login screen
    * **NewUser.py**: new user screen
    * **Status.py**: status screen
    * **UserMenu.py**: user menu screen
  * **main.py**: Python file containing main entry point
  * **ScreenTools.py**: useful screen-related functions, such as changing screens and pop-up messages
  * **Utils.py**: common algorithms needed for the client, such as temperature conversions
  * **coordinator.py**: Python file containing coordinator proxy
  * **PreferencesApp.py**: main Kivy application class for the GUI
* **preferencegui.service**: systemd startup script which executes main.py on Raspberry Pi boot (see resource link below)

**Resources**

 * [Starting preference client code on boot](https://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd)
 * [Using official RPi touch display](https://kivy.org/docs/installation/installation-rpi.html)
 * [Activate on-screen keyboard](https://github.com/kivy/kivy/tree/master/examples/keyboard)

