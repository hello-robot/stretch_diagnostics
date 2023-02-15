#!/usr/bin/env python3

from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import requests
import socket
class Test_SIMPLE_wifi(unittest.TestCase):
    """
    Test if Wifi is working reliably
    """
    test = TestBase('test_SIMPLE_wifi')


    def test_wifi_on(self):
        """
        Test that WiFi is on and internet connection works
        """
        try:
            s = socket.create_connection(("www.hello-robot.com", 80))
            if s is not None:
                s.close()
        except OSError:
            self.assertTrue(False,msg='Internet connection is bad. Check Wifi settings')



test_suite = TestSuite(test=Test_SIMPLE_wifi.test,failfast=False)
test_suite.addTest(Test_SIMPLE_wifi('test_wifi_on'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
