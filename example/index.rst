.. Example documentation master file, created by
   sphinx-quickstart on Sat Sep  7 17:17:38 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Example's documentation!
===================================

Contents:

.. toctree::
   :maxdepth: 1

   SRS
   SSS

.. item:: r001 First requirement
   :class: functional requirement

   This is one item

.. item:: r002
   :class: critical

   We have to extend this section

This text is not part of any item

.. item:: r003 The great
   :class: secondary
   :trace: r002

   Clean up all this.

.. item:: r005 Another
   :class: terciary
   :trace: r002 r003

   Clean up all this again
   

Item list
=========

.. itemlist::


Links and references
====================

Item reference: :item:`r001`

:item:`Item reference with alternative text<r001>`


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
