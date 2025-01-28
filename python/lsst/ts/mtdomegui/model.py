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

import asyncio
import logging
import math
import types
import typing

from lsst.ts.mtdomecom import (
    COMMANDS_REPLIED_PERIOD,
    CommandName,
    LlcName,
    LlcNameDict,
    MTDomeCom,
    motion_state_translations,
)
from lsst.ts.xml.enums import MTDome

from .reporter import Reporter

# Remove these keys from the telemetry because they are not used.
_KEYS_TO_REMOVE = {
    "status",
    "timestamp",
    "operationalMode",
    "appliedConfiguration",
}

# Polling periods [sec] for the lower level components.
# The values are from the ts_mtdome.
_AMCS_STATUS_PERIOD = 0.2
_APSCS_STATUS_PERIOD = 0.5
_CBCS_STATUS_PERIOD = 0.5
_CSCS_STATUS_PERIOD = 0.5
_LCS_STATUS_PERIOD = 0.5
_LWSCS_STATUS_PERIOD = 0.5
_MONCS_STATUS_PERIOD = 0.5
_RAD_STATUS_PERIOD = 0.5
_THCS_STATUS_PERIOD = 0.5

# Polling period [sec] for the task that checks if any commands are waiting to
# be issued.
_COMMAND_QUEUE_PERIOD = 1.0


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
    periodic_tasks : `list` [`asyncio.Task`]
        List of periodic tasks.
    """

    # All methods and the intervals at which they are executed. Not all
    # subsystems are supported at moment (especially for the rotating part).
    # See ts_mtdome.
    all_methods_and_intervals = {
        CommandName.STATUS_AMCS: _AMCS_STATUS_PERIOD,
        # CommandName.STATUS_APSCS: _APSCS_STATUS_PERIOD,
        CommandName.STATUS_CBCS: _CBCS_STATUS_PERIOD,
        # CommandName.STATUS_CSCS: _CSCS_STATUS_PERIOD,
        # CommandName.STATUS_LCS: _LCS_STATUS_PERIOD,
        # CommandName.STATUS_LWSCS: _LWSCS_STATUS_PERIOD,
        # CommandName.STATUS_MONCS: _MONCS_STATUS_PERIOD,
        # CommandName.STATUS_RAD: _RAD_STATUS_PERIOD,
        # CommandName.STATUS_THCS: _THCS_STATUS_PERIOD,
    }

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

        # TODO: Put this into the ts_config_mttcs in DM-48109.
        self.connection_information = {
            "host": host,
            "port": port,
        }

        self.duration_refresh = duration_refresh

        self.reporter = Reporter(self.log)

        self.mtdome_com: MTDomeCom | None = None

        self.periodic_tasks: list[asyncio.Task] = list()

    async def connect(self) -> None:
        """Connect to the controller.

        Start the mock controller, if simulating.
        """

        config = type(
            "Obj",
            (object,),
            {key: value for key, value in self.connection_information.items()},
        )()
        self.mtdome_com = MTDomeCom(
            self.log, config, simulation_mode=self._is_simulation_mode
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

        # Start polling for the status of the lower level components
        # periodically.
        await self.start_periodic_tasks()

        self.log.info("connected")

    async def start_periodic_tasks(self) -> None:
        """Start all periodic tasks."""

        await self.cancel_periodic_tasks()

        for method, interval in self.all_methods_and_intervals.items():
            funcion = getattr(self, method)
            self.periodic_tasks.append(
                asyncio.create_task(self.one_periodic_task(funcion, interval))
            )

        # Workaround the mypy check
        assert self.mtdome_com is not None

        self.periodic_tasks.append(
            asyncio.create_task(
                self.one_periodic_task(
                    self.mtdome_com.check_all_commands_have_replies,
                    COMMANDS_REPLIED_PERIOD,
                )
            )
        )

        self.periodic_tasks.append(
            asyncio.create_task(
                self.one_periodic_task(
                    self.mtdome_com.process_command_queue,
                    _COMMAND_QUEUE_PERIOD,
                )
            )
        )

    async def cancel_periodic_tasks(self) -> None:
        """Cancel all periodic tasks."""

        while self.periodic_tasks:
            periodic_task = self.periodic_tasks.pop()
            periodic_task.cancel()
            await periodic_task

    async def one_periodic_task(self, method: typing.Callable, interval: float) -> None:
        """Run one method forever at the specified interval.

        Parameters
        ----------
        method : `typing.Callable`
            The coroutine to run periodically.
        interval : `float`
            The interval at which to run the status method in second.
        """

        self.log.debug(f"Starting periodic task {method=} with {interval=}")

        try:
            while True:
                await method()
                await asyncio.sleep(interval)

        except asyncio.CancelledError:
            # Ignore because the task was canceled on purpose.
            pass

        except Exception:
            self.log.exception(f"one_periodic_task({method}) has stopped.")

    async def disconnect(self) -> None:
        """Disconnect from the controller, if connected, and stop the
        mock controller, if running.

        This function is safe to call even if the controller is not connected.
        """

        self.log.info("disconnect.")

        # Stop all periodic tasks, including polling for the status of the
        # lower level components.
        await self.cancel_periodic_tasks()

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

        return (
            self.mtdome_com is not None
            and self.mtdome_com.client is not None
            and self.mtdome_com.client.connected
        )

    async def request_llc_status_and_report(self, llc_name: LlcName) -> None:
        """Generic method for retrieving the status of a lower level component
        (LLC) and report it.

        Parameters
        ----------
        llc_name: enum `lsst.ts.mtdomecom.LlcName`
            The name of LLC.
        """

        # Workaround the mypy check
        assert self.mtdome_com is not None

        # Retrieve the status
        try:
            status = await self.mtdome_com.request_llc_status(llc_name)

        except ValueError:
            self.log.error(f"Failed to retrieve the status of {llc_name!r}.")

            return

        self._report_operational_mode(llc_name, status["status"])
        self._report_configuration(llc_name, status)

        self._check_errors_and_report(llc_name, status["status"])

        # Remove some keys because they are not reported in the telemetry
        processed_telemetry = self._remove_keys_from_dict(status)

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
                # There is the bug in the simulator at the moment to publish
                # the float value instead of boolean.
                # TODO: DM-48698 fix this.
                if type(processed_telemetry["fuseIntervention"][0]) is not bool:
                    processed_telemetry["fuseIntervention"] = [
                        bool(value) for value in processed_telemetry["fuseIntervention"]
                    ]

                self.reporter.report_capacitor_bank(processed_telemetry)

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

    def _remove_keys_from_dict(
        self, dict_with_too_many_keys: dict[str, typing.Any]
    ) -> dict[str, typing.Any]:
        """
        Return a copy of a dict with specified items removed.

        Parameters
        ----------
        dict_with_too_many_keys : `dict`
            The dict where to remove the keys from.

        Returns
        -------
        `dict`
            A dict with the same keys as the given dict but with the given keys
            removed.
        """

        return {
            x: dict_with_too_many_keys[x]
            for x in dict_with_too_many_keys
            if x not in _KEYS_TO_REMOVE
        }

    async def statusAMCS(self) -> None:
        """Azimuth motion control system (AMCS) status command as the periodic
        callback function, which is defined in enum
        `lsst.ts.mtdomecom.CommandName`.

        This command will be used to request the full status of the AMCS lower
        level component.
        """

        await self.request_llc_status_and_report(LlcName.AMCS)

    async def statusApSCS(self) -> None:
        """Aperture shutter control system (ApSCS) status command as the
        periodic callback function, which is defined in enum
        `lsst.ts.mtdomecom.CommandName`.

        This command will be used to request the full status of the ApSCS lower
        level component.
        """

        await self.request_llc_status_and_report(LlcName.APSCS)

    async def statusCBCS(self) -> None:
        """Capacitor banks control system (CBCS) status command as the periodic
        callback function, which is defined in enum
        `lsst.ts.mtdomecom.CommandName`.

        This command will be used to request the full status of the CBCS lower
        level component.
        """

        await self.request_llc_status_and_report(LlcName.CBCS)

    async def statusCSCS(self) -> None:
        """Calibration screen control system (CSCS) status command as the
        periodic callback function, which is defined in enum
        `lsst.ts.mtdomecom.CommandName`.

        This command will be used to request the full status of the CSCS lower
        level component.
        """

        await self.request_llc_status_and_report(LlcName.CSCS)

    async def statusLCS(self) -> None:
        """Louvers control system (LCS) status command as the periodic callback
        function, which is defined in enum `lsst.ts.mtdomecom.CommandName`.

        This command will be used to request the full status of the LCS lower
        level component.
        """

        await self.request_llc_status_and_report(LlcName.LCS)

    async def statusLWSCS(self) -> None:
        """Light and wind screen control system (LWSCS) status command as the
        periodic callback function, which is defined in enum
        `lsst.ts.mtdomecom.CommandName`.

        This command will be used to request the full status of the LWSCS lower
        level component.
        """

        await self.request_llc_status_and_report(LlcName.LWSCS)

    async def statusMonCS(self) -> None:
        """Monitoring control system (MonCS) status command as the periodic
        callback function, which is defined in enum
        `lsst.ts.mtdomecom.CommandName`.

        This command will be used to request the full status of the MonCS lower
        level component.
        """

        await self.request_llc_status_and_report(LlcName.MONCS)

    async def statusRAD(self) -> None:
        """Rear access door (RAD) status command as the periodic callback
        function, which is defined in enum `lsst.ts.mtdomecom.CommandName`.

        This command will be used to request the full status of the RAD lower
        level component.
        """

        await self.request_llc_status_and_report(LlcName.RAD)

    async def statusThCS(self) -> None:
        """Thermal control system (ThCS) status command as the periodic
        callback function, which is defined in enum
        `lsst.ts.mtdomecom.CommandName`.

        This command will be used to request the full status of the ThCS lower
        level component.
        """

        await self.request_llc_status_and_report(LlcName.THCS)

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
