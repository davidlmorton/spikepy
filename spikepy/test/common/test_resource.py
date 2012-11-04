#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import unittest
import uuid

from spikepy.common.trial_manager import Resource
from spikepy.common.errors import *

class ResourceTests(unittest.TestCase):
    name_1 = 'name_1'
    name_2 = 'name_2'
    data_2 = 'data_2'

    def setUp(self):
        self.r_1 = Resource(self.name_1)
        self.r_2 = Resource(self.name_2, data=self.data_2)

    def test_constructor(self):
        self.assertEqual(self.r_1.name, self.name_1)
        self.assertEqual(self.r_1._data, None)
        
        self.assertEqual(self.r_2.name, self.name_2)
        self.assertEqual(self.r_2._data, self.data_2)

    def test_checkout(self):
        self.assertEqual(self.r_2.is_locked, False)

        # perform checkout
        checkout_2 = self.r_2.checkout()

        # checkout results
        self.assertEqual(isinstance(checkout_2, dict), True)
        self.assertEqual(checkout_2['name'], self.name_2)
        self.assertEqual(checkout_2['data'], self.data_2)
        self.assertTrue(isinstance(checkout_2['locking_key'], uuid.UUID))

        # checkout status
        self.assertEqual(self.r_2.is_locked, True)
        self.assertRaises(ResourceLockedError, self.r_2.checkout)


    def test_checkin(self):
        # checkin before checkout raises error.
        self.assertRaises(ResourceNotLockedError, self.r_2.checkin)

        # perform checkout
        checkout_2 = self.r_2.checkout()

        # checkin without a key, rasies error
        self.assertRaises(InvalidLockingKeyError, self.r_2.checkin)

        # checkin with key works
        self.assertEqual(self.r_2.is_locked, True)
        self.r_2.checkin(key=checkout_2['locking_key'])
        self.assertEqual(self.r_2.is_locked, False)

    def test_checkin2(self):
        checkout_2 = self.r_2.checkout()

        data_dict = {'data':'checkin_data',
                     'change_info':{'with':{},
                                    'using':[]}}
        self.assertRaises(AssertionError, self.r_2.checkin, data_dict=data_dict,
                key=checkout_2['locking_key'])
        # since checkin failed, data should be unchanged...
        self.assertEqual(self.r_2.data, self.data_2)

        # fix the incomplete data_dict's 'change_info' and checkin
        data_dict['change_info']['by'] = 'test' # add last needed thing
        self.r_2.checkin(data_dict=data_dict, key=checkout_2['locking_key'])
        self.assertEqual(self.r_2.data, 'checkin_data')
        self.assertTrue('at' in self.r_2.change_info.keys())
        self.assertTrue('change_id' in self.r_2.change_info.keys())
