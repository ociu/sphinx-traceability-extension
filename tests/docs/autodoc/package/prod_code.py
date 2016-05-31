#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An exemplary production code module.
"""


class Animal(object):
    """
    Animal "interface".

    .. item:: SW_REQ_001 The software shall provide an abstract animal interface.
       :validated_by: SW_TEST_001
       :impacts_on: SW_REQ_003 SW_REQ_005
    """
    def __init__(self, name):
        self.name = name

    def talk(self):
        """
        "Abstract" interface method.

        .. item:: SW_REQ_002 The abstract animal interface shall provide an
                             abstract method "talk".
            :validated_by: SW_TEST_002
            :impacts_on: SW_REQ_004 SW_REQ_006
        """
        raise NotImplementedError("Subclass must implement abstract method")


class Cat(Animal):
    """
    Animal cat "implementation"

    .. item:: SW_REQ_003 A "cat" class shall implement the abstract animal
                         interface.
        :implements: SW_REQ_001
        :validated_by: SW_TEST_003
    """
    def talk(self):
        """
        Cat implementation of the "interface" method.

        .. item:: SW_REQ_004 The "cat" class shall implement the abstract animal
                             interface method.
            :implements: SW_REQ_002
            :validated_by: SW_TEST_004
        """
        return 'Meow!'


class Dog(Animal):
    """
    Animal dog "implementation"

    .. item:: SW_REQ_005 A "dog" class shall implement the abstract animal interface.
        :implements: SW_REQ_001
        :validated_by: SW_TEST_005
    """

    def talk(self):
        """
        Dog implementation of the "interface" method.

        .. item:: SW_REQ_006 The "dog" class shall implement the abstract animal
                             interface method.
            :implements: SW_REQ_002
            :validated_by: SW_TEST_006
        """
        return 'Woof!'
