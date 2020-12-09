================
sphinx-tabs test
================

Sphinx tabs is a sphinx extension that provides special `.. tabs::` directive,
which can produce nicely-looking tables with code snippets in separate tabs.
This can be used to provide the information dedicated, i.e.,
to different OS-es in a more concise way.

In example the following code snippets:

.. code-block:: bash
   :name: Ubuntu prerequisites

   apt install wget

.. code-block:: bash
   :name: CentOS prerequisites

   yum install wget


Can be substituted with:

.. tabs::

   .. group-tab:: Ubuntu
      :name: ubuntu-prerequisites

      apt install wget

   .. group-tab:: CentOS
      :name: centos-prerequisites

      yum install wget
