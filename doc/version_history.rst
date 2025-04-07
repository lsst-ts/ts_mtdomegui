.. py:currentmodule:: lsst.ts.mtdomegui

.. _lsst.ts.mtdomegui-version_history:

##################
Version History
##################

.. _lsst.ts.mtdomegui-0.4.7:

-------------
0.4.7
-------------

* Get the status of thermal control system.
* Use the first 5 elements of the azimuth temperature telemetry.

.. _lsst.ts.mtdomegui-0.4.6:

-------------
0.4.6
-------------

* Remove the ``wrap_callbacks_with_async_task`` argument when calling ``MTDomeCom()``.

.. _lsst.ts.mtdomegui-0.4.5:

-------------
0.4.5
-------------

* Update the ``TabSettings._callback_apply_amcs()`` and ``TabSettings._callback_apply_lwscs()`` to disable and enable the command button in the running of command.
* Add the **error_handling.rst** and **capacitor-bank.rst**.

.. _lsst.ts.mtdomegui-0.4.4:

-------------
0.4.4
-------------

* Update the ``TabCommand._callback_send_command()`` to disable and enable the command button in the running of command.
* Do not wrap the callback functions in the **MTDomeCom**.

.. _lsst.ts.mtdomegui-0.4.3:

-------------
0.4.3
-------------

* Allow to query the shutter status.
* Fix the unit of position of the shutter.
* Change the torque unit to be N*m instead of J.

.. _lsst.ts.mtdomegui-0.4.2:

-------------
0.4.2
-------------

* Add the user guide.

.. _lsst.ts.mtdomegui-0.4.1:

-------------
0.4.1
-------------

* Fix the received NaN in the azimuth table when crawing.

.. _lsst.ts.mtdomegui-0.4.0:

-------------
0.4.0
-------------

* Add the **SignalConfig**.
* Fix the **TabAperatureShutter** that the motion state and in-position are list.
* Update the **Reporter** to report the configuration and **TabSettings** to show the configuration.
* Support the TCP/IP communication with the controller.
* Update the **MainWindow** to connect/disconnect the controller.
* Read the configuration from **ts_config_mttcs**.

.. _lsst.ts.mtdomegui-0.3.0:

-------------
0.3.0
-------------

* Add the **reporter.py**.
* Add the signals of events.
* Adapt the constants in **ts_mtdomecom**.

.. _lsst.ts.mtdomegui-0.2.0:

-------------
0.2.0
-------------

* Add the dependencies of **ts_mtdomecom** and **ts_config_mttcs**.
* Remove the **enums.py** and use the enums in **ts_mtdomecom** instead.
* Add the **status.py** and **signals.py**.
* Support the telemetry related signals.
* Update the UML diagrams.

.. _lsst.ts.mtdomegui-0.1.0:

-------------
0.1.0
-------------

* Initial framework.
