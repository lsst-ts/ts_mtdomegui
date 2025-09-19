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

__all__ = ["TabCommand"]

import math

from lsst.ts.guitool import (
    TabTemplate,
    create_double_spin_box,
    create_group_box,
    prompt_dialog_warning,
    run_command,
    set_button,
)
from lsst.ts.mtdomecom import (
    AMCS_NUM_MOTORS,
    APSCS_NUM_SHUTTERS,
    DOME_AZIMUTH_OFFSET,
    LCS_NUM_LOUVERS,
    LCS_NUM_MOTORS_PER_LOUVER,
    LOUVERS_ENABLED,
    LWSCS_VMAX,
)
from lsst.ts.xml.enums import MTDome
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..constants import MAX_POSITION, MAX_TEMPERATURE, NUM_DRIVE_SHUTTER, SUBSYSTEMS
from ..model import Model
from .tab_selector import TabSelector


class TabCommand(TabTemplate):
    """Table of the command.

    Parameters
    ----------
    title : `str`
        Table's title.
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title)

        self.model = model

        self._tabs = self._create_tabs(model)

        self._command_parameters = self._create_command_parameters()
        self._commands = self._create_commands()

        self._button_send_command = set_button(
            "Send Command",
            self._callback_send_command,
            tool_tip="Send the command to the controller.",
        )

        self.set_widget_and_layout()

        self._set_default()

    def _create_tabs(self, model: Model) -> dict[str, TabSelector]:
        """Create the tabs.

        Parameters
        ----------
        model : `Model`
            Model class.
        """

        names_louver = [
            f"{louver.name} ({idx})" for (idx, louver) in enumerate(MTDome.Louver)
        ]
        names_drive_azimuth = [str(idx) for idx in range(AMCS_NUM_MOTORS)]
        names_drive_shuttor = [str(idx) for idx in range(NUM_DRIVE_SHUTTER)]

        tab_louver = TabSelector("Louver", model, names_louver)
        for idx, louver in enumerate(MTDome.Louver):
            tab_louver.set_selection_enabled(idx, louver in LOUVERS_ENABLED)

        return {
            "louver": tab_louver,
            "drive_az": TabSelector("Azimuth Drive", model, names_drive_azimuth),
            "drive_shuttor": TabSelector("Shutter Drive", model, names_drive_shuttor),
        }

    def _create_command_parameters(self, decimal: int = 3) -> dict:
        """Create the command parameters.

        Parameters
        ----------
        decimal : `int`, optional
            Decimal. (the default is 3)

        Returns
        -------
        `dict`
            Command parameters.
        """

        # Spin box
        position = create_double_spin_box(
            "deg",
            decimal,
            maximum=MAX_POSITION,
            minimum=-MAX_POSITION,
        )

        velocity = create_double_spin_box(
            "deg/sec",
            decimal,
            maximum=math.degrees(LWSCS_VMAX),
            minimum=-math.degrees(LWSCS_VMAX),
        )

        speed = create_double_spin_box(
            "%",
            decimal,
            maximum=100.0,
        )

        temperature = create_double_spin_box(
            "deg C",
            decimal,
            maximum=MAX_TEMPERATURE,
            minimum=-MAX_TEMPERATURE,
        )

        percentage = create_double_spin_box(
            "%",
            decimal,
            maximum=100.0,
            tool_tip=(
                "Desired percent open of each louver: 0 is fully closed,\n"
                "100 is fully opened."
            ),
        )

        # Combo box
        subsystem = QComboBox()
        for sub_system, sub_system_id in zip(SUBSYSTEMS, MTDome.SubSystemId):
            subsystem.addItem(f"{sub_system} ({sub_system_id.name})")

        operation_mode = QComboBox()
        for mode in MTDome.OperationalMode:
            operation_mode.addItem(mode.name)

        power_mode = QComboBox()
        for mode in MTDome.PowerManagementMode:
            power_mode.addItem(mode.name)

        action = QComboBox()
        action.addItem("")
        for specific_action in MTDome.OnOff:
            action.addItem(specific_action.name)

        engage_brakes = QComboBox()
        engage_brakes.addItem("")
        for specific_action in MTDome.OnOff:
            engage_brakes.addItem(specific_action.name)
        engage_brakes.setToolTip("Engage the brakes (on) or not (off).")

        direction = QComboBox()
        for specific_action in MTDome.OpenClose:
            direction.addItem(specific_action.name)
        direction.setToolTip("Direction to home to.")

        # Button
        button_louver = set_button(
            "select louver",
            self._tabs["louver"].show,
            tool_tip="Click to select the louver.",
        )

        button_reset_az = set_button(
            "select azimuth drive",
            self._tabs["drive_az"].show,
            tool_tip="Click to select the azimuth drive.",
        )

        button_reset_shutter = set_button(
            "select shutter drive",
            self._tabs["drive_shuttor"].show,
            tool_tip="Click to select the shutter drive.",
        )

        return {
            "position": position,
            "velocity": velocity,
            "speed": speed,
            "temperature": temperature,
            "percentage": percentage,
            "subsystem": subsystem,
            "operation_mode": operation_mode,
            "power_mode": power_mode,
            "action": action,
            "engage_brakes": engage_brakes,
            "direction": direction,
            "louver": button_louver,
            "reset_drives_az": button_reset_az,
            "reset_drives_shutter": button_reset_shutter,
        }

    def _create_commands(self) -> dict[str, QRadioButton]:
        """Create the commands.

        Returns
        -------
        `dict`
            Commands. The key is the name of the command and the value is the
            button.
        """

        # Commands
        command_exit_fault = QRadioButton("Exit fault", parent=self)
        command_home = QRadioButton("Home", parent=self)

        command_crawl_az = QRadioButton("Crawl azimuth", parent=self)
        command_crawl_el = QRadioButton("Crawl elevation", parent=self)

        command_move_az = QRadioButton("Move azimuth", parent=self)
        command_move_el = QRadioButton("Move elevation", parent=self)

        command_park = QRadioButton("Park", parent=self)

        command_set_louvers = QRadioButton("Set louvers", parent=self)
        command_close_louvers = QRadioButton("Close louvers", parent=self)

        command_close_shutter = QRadioButton("Close shutter", parent=self)
        command_open_shutter = QRadioButton("Open shutter", parent=self)

        command_stop = QRadioButton("Stop", parent=self)

        command_set_temperature = QRadioButton("Set temperature", parent=self)
        command_set_operational_mode = QRadioButton("Set operational mode", parent=self)

        command_reset_drives_az = QRadioButton("Reset azimuth drives", parent=self)
        command_set_zero_az = QRadioButton("Set zero azimuth", parent=self)

        command_reset_drives_shutter = QRadioButton("Reset shutter drives", parent=self)
        command_reset_drives_louvers = QRadioButton("Reset louver drives", parent=self)

        command_fans = QRadioButton("Fans", parent=self)
        command_inflate = QRadioButton("Inflate", parent=self)

        command_set_power_management_mode = QRadioButton(
            "Set power management mode", parent=self
        )

        # Set the tool top
        command_exit_fault.setToolTip(
            "Indicate that all hardware errors, leading to fault state, have\n"
            "been resolved for the indicated subsystem(s)."
        )
        command_home.setToolTip(
            "Make the indicated subsystems go to the home position.\n"
            "Currently only works with the aperture shutter."
        )

        command_crawl_az.setToolTip("Move the azimuth axis at constant velocity.")
        command_crawl_el.setToolTip(
            "Move the elevation axis (light/wind screen) at constant velocity."
        )

        command_move_az.setToolTip(
            "Move the dome to the specified azimuth position and start moving\n"
            "at the specified, constant velocity from there."
        )
        command_move_el.setToolTip(
            "Move the elevation axis (light/wind screen) to a specified position."
        )

        command_park.setToolTip(
            "Move all components to park position and engage the brakes and locking pins."
        )

        command_set_louvers.setToolTip(
            "Move one or more louvers. The Louver enumeration describes the louver indices."
        )
        command_close_louvers.setToolTip("Close all louvers.")

        command_close_shutter.setToolTip("Close the shutter.")
        command_open_shutter.setToolTip("Open the shutter.")

        command_stop.setToolTip(
            "For all indicated subsystems that are moving: stop the motion\n"
            "and then optionally apply the brakes. For all indicated\n"
            "subsystems that are not moving: disengage the locking pins\n"
            "(unparking the dome) and engage or disengage the brakes."
        )

        command_set_temperature.setToolTip(
            "Set the desired temperature of the MTDome heat sources (motors "
            "and cabinets)."
        )
        command_set_operational_mode.setToolTip(
            "Set the OperationalMode for the indicated subsystems."
        )

        command_reset_drives_az.setToolTip(
            "Reset one or more AZ drives. This is necessary when exiting from\n"
            "FAULT state without going to Degraded Mode since the drives don't\n"
            "reset themselves."
        )
        command_set_zero_az.setToolTip(
            "Take the current position of the AZ rotation of the dome as zero.\n"
            "This is necessary as long as the racks and pinions on the drives\n"
            "have not been installed yet to compensate for slippage of the\n"
            "drives."
        )

        command_reset_drives_shutter.setToolTip(
            "Reset one or more Aperture Shutter drives. This is necessary when\n"
            "exiting from FAULT state without going to Degraded Mode since the\n"
            "drives don't reset themselves."
        )

        command_reset_drives_louvers.setToolTip(
            "Reset one or more Louver drives. This is necessary when exiting\n"
            "from FAULT state without going to Degraded Mode since the drives\n"
            "don't reset themselves."
        )

        command_fans.setToolTip("Set the fans speed to the indicated value.")
        command_inflate.setToolTip(
            "Inflate (True) or deflate (False) the inflatable seal."
        )

        command_set_power_management_mode.setToolTip("Set the power management mode.")

        # Connect the toggled signal
        command_exit_fault.toggled.connect(self._callback_command)
        command_home.toggled.connect(self._callback_command)

        command_crawl_az.toggled.connect(self._callback_command)
        command_crawl_el.toggled.connect(self._callback_command)

        command_move_az.toggled.connect(self._callback_command)
        command_move_el.toggled.connect(self._callback_command)

        command_park.toggled.connect(self._callback_command)

        command_set_louvers.toggled.connect(self._callback_command)
        command_close_louvers.toggled.connect(self._callback_command)

        command_close_shutter.toggled.connect(self._callback_command)
        command_open_shutter.toggled.connect(self._callback_command)

        command_stop.toggled.connect(self._callback_command)

        command_set_temperature.toggled.connect(self._callback_command)
        command_set_operational_mode.toggled.connect(self._callback_command)

        command_reset_drives_az.toggled.connect(self._callback_command)
        command_set_zero_az.toggled.connect(self._callback_command)

        command_reset_drives_shutter.toggled.connect(self._callback_command)

        command_fans.toggled.connect(self._callback_command)
        command_inflate.toggled.connect(self._callback_command)

        command_set_power_management_mode.toggled.connect(self._callback_command)

        return {
            "exit_fault": command_exit_fault,
            "home": command_home,
            "crawl_az": command_crawl_az,
            "crawl_el": command_crawl_el,
            "move_az": command_move_az,
            "move_el": command_move_el,
            "park": command_park,
            "set_louvers": command_set_louvers,
            "close_louvers": command_close_louvers,
            "close_shutter": command_close_shutter,
            "open_shutter": command_open_shutter,
            "stop": command_stop,
            "set_temperature": command_set_temperature,
            "set_operational_mode": command_set_operational_mode,
            "reset_drives_az": command_reset_drives_az,
            "set_zero_az": command_set_zero_az,
            "reset_drives_shutter": command_reset_drives_shutter,
            "reset_drives_louvers": command_reset_drives_louvers,
            "fans": command_fans,
            "inflate": command_inflate,
            "set_power_management_mode": command_set_power_management_mode,
        }

    @asyncSlot()
    async def _callback_command(self) -> None:
        """Callback of the command button."""

        if self._commands["exit_fault"].isChecked():
            self._enable_command_parameters(["subsystem"])

        elif self._commands["home"].isChecked():
            self._enable_command_parameters(["subsystem", "direction"])

        elif self._commands["crawl_az"].isChecked():
            self._enable_command_parameters(["velocity"])

        elif self._commands["crawl_el"].isChecked():
            self._enable_command_parameters(["velocity"])

        elif self._commands["move_az"].isChecked():
            self._enable_command_parameters(["position", "velocity"])

        elif self._commands["move_el"].isChecked():
            self._enable_command_parameters(["position"])

        elif self._commands["park"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["set_louvers"].isChecked():
            self._enable_command_parameters(["louver", "percentage"])

        elif self._commands["close_louvers"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["close_shutter"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["open_shutter"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["stop"].isChecked():
            self._enable_command_parameters(["engage_brakes", "subsystem"])

        elif self._commands["set_temperature"].isChecked():
            self._enable_command_parameters(["temperature"])

        elif self._commands["set_operational_mode"].isChecked():
            self._enable_command_parameters(["operation_mode", "subsystem"])

        elif self._commands["reset_drives_az"].isChecked():
            self._enable_command_parameters(["reset_drives_az"])

        elif self._commands["set_zero_az"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["reset_drives_shutter"].isChecked():
            self._enable_command_parameters(["reset_drives_shutter"])

        elif self._commands["reset_drives_louvers"].isChecked():
            self._enable_command_parameters(["louver"])

        elif self._commands["fans"].isChecked():
            self._enable_command_parameters(["speed"])

        elif self._commands["inflate"].isChecked():
            self._enable_command_parameters(["action"])

        elif self._commands["set_power_management_mode"].isChecked():
            self._enable_command_parameters(["power_mode"])

    def _enable_command_parameters(self, enabled_parameters: list[str]) -> None:
        """Enable the command parameters.

        Parameters
        ----------
        enabled_parameters : `list` [`str`]
            Enabled command parameters.
        """

        for name, value in self._command_parameters.items():
            value.setEnabled(name in enabled_parameters)

    @asyncSlot()
    async def _callback_send_command(self) -> None:
        """Callback of the send-command button to command the controller."""

        # Check the connection status
        if not await run_command(self.model.assert_is_connected):
            return

        self._button_send_command.setEnabled(False)

        # Check the selected command and run the command
        name = self._get_selected_command()
        self.model.log.info(f"Send the command: {name}.")

        # Workaround the mypy check
        assert self.model.mtdome_com is not None

        match name:
            case "exit_fault":
                await run_command(
                    self.model.mtdome_com.exit_fault,  # type: ignore[union-attr]
                    self._get_subsystem_bitmask(),
                )

            case "home":
                # Move the shutters to the same direction
                direction = self._get_direction(self._command_parameters["direction"])
                await run_command(
                    self.model.mtdome_com.home,  # type: ignore[union-attr]
                    self._get_subsystem_bitmask(),
                    [direction] * APSCS_NUM_SHUTTERS,
                )

            case "crawl_az":
                velocity = self._command_parameters["velocity"].value()
                if await run_command(
                    self.model.mtdome_com.crawl_az,  # type: ignore[union-attr]
                    velocity,
                ):
                    self.model.reporter.report_target_azimuth(float("nan"), velocity)

            case "crawl_el":
                velocity = self._command_parameters["velocity"].value()
                if await run_command(
                    self.model.mtdome_com.crawl_el,  # type: ignore[union-attr]
                    velocity,
                ):
                    self.model.reporter.report_target_elevation(float("nan"), velocity)

            case "move_az":
                position = self._command_parameters["position"].value()
                velocity = self._command_parameters["velocity"].value()
                if await run_command(
                    self.model.mtdome_com.move_az,  # type: ignore[union-attr]
                    position,
                    velocity,
                ):
                    self.model.reporter.report_target_azimuth(position, velocity)

            case "move_el":
                position = self._command_parameters["position"].value()
                if await run_command(
                    self.model.mtdome_com.move_el,  # type: ignore[union-attr]
                    position,
                ):
                    self.model.reporter.report_target_elevation(position, 0.0)

            case "park":
                if await run_command(
                    self.model.mtdome_com.park,  # type: ignore[union-attr]
                ):
                    # See the ts_mtdome for the "360.0 - DOME_AZIMUTH_OFFSET"
                    self.model.reporter.report_target_azimuth(
                        360.0 - DOME_AZIMUTH_OFFSET, 0.0
                    )

            case "set_louvers":
                await run_command(
                    self.model.mtdome_com.set_louvers,  # type: ignore[union-attr]
                    self._get_louver_percentages(),
                )

            case "close_louvers":
                await run_command(
                    self.model.mtdome_com.close_louvers,  # type: ignore[union-attr]
                )

            case "close_shutter":
                await run_command(
                    self.model.mtdome_com.close_shutter,  # type: ignore[union-attr]
                )

            case "open_shutter":
                await run_command(
                    self.model.mtdome_com.open_shutter,  # type: ignore[union-attr]
                )

            case "stop":
                subsystem_bitmask = self._get_subsystem_bitmask()
                engage_brakes = self._get_on_off(
                    self._command_parameters["engage_brakes"]
                )
                if engage_brakes is None:
                    await prompt_dialog_warning(
                        "_callback_send_command()",
                        ("The engage brakes can not be empty."),
                    )
                    self._button_send_command.setEnabled(True)
                    return

                else:
                    await run_command(
                        self.model.mtdome_com.stop_sub_systems,  # type: ignore[union-attr]
                        subsystem_bitmask,
                        engage_brakes.value,
                    )

            case "set_temperature":
                await run_command(
                    self.model.mtdome_com.set_temperature,  # type: ignore[union-attr]
                    self._command_parameters["temperature"].value(),
                )

            case "set_operational_mode":
                await run_command(
                    self.model.mtdome_com.set_operational_mode,  # type: ignore[union-attr]
                    self._get_operational_mode(),
                    self._get_subsystem_bitmask(),
                )

            case "reset_drives_az":
                await run_command(
                    self.model.mtdome_com.reset_drives_az,  # type: ignore[union-attr]
                    self._get_reset_drives_azimuth(),
                )

            case "set_zero_az":
                await run_command(
                    self.model.mtdome_com.set_zero_az,  # type: ignore[union-attr]
                )

            case "reset_drives_shutter":
                await run_command(
                    self.model.mtdome_com.reset_drives_shutter,  # type: ignore[union-attr]
                    self._get_reset_drives_aperture_shutter(),
                )

            case "reset_drives_louvers":
                await run_command(
                    self.model.mtdome_com.reset_drives_louvers,  # type: ignore[union-attr]
                    self._get_reset_drives_louver(),
                )

            case "fans":
                await run_command(
                    self.model.mtdome_com.fans,  # type: ignore[union-attr]
                    self._command_parameters["speed"].value(),
                )

            case "inflate":
                action = self._get_on_off(self._command_parameters["action"])
                if action is None:
                    await prompt_dialog_warning(
                        "_callback_send_command()",
                        ("The action can not be empty."),
                    )
                    self._button_send_command.setEnabled(True)
                    return

                else:
                    await run_command(
                        self.model.mtdome_com.inflate,  # type: ignore[union-attr]
                        action,
                    )

            case "set_power_management_mode":
                mode = self._get_power_mode()
                if await run_command(
                    self.model.mtdome_com.set_power_management_mode,  # type: ignore[union-attr]
                    mode,
                ):
                    self.model.reporter.report_state_power_mode(mode)

            case _:
                # Should not reach here
                self.model.log.error(f"Unknown command: {name}.")

        self._button_send_command.setEnabled(True)

    def _get_selected_command(self) -> str:
        """Get the selected command.

        Returns
        -------
        name : `str`
            Selected command.
        """

        for name, commmand in self._commands.items():
            if commmand.isChecked():
                return name

        return ""

    def _get_louver_percentages(self) -> list[float]:
        """Get the louver percentages.

        -1.0 means "do not move".

        Returns
        -------
        percentages : `list` [`float`]
            Percentages.
        """

        percentage = self._command_parameters["percentage"].value()

        percentages = [-1.0] * len(MTDome.Louver)
        for selection in self._tabs["louver"].get_selection():
            percentages[selection] = percentage

        return percentages

    def _get_subsystem_bitmask(self) -> int:
        """Get the subsystem's bitmask.

        Returns
        -------
        `int`
            Subsystem's bitmask.
        """

        return list(MTDome.SubSystemId)[
            self._command_parameters["subsystem"].currentIndex()
        ].value

    def _get_direction(self, combo_box: QComboBox) -> MTDome.OpenClose:
        """Get the direction.

        Parameters
        ----------
        combo_box : `PySide6.QtWidgets.QComboBox`
            Combo box with the direction.

        Returns
        -------
        enum `MTDome.OpenClose`
            Direction.
        """

        return MTDome.OpenClose[combo_box.currentText()]

    def _get_on_off(self, combo_box: QComboBox) -> MTDome.OnOff | None:
        """Get the on/off status.

        Parameters
        ----------
        combo_box : `PySide6.QtWidgets.QComboBox`
            Combo box with the on/off status.

        Returns
        -------
        enum `MTDome.OnOff` or None
            On/Off status. If no selection, return None.
        """

        match combo_box.currentIndex():
            case 1:
                return MTDome.OnOff.ON

            case 2:
                return MTDome.OnOff.OFF

            case _:
                return None

    def _get_operational_mode(self) -> MTDome.OperationalMode:
        """Get the operational mode.

        Returns
        -------
        enum `MTDome.OperationalMode`
            Operational mode.
        """

        # The index of the combo box is 0-based, but the OperationalMode is
        # 1-based.
        return MTDome.OperationalMode(
            self._command_parameters["operation_mode"].currentIndex() + 1
        )

    def _get_reset_drives_azimuth(self) -> list[int]:
        """Get the reset azimuth drives.

        Returns
        -------
        reset_drives : `list` [`int`]
            Reset azimuth drives. 0 means no reset, 1 means reset.
        """

        reset_drives = [0] * AMCS_NUM_MOTORS
        for idx in self._tabs["drive_az"].get_selection():
            reset_drives[idx] = 1

        return reset_drives

    def _get_reset_drives_aperture_shutter(self) -> list[int]:
        """Get the reset aperture shutter drives.

        Returns
        -------
        reset_drives : `list` [`int`]
            Reset aperture shutter drives. 0 means no reset, 1 means reset.
        """

        reset_drives = [0] * NUM_DRIVE_SHUTTER
        for idx in self._tabs["drive_shuttor"].get_selection():
            reset_drives[idx] = 1

        return reset_drives

    def _get_reset_drives_louver(self) -> list[int]:
        """Get the reset louver drives.

        Returns
        -------
        reset_drives : `list` [`int`]
            Reset louver drives. 0 means no reset, 1 means reset.
        """

        reset_drives = [0] * LCS_NUM_MOTORS_PER_LOUVER * LCS_NUM_LOUVERS
        for idx in self._tabs["louver"].get_selection():
            reset_drives[
                LCS_NUM_MOTORS_PER_LOUVER * idx : LCS_NUM_MOTORS_PER_LOUVER * (idx + 1)
            ] = [1] * LCS_NUM_MOTORS_PER_LOUVER

        return reset_drives

    def _get_power_mode(self) -> MTDome.PowerManagementMode:
        """Get the power management mode.

        Returns
        -------
        enum `MTDome.PowerManagementMode`
            Power management mode.
        """

        # The index of the combo box is 0-based, but the PowerManagementMode is
        # 1-based.
        return MTDome.PowerManagementMode(
            self._command_parameters["power_mode"].currentIndex() + 1
        )

    def create_layout(self) -> QHBoxLayout:

        # First column
        layout_command = QVBoxLayout()
        layout_command.addWidget(self._create_group_commands())

        # Second column
        layout_command_parameters = QVBoxLayout()
        layout_command_parameters.addWidget(self._create_group_command_parameters())
        layout_command_parameters.addWidget(self._button_send_command)

        layout = QHBoxLayout()
        layout.addLayout(layout_command)
        layout.addLayout(layout_command_parameters)

        return layout

    def _create_group_commands(self) -> QGroupBox:
        """Create the group of commands.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()
        for command in self._commands.values():
            layout.addWidget(command)

        return create_group_box("Commands", layout)

    def _create_group_command_parameters(self) -> QGroupBox:
        """Create the group of command parameters.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Subsystem:", self._command_parameters["subsystem"])
        layout.addRow("Position:", self._command_parameters["position"])
        layout.addRow("Velocity:", self._command_parameters["velocity"])
        layout.addRow("Speed:", self._command_parameters["speed"])
        layout.addRow("Temperature:", self._command_parameters["temperature"])
        layout.addRow("Operation mode:", self._command_parameters["operation_mode"])
        layout.addRow("Power mode:", self._command_parameters["power_mode"])
        layout.addRow("Action:", self._command_parameters["action"])
        layout.addRow("Engage brakes:", self._command_parameters["engage_brakes"])
        layout.addRow("Direction:", self._command_parameters["direction"])
        layout.addRow("Louver:", self._command_parameters["louver"])
        layout.addRow("Percentage:", self._command_parameters["percentage"])
        layout.addRow("Azimuth drives:", self._command_parameters["reset_drives_az"])
        layout.addRow(
            "Shutter drives:", self._command_parameters["reset_drives_shutter"]
        )

        return create_group_box("Command Parameters", layout)

    def _set_default(self) -> None:
        """Set the default values."""

        self._commands["exit_fault"].setChecked(True)
