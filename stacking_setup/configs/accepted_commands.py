"""
The accepted commands and their accepted attributes.

This file contains the allowed commands in a dictoinary with the command id as
the dics key and as a value a dict containing the accepted attributes. The accepted
attribute dicst contains the accepted attribute symbols as keys and the allowed data
types as values.

When a new command is added to the system the command should be added to this dict otherwise
it will not be allowed by the gcode parser.

Only movement commands and attributes are allowed to have a symbol that is one single letter.
Movment comamands are not allowed to have attributes

"""

ACCEPTED_ATTRIBUTES = ['S', 'I', 'R']
ACCEPTED_AXES = ['X', 'Y', 'Z', 'I', 'J', 'K', 'L']
ACCEPTED_COMMANDS = {
    'G0' : {'ACCEPTED_AXES': ACCEPTED_AXES},
    'G1' : {'ACCEPTED_AXES': ACCEPTED_AXES},
    'G28' : {},
    'G90' : {},
    'G91' : {},
    'M0' : {},
    'M80' : {},
    'M81' : {},
    'M85' : {'S': [int, float]},
    'M92' : {'S': [int, float]},
    'M105' : {},
    'M111' : {'S': [int]},
    'M112' : {},
    'M113' : {},
    'M114' : {},
    'M119' : {},
    'M120' : {},
    'M121' : {},
    'M140' : {'I': [int],
              'S' : [int, float]},
    'M154' : {'S': [int]},
    'M155' : {'S': [int]},
    'M190' : {'I': [int],
              'R': [int, float],
              'S': [int, float]},
    'M500' : {},
    'M501' : {},
    'M503' : {},
    'M510' : {},
    'M511' : {'S' : [bytes]},
    'M512' : {'S' : [bytes]},
    'M810' : {},
    'M811' : {},
    'M812' : {},
    'M813' : {},
    'M814' : {},
    'M815' : {},
    'M816' : {},
    'M817' : {},
    'M818' : {},
    'M819' : {},
    'M999' : {'S' : [bool]}
}