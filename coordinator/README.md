## Coordinator

This code runs on a server which communicates with each preference client.

**Running coordinator**

    $ python coordinator.py

**Dependencies**

| Name | Version |
| ---- | ------- |
| Python | 2.7.x |
| cherrypy | >= 13.1.0 |
| numpy | >= 1.14.0 |


**Directory contents**

* **src**: directory containing source code
  * **coordinator.py**: Python file containing entry point for program
  * **queries.py**: Python file containing database queries
  * **calc_temp.py**: Python file containing temperature optimization logic
  * **config.cfg**: configuration file


