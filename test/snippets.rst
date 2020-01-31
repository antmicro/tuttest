RST file
=========

This is a nice *rst* file.

It's a `test <https://google.com>`_.

.. code-block:: python
   :name: something block

   def something(useless: str):
       a = 42
       print(a)

Suddenly, a paragraph.

1. Other code using a literal block inside a list - this will not be parsed as there is no way to pass metadata::

      def test():
          pass

   Another block that will be parsed. It is indented.

   .. code-block:: c++

      int main() {
          return 0;
      }
