.. |developer| replace:: *Te-Wei Tsai <ttsai@lsst.org>*

.. Note that the ts_ prefix is omitted from the title

########################
Dome GUI
########################

.. image:: https://img.shields.io/badge/GitHub-ts__mtdomegui-green.svg
    :target: https://github.com/lsst-ts/ts_mtdomegui
.. image:: https://img.shields.io/badge/Jenkins-ts__mtdomegui-green.svg
    :target: https://tssw-ci.lsst.org/job/LSST_Telescope-and-Site/job/ts_mtdomegui

.. _Overview:

Overview
========

This module is the MTDome Python QT-based GUI.
The `eups <https://github.com/RobertLuptonTheGood/eups>`_ is used as the package manager.
This package also supports the `conda <https://docs.conda.io/en/latest>`_ package manager.

The badges above navigate to the GitHub repository for the tool code.

.. _User_Documentation:

User Documentation
==================

Observatory operators and other interested parties should consult the user guide for insights into the main telescope dome GUI operations.

.. toctree::
    user-guide/user-guide
    :maxdepth: 1

.. toctree::
    user-guide/capacitor-bank
    :maxdepth: 1

.. _Error_Handling_Documentation:

Error Handling Documentation
============================

The possible error of MT dome and the related handling to recover the system are recorded here.

.. toctree::
    error-handling/error-handling
    :maxdepth: 1

.. _Development_Documentation:

Development Documentation
=========================

Classes and their methods are described in this section.

.. toctree::
    developer-guide/developer-guide
    :maxdepth: 1

.. _Version_History:

Version History
===============

The version history is at the following link.

.. toctree::
    version_history
    :maxdepth: 1

The released version is `here <https://github.com/lsst-ts/ts_mtdomegui/releases>`_.

.. _Contributing:

Contributing
============

To contribute, please start a new pull request on `GitHub <https://github.com/lsst-ts/ts_mtdomegui>`_.
Feature requests shall be filled in JIRA with the *ts_mtdomegui* label.
In all cases, reaching out to the :ref:`contacts for this repo <Contact_Personnel>` is recommended.

.. _Contact_Personnel:

Contact Personnel
=================

For questions not covered in the documentation, emails should be addressed to the developer: |developer|.

This page was last modified |today|.
