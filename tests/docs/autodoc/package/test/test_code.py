# -*- coding: utf-8 -*-

import unittest
from prod_code import Animal


class TestAnimal(unittest.TestCase):

    def test_abstract_method_shall_raise_error(self):
        """
        .. item:: SW_TEST_002
            :addresses: SW_REQ_002

            The abstract method shall raise a NotImplementedError.
        """
        a = Animal('unspecific animal')
        self.assertRaises(NotImplementedError, a.talk())


class TestCat(unittest.TestCase):

    def test_cat_shall_meow(self):
        """
        .. item:: SW_TEST_004
            :addresses: SW_REQ_004

            The concrete implementation of the "cat" class method "talk" shall return "Meow!".
        """
        c = Cat()
        self.assertEqual('Meow!', c.talk())


class TestDog(unittest.TestCase):

    def test_dog_shall_bark(self):
        """
        .. item:: SW_TEST_004
            :addresses: SW_REQ_004

            The concrete implementation of the "dog" class method "talk" shall return "Woof!".
        """
        d = Dog()
        self.assertEqual('Woof!', d.talk())
