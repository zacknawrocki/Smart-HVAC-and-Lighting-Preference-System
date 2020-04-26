'''
emergencyreset.py is as supplemental file for SCRResearchDocumentation.pdf, used
for troubleshooting HVAC Server problems
'''


# Make sure to run this file in the same directory as your HVACLib.py file

from HVACLib import HVAC

myhvac = HVAC()
myhvac.reset()
myhvac.close()