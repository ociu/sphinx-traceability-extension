#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An exemplary test code module.
"""

import unittest
from prod_code import Animal, Cat, Dog


class TestAnimal(unittest.TestCase):

    def test_abstract_method_shall_raise_error(self):
        """
        .. item:: SW_TEST_002 The abstract method shall raise a
                              NotImplementedError.
            :validates: SW_REQ_002
        """
        a = Animal('unspecific animal')
        self.assertRaises(NotImplementedError, a.talk())


class TestCat(unittest.TestCase):

    def test_cat_shall_inherit_from_animal(self):
        """
         .. item:: SW_TEST_003 The "cat" class shall have the animal class as
                              superclass.
            :validates: SW_REQ_003
        """
        c = Cat('amy')
        self.assertTrue(issubclass(c, Animal))

    def test_cat_shall_meow(self):
        """
        .. item:: SW_TEST_004 The concrete implementation of the "cat" class
                              method "talk" shall return "Meow!".
            :validates: SW_REQ_004
        """
        c = Cat('amy')
        self.assertEqual('Meow!', c.talk())


class TestDog(unittest.TestCase):

    def test_dog_shall_bark(self):
        """
        .. item:: SW_TEST_006 The concrete implementation of the "dog" class
                              method "talk" shall return "Woof!".
            :validates: SW_REQ_006
        """
        d = Dog('bulli')
        self.assertEqual('Woof!', d.talk())
