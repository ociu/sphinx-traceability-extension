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

   - More content
   - More again

     - And nested content
     - *other* with **emphasis** and
     - .. note:: a note

          Yes, a note

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
   
.. item:: r006 Depends on all
   :class: terciary
   :trace: r001
           r002
           r003 r005
	
   To demonstrate that bug #2 is solved
   
.. item:: r007 Depends on all with stereotypes
   :class: terciary
   :trace: <<covers>>    r001
           <<depends_on>>
           r002
           <<fulfills>>  r003
           r005
	
   To demonstrate stereotype usage in relationships


.. requirement:: r100 A requirement using the ``requirement`` type

   This item has been defined using other directive. It easily extends
   rst semantics


Item list
=========

List all items:

.. item-list::


List all items beginning with ``r00``

.. item-list::
   :filter: r00

List system requirements (beginning with SYS)

.. item-list::
   :filter: ^SYS

List all well-formed SYS and SRS requirements

.. item-list::
   :filter: ^S[YR]S_\d

Item matrix
===========

All relationships

.. item-matrix:: All

Traceability from SRS to SSS

.. item-matrix:: SRS to SSS
   :target: SYS
   :source: SRS
   :type:   fulfills
	    
Traceability from SSS to SRS

.. item-matrix:: SSS to SRS
   :target: SRS
   :source: SYS
   :type:   fulfilled_by


Links and references
====================

Item reference: :item:`r001`

:item:`Item reference with alternative text<r001>`

.. parsed-literal::

   This is literal text, to show
   that items can also be used in
   literals, such as code:

      Item reference: :item:`r001`

      :item:`Item reference with alternative text<r001>`

   Item links should be generated using parsed literal directive.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
