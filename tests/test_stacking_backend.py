import sys, os
#Following lines are for assigning parent directory dynamically.
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)
# The normal imports
from stacking_setup.stacking_backend.stacking_setup import StackingSetupBackend
from stacking_setup.stacking_backend.hardware import PIA13, PRMTZ8, KIM101, KDC101
from stacking_setup.stacking_backend.hardware.emergency_breaker import EmergencyBreaker
import unittest
from unittest.mock import MagicMock, patch


class TestControlBackend(unittest.TestCase):

    # Test initiate hardware
    @patch.multiple('stacking_setup.stacking_backend.stacking_setup.StackingSetupBackend', KDC101=MagicMock(), PRMTZ8=MagicMock(), KIM101=MagicMock(), PIA13=MagicMock(), EmergencyBreaker=MagicMock())
    def test_initiate_hardware(self):
        # Create a StackingSetup object.
        stack = StackingSetupBackend()
        # Test the initiate hardware function.
        stack.initiate_all_hardware()

    # Test disconnect hardware

    # Test emergency stop

    # Test execute one command

    # Test execute multiple commands

    # Test execute lots of commands

    # Test G0

    # Test G1

    # Test G28

    # Test G90

    # Test G91

    # Test M80

    # Test M81

    # Test M92

    # Test M105

    # Test M112

    # Test M113

    # Test M999


if __name__ == '__main__':
    # Run all the tests in this file
    unittest.main()
