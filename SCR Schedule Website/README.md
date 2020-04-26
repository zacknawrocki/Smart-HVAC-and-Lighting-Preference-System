# SCR Schedule Website


**Overview** <br>
This website serves as an online calendar web application (similar to Google or Apple Calendar), that allows users to schedule meetings in the Smart Conference Room (SCR) at Rensselaer Polytechnic Institute. Once scheduled or removed, the information is sent to the [Preference Coordinator Server](https://github.com/zacknawrocki/HVAC-and-Lighting-Preference-System/tree/master/coordinator), in order to set the meeting's temperature to the preferences of attendees, using a smart temperature, pre-heating/pre-cooling, data-driven learning, indoor thermal management control algorithm.

**Code changes** <br>
Lines 221 and 318 of home.php must be configured to match the appropriate url of the preference server before implementing. This url is removed from the repository, to protect the public ip address used to access this website. A home.php, with the relevant url, can be found on the SRC Linux Machine, located in opt/lampp/htdocs/home.php.


**Running the code** <br>
This repository is ran using XAMPP, an open-source cross-platform web server solution. Once installing the XAMPP environment, these files are placed in opt/lampp/htdocs.
