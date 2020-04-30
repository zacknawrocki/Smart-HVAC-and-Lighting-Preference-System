## HVAC & Lighting Preference System

**HVAC preference manager for the Smart Conference Room (SCR) in CII 7003**

This repository contains portions of the public code used to run the Smart Conference Room's (our research testbed's) system for collecting and implementing user preferences at Rensselaer Polytechnic Institute.

This repository contains code for the coordinating server, the preference clients, the SCR Schedule Website, the TOF occupant tagging, documentation, and other projects.

Currently, the coordinating server is an AWS EC2 instance and the preference clients are Raspberry Pi model 3s with touch screen displays. The Website, used to scedule meetings in the SCR, is hosted using XAMPP.

* **coordinator**: directory containing preference coordinator server code and other coordinator files, by Zack Nawrocki and Sam Atkinson
* **preference-client**: directory containing preference client code and other preference client files, by Zack Nawrocki and Sam Atkinson
* **SCR Schedule Website**: directory containing the calendar website code, to schedule meetings in the SCR, by Steven Cano and Zack Nawrocki
* **Miscellaneous SCR Projects and Documentation**: directory containing documentation, utilities, and code for other work in the SCR, by Zack Nawrocki and TK Woodstock

**Purpose of this Repository** <br>
The purpose of this repository is to archive some of my previous work, upon leaving the research project (graduating), so it can be easily reverted back to, if any problems emerge. Due to the current COVID-19 pandemic (April 2020), much of the changes made may not be tested until (hopefully) this fall. This work has been handed over to Team Setwipatanachai, who will be continuing with my research. Feel free to use this repository to troubleshoot any problems that may occur. Also, I imagine that this original code will be much different in the future, with more features, as well as our new algorithms, so if you are a new student in the future, and come accross this repository on GitHub (or hosted on-campus), shoot me an email. I'd love to hear about the changes and improvements made to the project! 

This version (May 2020) includes the stable implementation, before the campus was closed from COVID-19. This repository does not include the current work, including minor improvements, such as some better practices for holding data (much of which had to be done quickly, in advance for the 2020 conference and demo), a reliable fix to recover future meetings and room temperature preparations on a reboot, loss of power, or similar issues, and finishing live SCR status data sceens for the preference clients. It also does not include some of the current, major work (as of April 2020), such as switching over to MQTT from ROS and our pre-heating/pre-cooling meeting temperature algorithm, using a data-driven learning and MPC approach to a smart HVAC personlization algorithm, for indoor spaces. Please note that some external links in this repository may break, if future students, or the research center, ever decide to make specific work private or relocate it.

Any future students should be able to clone this repository, if necessary, or use it as a reference to contribute to new work. If there are any questions, issues, requests to access private code, or would just like give me an update, I can always be reached at zacknawrocki@gmail.com

I look forward hearing about all the exciting work, after graduating.

Best, <br>
Zack Nawrocki
