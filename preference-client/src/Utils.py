'''
Utils.py

Place important utility functions here, for the preference clients
'''

# Celsius to Farenheit
def ctof(temp_c):
    return temp_c * 1.8 + 32

# Farenheit to Celsius
def ftoc(temp_f):
    return (temp_f - 32) / 1.8
