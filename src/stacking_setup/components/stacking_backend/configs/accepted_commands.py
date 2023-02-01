"""
The accepted commands and their accepted attributes.

This file contains the allowed commands in a dictionary with the command id as
the dict key and as a value a dict containing the accepted attributes. The accepted
attribute dicts contains the accepted attribute symbols as keys and the allowed data
types as values.

When a new command is added to the system the command should be added to this dict otherwise
it will not be allowed by the Gcode parser.

Only movement commands and attributes are allowed to have a symbol that is one single letter.
Movement commands are not allowed to have attributes

"""

ACCEPTED_ATTRIBUTES = ('S', 'I', 'R', 'A')
ACCEPTED_AXES = ('X', 'Y', 'Z', 'H', 'J', 'K', 'L', 'N', 'O', 'P')
ACCEPTED_LINEAR_AXES = ('X', 'Y', 'Z', 'H', 'J', 'K',)
ACCEPTED_ROTATIONAL_AXES = ('L',)
ACCEPTED_COMMANDS = {
    'G0' : {'ACCEPTED_AXES': ACCEPTED_LINEAR_AXES},
    'G1' : {'ACCEPTED_AXES': ACCEPTED_ROTATIONAL_AXES},
    'G28' : {},
    'G90' : {},
    'G91' : {},
    'M0' : {},
    'M92' : {'ACCEPTED_AXES': ACCEPTED_AXES},
    'M105' : {},
    'M112' : {},
    'M113' : {'S': [int, float]},
    'M114' : {},
    'M140' : {'I': [int],
              'S' : [int, float]},
    'M154' : {'S': [int, float]},
    'M155' : {'S': [int, float]},
    'M811' : {'ACCEPTED_AXES': ACCEPTED_AXES},
    'M812' : {'ACCEPTED_AXES': ACCEPTED_AXES},
    'M813' : {'ACCEPTED_AXES': ACCEPTED_AXES},
    'M814' : {},
    # 'M815' : {},  # Free for new macro commands
    # 'M816' : {},
    # 'M817' : {},
    # 'M818' : {},
    # 'M819' : {},
    'M999' : {'S' : [bool]}
}