sksundae.common
===============

.. py:module:: sksundae.common


Classes
-------

.. autoapisummary::

   sksundae.common.RichResult


Module Contents
---------------

.. py:class:: RichResult(**kwargs)

   Output container with pretty printing.

   This class is a modified copy of ``_RichResult`` from the ``scipy``
   library. It combines a series of formatting functions to make the
   printed 'repr' easy to read. Use this class directly by passing in
   any number of keyword arguments, or use it as a base class to have
   custom classes for different result types.

   Inheriting classes should define the class attribute ``_order_keys``
   which is a list of strings that defines how output fields are sorted
   when an instance is printed.

   :param \*\*kwargs: User-specified keyword arguments. Any number of arguments can be
                      given as input. The class simply stores the key/value pairs, makes
                      them accessible as attributes, and provides pretty printing.
   :type \*\*kwargs: dict, optional

   .. rubric:: Examples

   The example below demonstrates how to define the ``_order_keys`` class
   attribute for custom sorting. If arguments are not in the list, they
   are placed at the end based on the order they were given. Note that
   ``_order_keys`` only provides sorting support and that no errors are
   raised if an argument is not present, e.g., ``third`` below.

   .. code-block:: python

       import sundae as sun

       class CustomResult(sun.common.RichResult):
           _order_keys = ['first', 'second', 'third',]

       result = CustomResult(second=None, last=None, first=None)
       print(result)

   ``RichResult`` can also be used directly, without any custom sorting.
   Arguments will print based on the order they were input. Instances will
   still have a fully formatted 'repr', including formatted arrays.

   .. code-block:: python

       import numpy as np
       from sundae.common import RichResult

       t = np.linspace(0, 1, 1000)
       y = np.random.rand(1000, 5)

       y[0] = np.inf
       y[-1] = np.nan

       result = RichResult(message='Example.', status=0, t=t, y=y)
       print(result)

   After initialization, all key/value pairs are accessible as instance
   attributes.

   .. code-block:: python

       from sundae.common import RichResult

       result = RichResult(a=10, b=20, c=30)

       print(result.a*(result.b + result.c))


