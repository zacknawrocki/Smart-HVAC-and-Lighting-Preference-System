# Google Calendar Integration

## Setup Steps
**Step 1: Google Credentials** <br/>
To coordinate your Google Calendar with googlecalendar_srcschedule.py, you must first setup your credentials by visiting [Google API Client](https://github.com/googleapis/google-api-python-client)

**Step 2: Creating a virtualenv** <br/>
The current SCR setup does not allow the use of [Python Quickstart](https://developers.google.com/calendar/quickstart/python) for Google Calendar API, when implementing the option to use a Google Calendar in lieu of the SCR Schedule website. Instead, you must create a virtualenv as explained on this repository's [README](https://github.com/googleapis/google-api-python-client/blob/master/README.md)

**Step 3: Running the Script** <br/>
After setting everything up, the Python script can be ran using the following commands: <br/>

```
$ source <your-env>/bin/activate           <your-env> is the name of your virtualenv created in Step 2 
$ python googlecalendar_srcschedule.py
```
