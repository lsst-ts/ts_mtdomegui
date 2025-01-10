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

__all__ = ["Model"]

import logging

from lsst.ts.mtdomecom.schema import registry
from lsst.ts.xml.enums import MTDome

from .signals import (
    SignalInterlock,
    SignalOperationalMode,
    SignalState,
    SignalTelemetry,
)
from .status import Status
from .utils import generate_dict_from_registry


class Model(object):
    """Model class of the application.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.
    is_simulation_mode: `bool`, optional
        True if running in simulation mode. (the default is False)
    duration_refresh : `int`, optional
        Duration to refresh the data in milliseconds. (the default is 200)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    connection_information : `dict`
        TCP/IP connection information.
    duration_refresh : `int`
        Duration to refresh the data in milliseconds.
    status : `Status`
        System status.
    signals : `dict`
        Signals.
    """

    def __init__(
        self,
        log: logging.Logger,
        is_simulation_mode: bool = False,
        duration_refresh: int = 200,
    ) -> None:

        self.log = log
        self._is_simulation_mode = is_simulation_mode

        # TODO: Put this into the ts_config_mttcs in DM-48109.
        self.connection_information = {
            "host": "localhost",
            "port": 1000,
            "timeout_connection": 10.0,
        }

        self.duration_refresh = duration_refresh

        self.status = Status()

        self.signals = {
            "interlock": SignalInterlock(),
            "state": SignalState(),
            "operational_mode": SignalOperationalMode(),
            "telemetry": SignalTelemetry(),
        }

    def report_default(self) -> None:
        """Report the default status."""

        self.signals["interlock"].interlock.emit(self.status.interlocks)  # type: ignore[attr-defined]
        self.report_state_locking_pins_engaged(0)

        self.report_state_brake_engaged(0)
        self.report_system_azimuth_axis(MTDome.EnabledState.DISABLED)
        self.report_system_elevation_axis(MTDome.EnabledState.DISABLED)
        self.report_system_aperture_shutter(MTDome.EnabledState.DISABLED)
        self.report_system_power_mode(MTDome.PowerManagementMode.NO_POWER_MANAGEMENT)

        for subsystem in MTDome.SubSystemId:
            self.report_operational_mode(subsystem, MTDome.OperationalMode.NORMAL)

        self.report_telemetry("cbcs", self.status.capacitor_bank)

        for component in ["AMCS", "LWSCS", "ApSCS", "LCS", "ThCS", "RAD"]:
            self.report_telemetry(
                component.lower(), generate_dict_from_registry(registry, component)
            )

        # TODO: Remove this workaround after the DM-48368 is fixed.
        data_cscs = {
            "positionActual": 0.0,
            "positionCommanded": 0.0,
            "driveTorqueActual": 0.0,
            "driveTorqueCommanded": 0.0,
            "driveCurrentActual": 0.0,
            "driveTemperature": 0.0,
            "encoderHeadRaw": 0.0,
            "encoderHeadCalibrated": 0.0,
            "powerDraw": 0.0,
            "timestamp": 0.0,
        }
        self.report_telemetry("cscs", data_cscs)

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

        self._check_system_state_and_report(
            "brakeEngaged", "state", "brake_engaged", brakes
        )

    def report_system_azimuth_axis(self, state: MTDome.EnabledState) -> None:
        """Report the state of the azimuth axis.

        Parameters
        ----------
        state : enum `MTDome.EnabledState`
            State of the azimuth axis.
        """

        self._check_system_state_and_report(
            "azimuthAxis", "state", "azimuth_axis", state.value
        )

    def report_system_elevation_axis(self, state: MTDome.EnabledState) -> None:
        """Report the state of the elevation axis.

        Parameters
        ----------
        state : enum `MTDome.EnabledState`
            State of the elevation axis.
        """

        self._check_system_state_and_report(
            "elevationAxis", "state", "elevation_axis", state.value
        )

    def report_system_aperture_shutter(self, state: MTDome.EnabledState) -> None:
        """Report the state of the aperture shutter.

        Parameters
        ----------
        state : enum `MTDome.EnabledState`
            State of the aperture shutter.
        """

        self._check_system_state_and_report(
            "apertureShutter", "state", "aperture_shutter", state.value
        )

    def report_system_power_mode(self, mode: MTDome.PowerManagementMode) -> None:
        """Report the state of the power mode.

        Parameters
        ----------
        mode : enum `MTDome.PowerManagementMode`
            Power mode.
        """

        self._check_system_state_and_report(
            "powerMode", "state", "power_mode", mode.value
        )

    def report_operational_mode(
        self, subsystem: MTDome.SubSystemId, mode: MTDome.OperationalMode
    ) -> None:
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

    def report_capacitor_bank(self, capacitor_bank: dict[str, list[bool]]) -> None:
        """Report the status of the capacitor bank.

        Parameters
        ----------
        capacitor_bank : `dict`
            Status of the capacitor bank.
        """

        if self.status.capacitor_bank != capacitor_bank:
            self.status.capacitor_bank = capacitor_bank
            self.signals["telemetry"].cbcs.emit(capacitor_bank)  # type: ignore[attr-defined]

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
