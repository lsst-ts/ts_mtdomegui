.. py:currentmodule:: lsst.ts.mtdomegui

.. _lsst.ts.mtdomegui-version_history:

##################
Version History
##################

.. _lsst.ts.mtdomegui-0.6.1:

-------------
0.6.1
-------------

* Adapt the **ts_mtdomecom** to use the **LlcName.LLC**.

.. _lsst.ts.mtdomegui-0.6.0:

-------------
0.6.0
-------------

* Add the ``tab_brake.py``.
* Check the engaged brakes.
* Support the control status of control system.
* Support the state, motion state, and fault error code in the rear access door and calibration screen.
* Add the ``documenteer.toml``.
* Update the ``Jenkinsfile`` to remove the ``use_pyside6`` option, which is the default value.
* Sort the Python scripts to put the lsst to an individual section.

.. _lsst.ts.mtdomegui-0.5.7:

-------------
0.5.7
-------------

* Deal with the **ResponseCode.NOT_CONNECTED**.

.. _lsst.ts.mtdomegui-0.5.6:

-------------
0.5.6
-------------

* Adapt the **ts_mtdomecom** to read the enabled louvers from the **ts_config_mttcs**.

.. _lsst.ts.mtdomegui-0.5.5:

-------------
0.5.5
-------------

* Adapt the qasync v0.28.0.
* Reformat by ruff.

.. _lsst.ts.mtdomegui-0.5.4:

-------------
0.5.4
-------------

* Adapt the schema on summit. Remove the workaround.

.. _lsst.ts.mtdomegui-0.5.3:

-------------
0.5.3
-------------

* Add the ``string`` in the build section of ``meta.yaml``.

.. _lsst.ts.mtdomegui-0.5.2:

-------------
0.5.2
-------------

* Report the louvers control system to be Enabled once there is the connection.

.. _lsst.ts.mtdomegui-0.5.1:

-------------
0.5.1
-------------

* Improve the ``test_application.py``.
* Assign the qasync version in ``meta.yaml``.

.. _lsst.ts.mtdomegui-0.5.0:

-------------
0.5.0
-------------

* Adapt the **ts_mtdomecom** v0.3.0.
* Support the louver control system.
* Show the temperatures of the cabinet, motor drive, and motor coils in the thermal control system.
* Update the screenshots of the azimuth, thermal, louver, and command tables.
* Update the ``user-guide.rst`` and ``class_tab_louver.md``.

.. _lsst.ts.mtdomegui-0.4.14:

-------------
0.4.14
-------------

* Remove the temperatures in **TabAzimuth**.
* Update the temperature sensors in **TabThermalSystem** to have the motor drive, motor coil, and cabinet.
* Adapt the latest **ts_mtdomecom** for the constants.

.. _lsst.ts.mtdomegui-0.4.13:

-------------
0.4.13
-------------

* Simplify the ``setup.py``.
* Adapt the **ts_mtdomecom** v0.2.13.

.. _lsst.ts.mtdomegui-0.4.12:

-------------
0.4.12
-------------

* Ensure that aperture shutter InPosition is correct.

.. _lsst.ts.mtdomegui-0.4.11:

-------------
0.4.11
-------------

* Improve the disconnection and failed communication with the rotating cRIO.

.. _lsst.ts.mtdomegui-0.4.10:

-------------
0.4.10
-------------

* Add the **QT_QPA_PLATFORM** to ``meta.yaml`` to fix the test section of conda recipe.

.. _lsst.ts.mtdomegui-0.4.9:

-------------
0.4.9
-------------

* Support the DC bus voltage of capacitor banks.

.. _lsst.ts.mtdomegui-0.4.8:

-------------
0.4.8
-------------

* Improve the ``setup.py`` to support the version of Python 3.11 and 3.12.
* Improve the document of capacitor bank.

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
