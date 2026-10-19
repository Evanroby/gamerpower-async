Installation
============

Requirements
------------

- Python 3.11 or newer
- ``httpx`` 0.27 or newer, installed automatically

Install
-------

From a source checkout::

    pip install .

When the package is published on PyPI, it will install with::

    pip install gamerpower-async

The import name is ``gamerpower``:

.. code-block:: python

   import gamerpower

   print(gamerpower.__version__)

Building these docs
-------------------

The documentation uses `Sphinx <https://www.sphinx-doc.org>`_ with the
`Furo <https://pradyunsg.me/furo/>`_ theme. From the project root::

    pip install -e ".[docs]"
    python -m sphinx -b html docs docs/_build/html

Then open ``docs/_build/html/index.html``. Read the Docs builds the same way, using
``.readthedocs.yaml``.
