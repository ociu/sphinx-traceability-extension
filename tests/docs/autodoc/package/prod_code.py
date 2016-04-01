# -*- coding: utf-8 -*-


class Animal(object):
    """
    Animal "interface".

    .. item:: SW_REQ_001
       #:validated_by: SW_TEST_001
       #:impacts_on: SW_REQ_003 SW_REQ_005
       :trace: SW_TEST_001

       The software shall provide an abstract animal interface.
    """
    def __init__(self, name):
        self.name = name

    def talk(self):
        """
        "Abstract" interface method.

        .. item:: SW_REQ_002
            #:tested_by: SW_TEST_002
            #:impacts_on: SW_REQ_004 SW_REQ_006
            :trace: SW_TEST_002

            The abstract animal interface shall provide an abstract method "talk".
        """
        raise NotImplementedError("Subclass must implement abstract method")


class Cat(Animal):
    """
    Animal cat "implementation"

    .. item:: SW_REQ_003
        #:implements: SW_REQ_001
        #:tested_by: SW_TEST_003
        #:allocated_to: SW_CSU_002
        :trace: SW_TEST_003

        A "cat" class shall implement the abstract animal interface.
        """
    def talk(self):
        """
        Cat implementation of the "interface" method.

        .. item:: SW_REQ_004
            #:implements: SW_REQ_002
            #:tested_by: SW_TEST_004
            #:allocated_to: SW_CSU_002
            :trace: SW_TEST_004

            The "cat" class shall implement the abstract animal interface method.
        """
        return 'Meow!'


class Dog(Animal):
    """
    Animal dog "implementation"

    .. item:: SW_REQ_005
        #:implements: SW_REQ_001
        #:tested_by: SW_TEST_005
        #:allocated_to: SW_CSU_003
        :trace: SW_TEST_005

        A "dog" class shall implement the abstract animal interface.
    """

    def talk(self):
        """
        Dog implementation of the "interface" method.

        .. item:: SW_REQ_006
            #:implements: SW_REQ_002
            #:tested_by: SW_TEST_006
            #:allocated_to: SW_CSU_003
            :trace: SW_TEST_006

            The "dog" class shall implement the abstract animal interface method.
        """
        return 'Woof!'
