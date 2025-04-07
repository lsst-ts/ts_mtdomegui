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
import math
import types
import typing

from lsst.ts.mtdomecom import (
    LlcName,
    LlcNameDict,
    MTDomeCom,
    ValidSimulationMode,
    motion_state_translations,
)
from lsst.ts.xml.enums import MTDome

from .reporter import Reporter


class Model:
    """Model class of the application.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.
    host : `str`, optional
        Host address. (the default is "localhost")
    port : `int`, optional
        Port to connect. (the default is 4998)
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
    reporter : `Reporter`
        Reporter to report the status and telemetry.
    mtdome_com : `lsst.ts.mtdomecom.MTDomeCom`
        TCP/IP interface to the MTDome controller.
    """

    def __init__(
        self,
        log: logging.Logger,
        host: str = "localhost",
        port: int = 4998,
        is_simulation_mode: bool = False,
        duration_refresh: int = 200,
    ) -> None:

        self.log = log
        self._is_simulation_mode = is_simulation_mode

        self.connection_information = {
            "host": host,
            "port": port,
        }

        self.duration_refresh = duration_refresh

        self.reporter = Reporter(self.log)

        self.mtdome_com: MTDomeCom | None = None

    async def connect(self) -> None:
        """Connect to the controller.

        Start the mock controller, if simulating.
        """

        config = type(
            "Obj",
            (object,),
            {key: value for key, value in self.connection_information.items()},
        )()

        simulation_mode = (
            ValidSimulationMode.SIMULATION_WITH_MOCK_CONTROLLER
            if self._is_simulation_mode
            else ValidSimulationMode.NORMAL_OPERATIONS
        )

        telemetry_callbacks = (
            {
                LlcName.AMCS: self.callback_status_amcs,
                LlcName.APSCS: self.callback_status_apscs,
                LlcName.CBCS: self.callback_status_cbcs,
                LlcName.CSCS: self.callback_status_cscs,
                LlcName.LCS: self.callback_status_lcs,
                LlcName.LWSCS: self.callback_status_lwscs,
                LlcName.MONCS: self.callback_status_moncs,
                LlcName.RAD: self.callback_status_rad,
            }
            if self._is_simulation_mode
            else {
                LlcName.AMCS: self.callback_status_amcs,
                LlcName.APSCS: self.callback_status_apscs,
                LlcName.CBCS: self.callback_status_cbcs,
                LlcName.THCS: self.callback_status_thcs,
            }
        )

        self.mtdome_com = MTDomeCom(
            self.log,
            config,
            simulation_mode=simulation_mode,
            telemetry_callbacks=telemetry_callbacks,
        )

        try:
            await self.mtdome_com.connect()
        except Exception as error:
            raise RuntimeError(f"Connection to the controller failed: {error!r}.")

        self.reporter.report_state_azimuth_axis(MTDome.EnabledState.ENABLED)
        self.reporter.report_fault_code_azimuth_axis("")

        self.reporter.report_state_elevation_axis(MTDome.EnabledState.ENABLED)
        self.reporter.report_fault_code_elevation_axis("")

        self.reporter.report_state_aperture_shutter(MTDome.EnabledState.ENABLED)
        self.reporter.report_fault_code_aperture_shutter("")

        self.reporter.report_state_brake_engaged(0)
        self.reporter.report_state_locking_pins_engaged(0)

        self.reporter.report_state_power_mode(self.mtdome_com.power_management_mode)

    async def disconnect(self) -> None:
        """Disconnect from the controller, if connected, and stop the
        mock controller, if running.

        This function is safe to call even if the controller is not connected.
        """

        self.log.info("disconnect.")

        # Disconnect from the controller
        if self.is_connected():

            # Workaround the mypy check
            assert self.mtdome_com is not None

            await self.mtdome_com.disconnect()
            self.mtdome_com = None

    def assert_is_connected(self) -> None:
        """Assert the connection is established.

        Raises
        ------
        `RuntimeError`
            If the connection is not established.
        """

        if not self.is_connected():
            raise RuntimeError("The connection is not established.")

    def is_connected(self) -> bool:
        """Is the controller connected or not.

        Returns
        -------
        `bool`
            True if the controller is connected. False otherwise.
        """

        return self.mtdome_com is not None and self.mtdome_com.connected

    async def report_llc_status(self, llc_name: LlcName, status: dict) -> None:
        """Report the status of lower level component (LLC).

        Parameters
        ----------
        llc_name : enum `lsst.ts.mtdomecom.LlcName`
            The name of LLC.
        status : `dict`
            System status.
        """

        # Workaround of the mypy check
        assert self.mtdome_com is not None

        # If there is only the "exception" key, it means that the status
        # reporting has failed. Return without reporting the status.
        if list(status.keys()) == ["exception"]:
            self.log.error(f"Failed to report the status of {llc_name!r}.")
            return

        self._report_operational_mode(llc_name, status["status"])
        self._report_configuration(llc_name, status)

        self._check_errors_and_report(llc_name, status["status"])

        # Remove some keys because they are not reported in the telemetry
        processed_telemetry = self.mtdome_com.remove_keys_from_dict(
            status, {"timestamp"}
        )

        # Report the telemetry
        match llc_name:
            case LlcName.MONCS:
                # There is the question for the details of interlock at the
                # moment. This part might be updated in the future.
                interlocks = [bool(value) for value in processed_telemetry["data"]]
                self.reporter.report_interlocks(interlocks)

            case LlcName.OBC:
                # The related event/telemetry is not defined yet.
                # TODO: DM-40876 should give the details.
                pass

            case LlcName.CBCS:
                processed_telemetry_update = self.mtdome_com.remove_keys_from_dict(
                    processed_telemetry, {"status"}
                )
                self.reporter.report_capacitor_bank(processed_telemetry_update)

            case _:
                self.reporter.report_telemetry(
                    llc_name.name.lower(), processed_telemetry
                )

    def _report_operational_mode(
        self, llc_name: LlcName, status: dict[str, typing.Any]
    ) -> None:
        """Report the operational mode.

        Parameters
        ----------
        llc_name : enum `lsst.ts.mtdomecom.LlcName`
            The name of the lower level component (LLC).
        status : `dict`
            Status.
        """

        if "operationalMode" in status:
            self.reporter.report_operational_mode(
                self._get_subsystem_id(llc_name),
                MTDome.OperationalMode[status["operationalMode"]],
            )

    def _get_subsystem_id(self, llc_name: LlcName) -> MTDome.SubSystemId:
        """Get the subsystem ID from the low level component (LLC) name.

        Parameters
        ----------
        llc_name : enum `lsst.ts.mtdomecom.LlcName`
            The name of LLC.

        Returns
        -------
        enum `MTDome.SubSystemId`
            Subsystem ID.
        """

        return MTDome.SubSystemId(
            [sid for sid, name in LlcNameDict.items() if name == llc_name][0]
        )

    def _report_configuration(
        self, llc_name: LlcName, status: dict[str, typing.Any]
    ) -> None:
        """Report the configuration.

        Parameters
        ----------
        llc_name : enum `lsst.ts.mtdomecom.LlcName`
            The name of the lower level component (LLC).
        status : `dict`
            Status.
        """

        if "appliedConfiguration" in status:
            configuration = status["appliedConfiguration"]

            # Radial to degree conversion
            for name in ["jmax", "amax", "vmax"]:
                configuration[name] = math.degrees(configuration[name])

            if llc_name == LlcName.AMCS:
                self.reporter.report_config_azimuth(configuration)

            elif llc_name == LlcName.LWSCS:
                self.reporter.report_config_elevation(configuration)

    def _check_errors_and_report(
        self, llc_name: LlcName, status: dict[str, typing.Any]
    ) -> None:
        """Check the errors and report.

        Parameters
        ----------
        llc_name : enum `lsst.ts.mtdomecom.LlcName`
            The name of the lower level component (LLC).
        status : `dict`
            Status.
        """

        match llc_name:
            case LlcName.AMCS:
                self._check_errors_and_report_azimuth(status)

            case LlcName.LWSCS:
                self._check_errors_and_report_elevation(status)

            case LlcName.APSCS:
                self._check_errors_and_report_aperture_shutter(status)

            case _:
                # The details for other subsystems are not defined yet.
                # See the ts_mtdome.
                pass

    def _check_errors_and_report_azimuth(self, status: dict[str, typing.Any]) -> None:
        """Check the errors and report for the azimuth.

        Parameters
        ----------
        status : `dict`
            Status.
        """

        has_error, fault_code = self._get_fault_code(status)
        state = MTDome.EnabledState.FAULT if has_error else MTDome.EnabledState.ENABLED

        self.reporter.report_state_azimuth_axis(state)
        self.reporter.report_fault_code_azimuth_axis(fault_code)

        if not has_error:
            motion_state = self._translate_motion_state_if_necessary(status["status"])
            if motion_state is not None:
                in_position = motion_state in [
                    MTDome.MotionState.STOPPED,
                    MTDome.MotionState.STOPPED_BRAKED,
                    MTDome.MotionState.CRAWLING,
                    MTDome.MotionState.PARKED,
                ]
                self.reporter.report_motion_azimuth_axis(motion_state, in_position)

    def _get_fault_code(self, status: dict[str, typing.Any]) -> tuple[bool, str]:
        """Get the fault code.

        Parameters
        ----------
        status : `dict`
            Status.

        Returns
        -------
        has_error : `bool`
            True if there is an error. False otherwise.
        fault_code : `str`
            Fault code. If no error, it is an empty string.
        """

        messages = status["messages"]

        codes = [message["code"] for message in messages]
        has_error = (len(messages) != 1) or (codes[0] != 0)

        fault_code = (
            ", ".join(
                [f"{message['code']}={message['description']}" for message in messages]
            )
            if has_error
            else ""
        )

        return has_error, fault_code

    def _translate_motion_state_if_necessary(
        self, state: str
    ) -> MTDome.MotionState | None:
        """Translate the motion state if necessary.

        Parameters
        ----------
        state : `str`
            State.

        Returns
        -------
        `MTDome.MotionState` or None
            Motion state. If the state is unknown, it returns None.
        """

        try:
            return MTDome.MotionState[state]

        except KeyError:

            try:
                return motion_state_translations[state]

            except KeyError:
                self.log.error(f"Unknown motion state: {state!r}")
                return None

    def _check_errors_and_report_elevation(self, status: dict[str, typing.Any]) -> None:
        """Check the errors and report for the elevation.

        Parameters
        ----------
        status : `dict`
            Status.
        """

        has_error, fault_code = self._get_fault_code(status)
        state = MTDome.EnabledState.FAULT if has_error else MTDome.EnabledState.ENABLED

        self.reporter.report_state_elevation_axis(state)
        self.reporter.report_fault_code_elevation_axis(fault_code)

        if not has_error:
            motion_state = self._translate_motion_state_if_necessary(status["status"])
            if motion_state is not None:
                in_position = motion_state in [
                    MTDome.MotionState.STOPPED,
                    MTDome.MotionState.STOPPED_BRAKED,
                    MTDome.MotionState.CRAWLING,
                ]
                self.reporter.report_motion_elevation_axis(motion_state, in_position)

    def _check_errors_and_report_aperture_shutter(
        self, status: dict[str, typing.Any]
    ) -> None:
        """Check the errors and report for the aperture shutter.

        Parameters
        ----------
        status : `dict`
            Status.
        """

        has_error, fault_code = self._get_fault_code(status)
        state = MTDome.EnabledState.FAULT if has_error else MTDome.EnabledState.ENABLED

        self.reporter.report_state_aperture_shutter(state)
        self.reporter.report_fault_code_aperture_shutter(fault_code)

        if not has_error:
            # The number of statuses has been validated by the JSON schema. So
            # here it is safe to loop over all statuses.
            motion_states = list()
            in_positions = list()
            for specific_status in status["status"]:
                motion_state = self._translate_motion_state_if_necessary(
                    specific_status
                )

                if motion_state is None:
                    return

                motion_states.append(motion_state)
                in_positions.append(
                    motion_state
                    in [
                        MTDome.MotionState.STOPPED,
                        MTDome.MotionState.STOPPED_BRAKED,
                    ]
                )

            self.reporter.report_motion_aperture_shutter(motion_states, in_positions)

    async def callback_status_amcs(self, status: dict) -> None:
        """Callback to report the status of azimuth motion control system
        (AMCS).

        Parameters
        ----------
        status : `dict`
            System status.
        """

        await self.report_llc_status(LlcName.AMCS, status)

    async def callback_status_apscs(self, status: dict) -> None:
        """Callback to report the status of aperture shutter control system
        (ApSCS).

        Parameters
        ----------
        status : `dict`
            System status.
        """

        await self.report_llc_status(LlcName.APSCS, status)

    async def callback_status_cbcs(self, status: dict) -> None:
        """Callback to report the status of capacitor banks control system
        (CBCS).

        Parameters
        ----------
        status : `dict`
            System status.
        """

        await self.report_llc_status(LlcName.CBCS, status)

    async def callback_status_cscs(self, status: dict) -> None:
        """Callback to report the status of calibration screen control system
        (CSCS).

        Parameters
        ----------
        status : `dict`
            System status.
        """

        await self.report_llc_status(LlcName.CSCS, status)

    async def callback_status_lcs(self, status: dict) -> None:
        """Callback to report the status of louvers control system (LCS).

        Parameters
        ----------
        status : `dict`
            System status.
        """

        await self.report_llc_status(LlcName.LCS, status)

    async def callback_status_lwscs(self, status: dict) -> None:
        """Callback to report the status of light and wind screen control
        system (LWSCS).

        Parameters
        ----------
        status : `dict`
            System status.
        """

        await self.report_llc_status(LlcName.LWSCS, status)

    async def callback_status_moncs(self, status: dict) -> None:
        """Callback to report the status of monitoring control system (MonCS).

        Parameters
        ----------
        status : `dict`
            System status.
        """

        await self.report_llc_status(LlcName.MONCS, status)

    async def callback_status_rad(self, status: dict) -> None:
        """Callback to report the status of rear access door (RAD).

        Parameters
        ----------
        status : `dict`
            System status.
        """

        await self.report_llc_status(LlcName.RAD, status)

    async def callback_status_thcs(self, status: dict) -> None:
        """Callback to report the status of thermal control system (ThCS).

        Parameters
        ----------
        status : `dict`
            System status.
        """

        await self.report_llc_status(LlcName.THCS, status)

    async def __aenter__(self) -> object:
        """This is an overridden function to support the asynchronous context
        manager."""
        return self

    async def __aexit__(
        self,
        type: typing.Type[BaseException] | None,
        value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """This is an overridden function to support the asynchronous context
        manager."""
        await self.disconnect()
