import os
import unittest
from os.path import join as pjoin

import jericho


class TestJericho(unittest.TestCase):
    def test_load_bindings(self):
        self.assertRaises(ValueError, jericho.load_bindings, "")
        data1 = jericho.load_bindings("905")
        data2 = jericho.load_bindings("905.z5")
        assert data1 == data2
