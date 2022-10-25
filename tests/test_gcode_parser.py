import unittest
#Following lines are for assigning parent directory dynamically.
import sys, os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)
from stacking_setup.stacking_backend.gcode_parser import GcodeParser


class TestGcodeParser(unittest.TestCase):

    # Test is valid with valid commands.
    def test_is_valid_with_valid_commands(self):
        self.assertTrue(GcodeParser._is_valid('Y0'))
        self.assertTrue(GcodeParser._is_valid('G1'))
        self.assertTrue(GcodeParser._is_valid('I0'))
        self.assertTrue(GcodeParser._is_valid('X0.0'))
        self.assertTrue(GcodeParser._is_valid('L0.0'))
        self.assertTrue(GcodeParser._is_valid('K0'))
        self.assertTrue(GcodeParser._is_valid('G28'))
        self.assertTrue(GcodeParser._is_valid('G90'))
        self.assertTrue(GcodeParser._is_valid('G91'))
        self.assertTrue(GcodeParser._is_valid('M0'))
        #self.assertTrue(GcodeParser._is_valid('M111'))
        self.assertTrue(GcodeParser._is_valid('M112'))
        #self.assertTrue(GcodeParser._is_valid('M119'))
        #self.assertTrue(GcodeParser._is_valid('M120'))
        self.assertTrue(GcodeParser._is_valid('M999'))

    # Test is valid with invalid commands.
    def test_is_valid_with_invalid_commands(self):
        # Should not be valid because a value should be attached
        self.assertFalse(GcodeParser._is_valid('Y'))
        self.assertFalse(GcodeParser._is_valid('G'))
        self.assertFalse(GcodeParser._is_valid('I'))
        self.assertFalse(GcodeParser._is_valid('X'))
        self.assertFalse(GcodeParser._is_valid('K'))
        self.assertFalse(GcodeParser._is_valid('L'))

        # Should not be valid because does not exits
        self.assertFalse(GcodeParser._is_valid('G22222'))
        self.assertFalse(GcodeParser._is_valid('G2902'))
        self.assertFalse(GcodeParser._is_valid('G'))
        self.assertFalse(GcodeParser._is_valid('M'))
        self.assertFalse(GcodeParser._is_valid('1045'))
        self.assertFalse(GcodeParser._is_valid('0'))
        self.assertFalse(GcodeParser._is_valid('999'))

    # Test add one machine command
    def test_add_one_machine_command(self):
        expected = {'M112': {}}
        gcode_line = 'M112'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)
        self.assertEqual(parsed_commands, expected)

    # Test add multiple machine commands
    def test_add_multiple_machine_commands(self):
        expected = {'M112': {}, 'M113': {}}
        gcode_line = 'M112 M113'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)
        self.assertEqual(parsed_commands, expected)

    # Test add one attribute command
    def test_add_one_attribute_command(self):
        expected = {'M140': {'S': 0.0}}
        gcode_line = 'M140 S0.0'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)
        self.assertEqual(parsed_commands, expected)

    # Test add multiple attribute commands
    def test_add_multiple_attribute_commands(self):
        expected = {'M190': {'S': 0.6, 'R': 5, 'I':-2}}
        gcode_line = 'M190 R5 I-2 S0.6'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)
        self.assertEqual(parsed_commands, expected)

    # Test add boolean attribute
    def test_add_boolean_attribute(self):
        expected = {'M999': {'S': True}}
        gcode_line = 'M999 S1'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)
        self.assertEqual(parsed_commands, expected)

        gcode_line = 'M999 STrue'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)
        self.assertEqual(parsed_commands, expected)

        gcode_line = 'M999 Strue'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)
        self.assertEqual(parsed_commands, expected)

        expected = {'M999': {'S': False}}
        gcode_line = 'M999 S0'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)
        self.assertEqual(parsed_commands, expected)

    # Test add one movement command
    def test_add_one_movement_command(self):
        expected = {'G1': {'L': 0.0}}
        gcode_line = 'G1 L0.0'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)
        self.assertEqual(parsed_commands, expected)

    # Test add multiple movement commands
    def test_add_multiple_movement_commands(self):
        expected = {'G0': {'X': 5, 'Y': 0, 'Z': 5.7}}
        gcode_line = 'G0 X5 Y0 Z5.7'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)
        self.assertEqual(parsed_commands, expected)

    # Test backward movement command
    def test_backward_movement_(self):
        expected = {'G1': { 'L': -5 } }
        gcode_line = 'G1 L-5'
        parsed_commands = GcodeParser().parse_gcode_line(gcode_line)

    # Test add duplicate movement command
    def test_add_duplicate_movement_command(self):
        gcode_line = 'G0 X0.0 X0.0'
        with self.assertRaises(ValueError):
            _ = GcodeParser().parse_gcode_line(gcode_line)

    # Test add movent to command that doesnt allow movement
    def test_add_movement_to_not_allowed(self):
        gcode_line = 'G28 X0.0'
        with self.assertRaises(AttributeError):
            _ = GcodeParser().parse_gcode_line(gcode_line)

    # Test forbidden movement on linear axis

    # Test forbidden movement on rotational axis


if __name__ == '__main__':
    unittest.main()