RST file
=========

This is a nice *rst* file.

It's a `test <https://google.com>`_.

.. code-block:: python

   def something(useless: str):
       a = 42
       print(a)

..
    meta: name="something"

Suddenly, a paragraph.

1. Other code using a literal block inside a list::

      def test():
          pass

   Another block that will be parsed. It is indented.

   .. code-block:: c++

      int main() {
          return 0;
      }
