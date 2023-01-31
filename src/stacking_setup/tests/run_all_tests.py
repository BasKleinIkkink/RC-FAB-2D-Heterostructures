from .test_gcode_parser import TestGcodeParser
from .test_middleware import TestPipeLineConnection
from .test_stacking_backend import TestControlBackend
import unittest


def run_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGcodeParser))
    suite.addTest(unittest.makeSuite(TestPipeLineConnection))
    suite.addTest(unittest.makeSuite(TestControlBackend))
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    run_tests()