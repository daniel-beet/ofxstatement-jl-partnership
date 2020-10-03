~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
John Lewis Partnership Card plugin for ofxstatement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`ofxstatement`_ is a tool to convert proprietary bank statement to OFX format,
suitable for importing to GnuCash. Plugin for ofxstatement parses a
particular proprietary bank statement format and produces common data
structure, that is then formatted into an OFX file.

.. _ofxstatement: https://github.com/kedder/ofxstatement


Users of ofxstatement have developed several plugins for their banks. They are
listed on main `ofxstatement`_ site. If your bank is missing, you can develop
your own plugin.

Usage
=====

  $ ofxstatement convert -t jlpartnership input.csv output.ofx

Development / Test
==================

``ofxstatemnt`` uses `pipenv`_ to manage the development environment and
dependencies::

  $ pip install pipenv
  $ pipenv sync --dev

.. _pipenv: https://github.com/pypa/pipenv

And finally run the test suite::

  $ pipenv shell
  $ pytest

Or use make:
  $ make

Package tgz for pip install:
  $ python setup.py sdist


When satisfied, you may create a pull request.