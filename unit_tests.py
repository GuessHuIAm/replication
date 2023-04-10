import unittest
from unittest.mock import MagicMock

import inquirer

from client import *
from constants import *
from server import *


class TestServerMethods(unittest.TestCase):
    mock_client = MagicMock()

    def test_Validate_input_Happy_case_Returns_True(self):
        self.assertTrue(validate_input('hello'))

    def test_Validate_input_Contains_illegal_char_Throws_error(self):
        with self.assertRaises(inquirer.errors.ValidationError):
            validate_input('h*llo?')

    def test_Validate_ip_Happy_case_Returns_True(self):
        self.assertTrue(validate_ip('192.91.202.3'))

    def test_Validate_ip_Invalid_address_Throws_error(self):
        with self.assertRaises(inquirer.errors.ValidationError):
            validate_ip('1.123.3.ajsdf')

    def test_Validate_user_User_found_Returns_True(self):
        username = 'yessir'
        self.__class__.mock_client.list_accounts(username).__str__.return_value = f'usernames: "{username}"'
        self.assertTrue(validate_user(username, self.__class__.mock_client))

    def test_Validate_user_Fails_val_input_Throws_error(self):
        with self.assertRaises(inquirer.errors.ValidationError):
            validate_user('h*llo?', self.__class__.mock_client)

    def test_Validate_user_DNE_Throws_error(self):
        self.__class__.mock_client.list_accounts(str).__str__.return_value = 'usernames: ""'
        with self.assertRaises(inquirer.errors.ValidationError):
            validate_user('asdfk', self.__class__.mock_client)

    def test_Validate_regex_Happy_case_Returns_True(self):
        self.assertTrue(validate_regex('.*asdfkj'))

    def test_Validate_regex_Invalid_regex_Throws_error(self):
        with self.assertRaises(inquirer.errors.ValidationError):
            validate_regex('*\\')

if __name__ == '__main__':
    unittest.main()