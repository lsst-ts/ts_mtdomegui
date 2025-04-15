# This file is part of ts_mtdomegui.
#
# Developed for the Vera Rubin Observatory Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = [
    "SignalInterlock",
    "SignalState",
    "SignalOperationalMode",
    "SignalTelemetry",
    "SignalTarget",
    "SignalMotion",
    "SignalFaultCode",
    "SignalConfig",
]

from PySide6 import QtCore


class SignalInterlock(QtCore.QObject):
    """Interlock signal to send the current interlock status."""

    # List of the safety interlock status. This should be the same as the
    # "MTDome_interlocks" in ts_xml. But I found another
    # "MTDome_logevent_interlocks" topic. Need to check the difference
    # TODO: DM-48348.
    #
    # In addition, this should be related to the dictionary object defined in
    # the "moncs_status.py" in ts_mtdomecom.
    interlock = QtCore.Signal(object)

    # Bitmask of the locking pins that have been engaged. This is not fully
    # defined yet. See the "MTDome_logevent_lockingPinsEngaged" in ts_xml.
    locking_pins_engaged = QtCore.Signal(int)


class SignalState(QtCore.QObject):
    """State signal to send the current state."""

    # Bitmask of the brakes that are engaged. This is not fully defined yet.
    # See the "MTDome_logevent_brakesEngaged" in ts_xml.
    brake_engaged = QtCore.Signal(int)

    # State of the azimuth axis as the enum of
    # `lsst.ts.xml.enums.MTDome.EnabledState`.
    azimuth_axis = QtCore.Signal(int)

    # State of the elevation axis as the enum of
    # `lsst.ts.xml.enums.MTDome.EnabledState`.
    elevation_axis = QtCore.Signal(int)

    # State of the aperature shutter as the enum of
    # `lsst.ts.xml.enums.MTDome.EnabledState`.
    aperture_shutter = QtCore.Signal(int)

    # Power mode as the enum of `lsst.ts.xml.enums.MTDome.PowerManagementMode`.
    power_mode = QtCore.Signal(int)


class SignalOperationalMode(QtCore.QObject):
    """Operational mode signal to send the current operational mode of each
    control system.

    A tuple of (subsystem, mode) with the enums defined in
    `lsst.ts.xml.enums.MTDome.SubSystemId` and
    `lsst.ts.xml.enums.MTDome.OperationalMode`.
    """

    subsystem_mode = QtCore.Signal(object)


class SignalTelemetry(QtCore.QObject):
    """Telemetry signal to send the telemetry of each control system."""

    # Dictionary object defined in the "amcs_status.py" in ts_mtdomecom.
    amcs = QtCore.Signal(object)

    # Dictionary object defined in the "apscs_status.py" in ts_mtdomecom.
    apscs = QtCore.Signal(object)

    # Dictionary object defined in the "cbcs_status.py" in ts_mtdomecom (as the
    # event).
    cbcs = QtCore.Signal(object)
    # DC bus voltage of the capacitor bank in Volt.
    cbcs_voltage = QtCore.Signal(float)

    # Dictionary object defined in the "cscs_status.py" in ts_mtdomecom.
    cscs = QtCore.Signal(object)

    # Dictionary object defined in the "lcs_status.py" in ts_mtdomecom.
    lcs = QtCore.Signal(object)

    # Dictionary object defined in the "lwscs_status.py" in ts_mtdomecom.
    lwscs = QtCore.Signal(object)

    # Dictionary object defined in the "rad_status.py" in ts_mtdomecom.
    rad = QtCore.Signal(object)

    # Dictionary object defined in the "thcs_status.py" in ts_mtdomecom.
    thcs = QtCore.Signal(object)


class SignalTarget(QtCore.QObject):
    """Target signal to send the current target.

    A tuple of (position, velocity) in deg and deg/sec.
    """

    position_velocity_azimuth = QtCore.Signal(object)
    position_velocity_elevation = QtCore.Signal(object)


class SignalMotion(QtCore.QObject):
    """Motion signal to send the current motion state.

    A tuple of (motion_state, in_position). "motion_state" is an enum
    `lsst.ts.xml.enums.MTDome.MotionState`. "in_position" is a boolean value.

    Note for the "aperture_shutter", it would be (motion_states, in_positions),
    which means both of the elements are list.
    """

    azimuth_axis = QtCore.Signal(object)
    elevation_axis = QtCore.Signal(object)
    aperture_shutter = QtCore.Signal(object)


class SignalFaultCode(QtCore.QObject):
    """Fault code signal to send the current fault condition."""

    azimuth_axis = QtCore.Signal(str)
    elevation_axis = QtCore.Signal(str)
    aperture_shutter = QtCore.Signal(str)


class SignalConfig(QtCore.QObject):
    """Config signal to send the current configuration."""

    # Configuration dictionary of the azimuth motion control system (AMCS).
    amcs = QtCore.Signal(object)

    # Configuration dictionary of the light and wind screen control system
    # (LWSCS).
    lwscs = QtCore.Signal(object)
