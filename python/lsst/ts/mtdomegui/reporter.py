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

__all__ = ["Reporter"]

import logging

# TODO: OSW-1538, remove the ControlMode after the ts_xml: 24.4.
from lsst.ts.mtdomecom import APSCS_NUM_SHUTTERS, LCS_NUM_LOUVERS, RAD_NUM_DOORS, ControlMode
from lsst.ts.mtdomecom.schema import registry
from lsst.ts.xml.enums import MTDome

from .signals import (
    SignalConfig,
    SignalFaultCode,
    SignalInterlock,
    SignalMotion,
    SignalOperationalMode,
    SignalState,
    SignalTarget,
    SignalTelemetry,
)
from .status import Status
from .utils import generate_dict_from_registry


class Reporter:
    """Report class to report the system status.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    status : `Status`
        System status.
    signals : `dict`
        Signals.
    """

    def __init__(self, log: logging.Logger) -> None:
        self.log = log

        self.status = Status()
        self.signals = {
            "interlock": SignalInterlock(),
            "state": SignalState(),
            "operational_mode": SignalOperationalMode(),
            "telemetry": SignalTelemetry(),
            "target": SignalTarget(),
            "motion": SignalMotion(),
            "fault_code": SignalFaultCode(),
            "config": SignalConfig(),
        }

    def report_default(self) -> None:
        """Report the default status."""

        self.signals["interlock"].interlock.emit(self.status.interlocks)  # type: ignore[attr-defined]
        self.report_state_locking_pins_engaged(0)

        self.report_state_brake_engaged(0)
        self.report_state_azimuth_axis(MTDome.EnabledState.DISABLED)
        self.report_state_elevation_axis(MTDome.EnabledState.DISABLED)
        self.report_state_aperture_shutter(MTDome.EnabledState.DISABLED)
        self.report_state_louvers(MTDome.EnabledState.DISABLED)
        self.report_state_rear_access_door(MTDome.EnabledState.DISABLED)
        self.report_state_calibration_screen(MTDome.EnabledState.DISABLED)

        self.report_state_power_mode(MTDome.PowerManagementMode.NO_POWER_MANAGEMENT)
        self.report_state_control_mode(ControlMode.Remote)

        for subsystem in MTDome.SubSystemId:
            self.report_operational_mode(subsystem, MTDome.OperationalMode.NORMAL)

        self.report_telemetry("cbcs", self.status.capacitor_bank)
        self.signals["telemetry"].cbcs_voltage.emit(0.0)  # type: ignore[attr-defined]

        for component in ["AMCS", "LWSCS", "ApSCS", "LCS", "ThCS", "RAD", "CSCS"]:
            self.report_telemetry(component.lower(), generate_dict_from_registry(registry, component))

        self.report_target_azimuth(0.0, 0.0)
        self.report_target_elevation(0.0, 0.0)

        self.report_motion_azimuth_axis(MTDome.MotionState.STOPPED, False)
        self.report_motion_elevation_axis(MTDome.MotionState.STOPPED, False)
        self.report_motion_aperture_shutter(
            [MTDome.MotionState.STOPPED] * APSCS_NUM_SHUTTERS,
            [False] * APSCS_NUM_SHUTTERS,
        )
        self.report_motion_louvers(
            [MTDome.MotionState.STOPPED] * LCS_NUM_LOUVERS,
            [False] * LCS_NUM_LOUVERS,
        )
        self.report_motion_rear_access_door(
            [MTDome.MotionState.STOPPED] * RAD_NUM_DOORS,
            [False] * RAD_NUM_DOORS,
        )
        self.report_motion_calibration_screen(MTDome.MotionState.STOPPED, False)

    def report_interlocks(self, interlocks: list[bool]) -> None:
        """Report the interlocks.

        Parameters
        ----------
        interlocks : `list` [`bool`]
            Status of the interlocks. True is latched. Otherwise, False.
        """

        if self.status.interlocks != interlocks:
            self.status.interlocks = interlocks
            self.signals["interlock"].interlock.emit(interlocks)  # type: ignore[attr-defined]

    def report_state_locking_pins_engaged(self, engaged_pins: int) -> None:
        """Report the state of the engaged locking pins.

        Parameters
        ----------
        engaged_pins : `int`
            Bitmask of the locking pins that have been engaged.
        """

        self._check_system_state_and_report(
            "lockingPinsEngaged", "interlock", "locking_pins_engaged", engaged_pins
        )

    def _check_system_state_and_report(
        self, state_field: str, signal_name: str, signal_field: str, value: int
    ) -> None:
        """Check the system's state and report it if the value is changed.

        Parameters
        ----------
        state_field : `str`
            State's field.
        signal_name : `str`
            Signal's name defined in "self.signals".
        signal_field : `str`
            Signal's field.
        value : `int`
            New value.
        """

        if self.status.state[state_field] != value:
            self.status.state[state_field] = value
            getattr(self.signals[signal_name], signal_field).emit(value)

    def report_state_brake_engaged(self, brakes: int) -> None:
        """Report the state of the engaged brake.

        Parameters
        ----------
        brakes : `int`
            Bitmask of the brakes that are engaged.
        """

        self._check_system_state_and_report("brakeEngaged", "state", "brake_engaged", brakes)

    def report_state_azimuth_axis(self, state: MTDome.EnabledState) -> None:
        """Report the state of the azimuth axis.

        Parameters
        ----------
        state : enum `MTDome.EnabledState`
            State of the azimuth axis.
        """

        self._check_system_state_and_report("azimuthAxis", "state", "azimuth_axis", state.value)

    def report_state_elevation_axis(self, state: MTDome.EnabledState) -> None:
        """Report the state of the elevation axis.

        Parameters
        ----------
        state : enum `MTDome.EnabledState`
            State of the elevation axis.
        """

        self._check_system_state_and_report("elevationAxis", "state", "elevation_axis", state.value)

    def report_state_aperture_shutter(self, state: MTDome.EnabledState) -> None:
        """Report the state of the aperture shutter.

        Parameters
        ----------
        state : enum `MTDome.EnabledState`
            State of the aperture shutter.
        """

        self._check_system_state_and_report("apertureShutter", "state", "aperture_shutter", state.value)

    def report_state_louvers(self, state: MTDome.EnabledState) -> None:
        """Report the state of the louvers.

        Parameters
        ----------
        state : enum `MTDome.EnabledState`
            State of the louvers.
        """

        self._check_system_state_and_report("louvers", "state", "louvers", state.value)

    def report_state_rear_access_door(self, state: MTDome.EnabledState) -> None:
        """Report the state of the rear access door.

        Parameters
        ----------
        state : enum `MTDome.EnabledState`
            State of the rear access door.
        """

        self._check_system_state_and_report("rearAccessDoor", "state", "rear_access_door", state.value)

    def report_state_calibration_screen(self, state: MTDome.EnabledState) -> None:
        """Report the state of the calibration screen.

        Parameters
        ----------
        state : enum `MTDome.EnabledState`
            State of the calibration screen.
        """

        self._check_system_state_and_report("calibrationScreen", "state", "calibration_screen", state.value)

    def report_state_power_mode(self, mode: MTDome.PowerManagementMode) -> None:
        """Report the state of the power mode.

        Parameters
        ----------
        mode : enum `MTDome.PowerManagementMode`
            Power mode.
        """

        self._check_system_state_and_report("powerMode", "state", "power_mode", mode.value)

    def report_state_control_mode(self, mode: ControlMode) -> None:
        """Report the state of the control mode.

        Parameters
        ----------
        mode : enum `lsst.ts.mtdome.ControlMode`
            Control mode.
        """

        # TODO: OSW-1538, update the annotation of enum and related doc string
        # to use the MTDome.ControlMode after ts_xml 24.4.

        self._check_system_state_and_report("controlMode", "state", "control_mode", mode.value)

    def report_operational_mode(self, subsystem: MTDome.SubSystemId, mode: MTDome.OperationalMode) -> None:
        """Report the operational mode of a subsystem.

        Parameters
        ----------
        subsystem : `MTDome.SubSystemId`
            Subsystem ID.
        mode : `MTDome.OperationalMode`
            Operational mode.
        """

        for idx, specific_subsystem in enumerate(MTDome.SubSystemId):
            if subsystem == specific_subsystem:
                break

        if self.status.operational_modes[idx] != mode.value:
            self.status.operational_modes[idx] = mode.value
            self.signals["operational_mode"].subsystem_mode.emit(  # type: ignore[attr-defined]
                (subsystem, mode)
            )

    def report_capacitor_bank(self, capacitor_bank: dict[str, list[bool] | float]) -> None:
        """Report the status of the capacitor bank.

        Parameters
        ----------
        capacitor_bank : `dict`
            Status of the capacitor bank.
        """

        self.signals["telemetry"].cbcs_voltage.emit(  # type: ignore[attr-defined]
            capacitor_bank["dcBusVoltage"]
        )
        capacitor_bank.pop("dcBusVoltage")

        if self.status.capacitor_bank != capacitor_bank:
            self.status.capacitor_bank = capacitor_bank  # type: ignore[assignment]
            self.signals["telemetry"].cbcs.emit(capacitor_bank)  # type: ignore[attr-defined]

    def report_config_azimuth(self, config: dict[str, float]) -> None:
        """Report the configuration of the azimuth motion control system
        (AMCS).

        Parameters
        ----------
        config : `dict`
            Configuration.
        """

        if self.status.config_amcs != config:
            self.status.config_amcs = config
            self.signals["config"].amcs.emit(config)  # type: ignore[attr-defined]

    def report_config_elevation(self, config: dict[str, float]) -> None:
        """Report the configuration of the elevation (light and wind screen)
        control system (LWSCS).

        Parameters
        ----------
        config : `dict`
            Configuration.
        """

        if self.status.config_lwscs != config:
            self.status.config_lwscs = config
            self.signals["config"].lwscs.emit(config)  # type: ignore[attr-defined]

    def report_telemetry(self, field: str, telemetry: dict) -> None:
        """Report the telemetry.

        Parameters
        ----------
        field : `str`
            Field defined in the `SignalTelemetry`.
        telemetry : `dict`
            Telemetry defined in the schema/registry of ts_mtdomecom.
        """

        getattr(self.signals["telemetry"], field).emit(telemetry)

    def report_target_azimuth(self, position: float, velocity: float) -> None:
        """Report the azimuth target.

        Parameters
        ----------
        position : `float`
            Target position in deg.
        velocity : `float`
            Target velocity in deg/sec.
        """

        self.signals["target"].position_velocity_azimuth.emit(  # type: ignore[attr-defined]
            (position, velocity)
        )

    def report_target_elevation(self, position: float, velocity: float) -> None:
        """Report the elevation target.

        Parameters
        ----------
        position : `float`
            Target position in deg.
        velocity : `float`
            Target velocity in deg/sec.
        """

        self.signals["target"].position_velocity_elevation.emit(  # type: ignore[attr-defined]
            (position, velocity)
        )

    def report_motion_azimuth_axis(self, motion_state: MTDome.MotionState, in_position: bool) -> None:
        """Report the motion of the azimuth axis.

        Parameters
        ----------
        motion_state : enum `MTDome.MotionState`
            Motion state.
        in_position : `bool`
            True if the azimuth axis is in position. Otherwise, False.
        """

        self.signals["motion"].azimuth_axis.emit((motion_state, in_position))  # type: ignore[attr-defined]

    def report_motion_elevation_axis(self, motion_state: MTDome.MotionState, in_position: bool) -> None:
        """Report the motion of the elevation axis.

        Parameters
        ----------
        motion_state : enum `MTDome.MotionState`
            Motion state.
        in_position : `bool`
            True if the elevation axis is in position. Otherwise, False.
        """

        self.signals["motion"].elevation_axis.emit((motion_state, in_position))  # type: ignore[attr-defined]

    def report_motion_aperture_shutter(
        self, motion_states: list[MTDome.MotionState], in_positions: list[bool]
    ) -> None:
        """Report the motion of the aperture shutter.

        Parameters
        ----------
        motion_states : `list` [enum `MTDome.MotionState`]
            List of the Motion states.
        in_positions : `list` [`bool`]
            List of the in-position. True if the aperture shutter is in
            position. Otherwise, False.
        """

        self.signals["motion"].aperture_shutter.emit(  # type: ignore[attr-defined]
            (motion_states, in_positions)
        )

    def report_motion_louvers(
        self, motion_states: list[MTDome.MotionState], in_positions: list[bool]
    ) -> None:
        """Report the motion of the louvers.

        Parameters
        ----------
        motion_states : `list` [enum `MTDome.MotionState`]
            List of the Motion states.
        in_positions : `list` [`bool`]
            List of the in-position. True if the louver is in
            position. Otherwise, False.
        """

        self.signals["motion"].louvers.emit(  # type: ignore[attr-defined]
            (motion_states, in_positions)
        )

    def report_motion_rear_access_door(
        self, motion_states: list[MTDome.MotionState], in_positions: list[bool]
    ) -> None:
        """Report the motion of the rear access door.

        Parameters
        ----------
        motion_states : `list` [enum `MTDome.MotionState`]
            List of the Motion states.
        in_positions : `list` [`bool`]
            List of the in-position. True if the rear access door is in
            position. Otherwise, False.
        """

        self.signals["motion"].rear_access_door.emit(  # type: ignore[attr-defined]
            (motion_states, in_positions)
        )

    def report_motion_calibration_screen(self, motion_state: MTDome.MotionState, in_position: bool) -> None:
        """Report the motion of the calibration screen.

        Parameters
        ----------
        motion_state : enum `MTDome.MotionState`
            Motion state.
        in_position : `bool`
            True if the calibration screen is in position. Otherwise, False.
        """

        self.signals["motion"].calibration_screen.emit((motion_state, in_position))  # type: ignore[attr-defined]

    def report_fault_code_azimuth_axis(self, fault_code: str) -> None:
        """Report the fault code of the azimuth axis.

        Parameters
        ----------
        fault_code : `str`
            Fault code.
        """

        self.signals["fault_code"].azimuth_axis.emit(fault_code)  # type: ignore[attr-defined]

    def report_fault_code_elevation_axis(self, fault_code: str) -> None:
        """Report the fault code of the elevation axis.

        Parameters
        ----------
        fault_code : `str`
            Fault code.
        """

        self.signals["fault_code"].elevation_axis.emit(fault_code)  # type: ignore[attr-defined]

    def report_fault_code_aperture_shutter(self, fault_code: str) -> None:
        """Report the fault code of the aperture shutter.

        Parameters
        ----------
        fault_code : `str`
            Fault code.
        """

        self.signals["fault_code"].aperture_shutter.emit(fault_code)  # type: ignore[attr-defined]

    def report_fault_code_louvers(self, fault_code: str) -> None:
        """Report the fault code of the louvers.

        Parameters
        ----------
        fault_code : `str`
            Fault code.
        """

        self.signals["fault_code"].louvers.emit(fault_code)  # type: ignore[attr-defined]

    def report_fault_code_rear_access_door(self, fault_code: str) -> None:
        """Report the fault code of the rear access door.

        Parameters
        ----------
        fault_code : `str`
            Fault code.
        """

        self.signals["fault_code"].rear_access_door.emit(fault_code)  # type: ignore[attr-defined]

    def report_fault_code_calibration_screen(self, fault_code: str) -> None:
        """Report the fault code of the calibration screen.

        Parameters
        ----------
        fault_code : `str`
            Fault code.
        """

        self.signals["fault_code"].calibration_screen.emit(fault_code)  # type: ignore[attr-defined]
