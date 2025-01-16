.. _Developer_Guide:

#########################
Developer Guide
#########################

This GUI is constructed on the top of Qt framework (`Qt for Python <https://wiki.qt.io/Qt_for_Python>`_).

.. _Dependencies:

Dependencies
============

* `ts_xml <https://github.com/lsst-ts/ts_xml>`_
* `ts_guitool <https://github.com/lsst-ts/ts_guitool>`_
* `ts_mtdomecom <https://github.com/lsst-ts/ts_mtdomecom>`_

.. _Architecture:

Architecture
=============

The classes in module are listed below.

.. _lsst.ts.mtdomegui-modules_mtdomegui:

mtdomegui
---------

.. mermaid:: ../uml/class_mtdomegui.mmd
    :caption: Class diagram of dome GUI

* **MainWindow** is the main window of the application.
* **Model** contains the main business logic in the application.
* **ControlPanel** shows the current system status.
* **Status** is a data class that has the current controller status.
* **Reporter** reports the system status and telemetry.

The model–view–controller (MVC) architecture is used in this module.
In this design, the view always shows the data sent from the model.
This helps minimize the business logic in view and makes testing easier.

The `Qt signal <https://doc.qt.io/qt-6/signalsandslots.html>`_ is used to do the data exchange.
The `emit()` and `connect()` in the class diagrams mean the class **emits** a specific signal and **connects** it to a specific callback function.
Signals are held and emitted from the **Model** to simplify the management of signals.

Qt provides its event loop that is different from the event loop in Python `asyncio <https://docs.python.org/3/library/asyncio.html>`_ library.
The `qasync <https://github.com/CabbageDevelopment/qasync>`_ allows coroutines (`async/await` keywords) to be used in PyQt/PySide applications by providing an implementation of the PEP-3156 event-loop.
For the other tasks in a loop to run, an awaitable must be called from another coroutine.
This allow for the coroutine to claim CPU and performs its operations.
Therefore `await asyncio.sleep()` calls are placed in unit tests calls, so the signal handling etc. can occur.

.. _lsst.ts.mtdomegui-modules_mtdomegui_signals:

mtdomegui.signals
-----------------

The available Qt signals are listed below:

* **SignalInterlock** sends the current interlock status.
* **SignalState** sends the current state..
* **SignalOperationalMode** sends the current operational mode.
* **SignalTelemetry** sends the telemetry.
* **SignalTarget** sends the target.
* **SignalMotion** sends the motion status.
* **SignalFaultCode** sends the fault code.

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab:

mtdomegui.tab
-------------

.. mermaid:: ../uml/tab/class_tab.mmd
    :caption: Class diagram of tab module

* **TabApertureShutter** shows the aperture shutter status.
* **TabAzimuth** shows the azimuth status.
* **TabCalibration** shows the calibration screen status.
* **TabCommand** shows the avaiable commands to the controller.
* **TabElevation** shows the elevation (light/wind screen) status.
* **TabFigure** shows the real-time figure.
* **TabInterlock** shows the interlock status.
* **TabLouver** shows the louver status.
* **TabLouverSingle** shows the single louver status that is selected in **TabLouver**.
* **TabRearAccessDoor** shows the rear access door status.
* **TabSelector** shows the selections used in the **TabCommand** and **TabThermalSystem**.
* **TabSettings** shows the settings of GUI.
* **TabThermalSystem** shows the thermal system status.
* **TabUtility** shows the utility status.

The class diagrams for each table class are listed below to give you the idea of class relationship.

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_aperture_shutter:

mtdomegui.tab.TabApertureShutter
--------------------------------

.. mermaid:: ../uml/tab/class_tab_aperture_shutter.mmd
    :caption: Class diagram of TabApertureShutter class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_azimuth:

mtdomegui.tab.TabAzimuth
------------------------

.. mermaid:: ../uml/tab/class_tab_azimuth.mmd
    :caption: Class diagram of TabAzimuth class


.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_calibration:

mtdomegui.tab.TabCalibration
----------------------------

.. mermaid:: ../uml/tab/class_tab_calibration.mmd
    :caption: Class diagram of TabCalibration class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_command:

mtdomegui.tab.TabCommand
------------------------

.. mermaid:: ../uml/tab/class_tab_command.mmd
    :caption: Class diagram of TabCommand class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_elevation:

mtdomegui.tab.TabElevation
--------------------------

.. mermaid:: ../uml/tab/class_tab_elevation.mmd
    :caption: Class diagram of TabElevation class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_figure:

mtdomegui.tab.TabFigure
-----------------------

.. mermaid:: ../uml/tab/class_tab_figure.mmd
    :caption: Class diagram of TabFigure class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_interlock:

mtdomegui.tab.TabInterlock
--------------------------

.. mermaid:: ../uml/tab/class_tab_interlock.mmd
    :caption: Class diagram of TabInterlock class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_louver:

mtdomegui.tab.TabLouver
-----------------------

.. mermaid:: ../uml/tab/class_tab_louver.mmd
    :caption: Class diagram of TabLouver class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_louver_single:

mtdomegui.tab.TabLouverSingle
-----------------------------

.. mermaid:: ../uml/tab/class_tab_louver_single.mmd
    :caption: Class diagram of TabLouverSingle class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_rear_access_door:

mtdomegui.tab.TabRearAccessDoor
-------------------------------

.. mermaid:: ../uml/tab/class_tab_rear_access_door.mmd
    :caption: Class diagram of TabRearAccessDoor class


.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_selector:

mtdomegui.tab.TabSelector
-------------------------

.. mermaid:: ../uml/tab/class_tab_selector.mmd
    :caption: Class diagram of TabSelector class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_settings:

mtdomegui.tab.TabSettings
-------------------------

.. mermaid:: ../uml/tab/class_tab_settings.mmd
    :caption: Class diagram of TabSettings class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_thermal_system:

mtdomegui.tab.TabThermalSystem
------------------------------

.. mermaid:: ../uml/tab/class_tab_thermal_system.mmd
    :caption: Class diagram of TabThermalSystem class

.. _lsst.ts.mtdomegui-modules_mtdomegui_tab_utility:

mtdomegui.tab.TabUtility
------------------------

.. mermaid:: ../uml/tab/class_tab_utility.mmd
    :caption: Class diagram of TabUtility class

.. _API:

APIs
=============

This section is autogenerated from docstrings.

.. automodapi:: lsst.ts.mtdomegui
    :no-inheritance-diagram:
