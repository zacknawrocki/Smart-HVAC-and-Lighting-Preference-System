# Miscellaneous-SCR-Projects
This repository contains utilities, scripts, and other programs used for the LESA Smart Conference Room, located in CII 7003 at Rensselaer Polytechnic Institute, that run
independently of the main repositories, such as [HVAC & Lighting Preference System](https://github.com/zacknawrocki/HVAC-and-Lighting-Preference-System),
[SCR Schedule Website](https://github.com/zacknawrocki/HVACWebsite), and scr.ros_bridge (private). While the directories of this repository's projects are run independently in different locations of the main repositories, these main repositories are still reliant on the work relevant to Miscellaneous-SCR-Projects. Unrelated SCR projects rely on the projects in here, as well, which is why they are treated as a separate collection of projects.


## Documentation
The documentation section provides all the necessary (non-confidential) information for new contributors to get started on the project.

## Temperature Localization TOF Tracking/Tagging
Uses the SCR Time-of-Flight sensors to track individuals in the SCR using artificial light signal sensors, while at the
same time, satisfying the conference room occupants' preferences, by providing their current location with their preferred
temperature preference. Ideally, the goal is for every occupant to have their own personal bubble of temperature satisfaction,
while roaming in the open space of the Smart Conference Room. The ROS TOF tracking was created by TK Woodstock and the tagging/HVAC integration was created by Zack Nawrocki.

## Google Calendar Integration
While the [SCR Schedule Website](https://github.com/zacknawrocki/HVACWebsite) is the ideal way to schedule meetings
in the Smart Conference Rooms (for reasons related to usefulness, convenience, and efficiency), it may not always be in use.
The Google Calendar Integration scripts provides a way to automatically schedule meetings when the website is not used. When meetings are not scheduled through the website, they are scheduled via email, and synced with a Google Calendar. Google Calendar Integration syncs the Google Calendar with the Smart Conference Room Calendar, in cases where the website is not used,
using tools such as the Google Calendar API.

