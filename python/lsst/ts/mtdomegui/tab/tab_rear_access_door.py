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

__all__ = ["TabRearAccessDoor"]

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)
from qasync import asyncSlot

from lsst.ts.guitool import (
    TabTemplate,
    create_group_box,
    create_label,
    create_radio_indicators,
)
from lsst.ts.mtdomecom import (
    RAD_NUM_DOORS,
    RAD_NUM_LIMIT_SWITCHES,
    RAD_NUM_LOCKING_PINS,
)
from lsst.ts.xml.enums import MTDome

from ..model import Model
from ..signals import SignalFaultCode, SignalMotion, SignalState, SignalTelemetry
from ..utils import (
    add_empty_row_to_form_layout,
    combine_indicators,
    create_buttons_with_tabs,
    create_window_fault_code,
    update_boolean_indicator_status,
)
from .tab_figure import TabFigure


class TabRearAccessDoor(TabTemplate):
    """Table of the rear access door.

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

        self._states = self._create_states()
        self._status = self._create_status()
        self._window_fault_code = create_window_fault_code()
        self._indicators = self._create_indicators()

        self._figures = self._create_figures()
        self._buttons = self._create_buttons()

        self.set_widget_and_layout()

        signals = self.model.reporter.signals
        self._set_signal_telemetry(signals["telemetry"])  # type: ignore[arg-type]
        self._set_signal_state(signals["state"])  # type: ignore[arg-type]
        self._set_signal_motion(signals["motion"])  # type: ignore[arg-type]
        self._set_signal_fault_code(signals["fault_code"])  # type: ignore[arg-type]

    def _create_states(self) -> dict[str, QLabel]:
        """Create the states.

        Returns
        -------
        `dict`
            System states.
        """

        return {
            "state": create_label(),
            "motion": create_label(),
            "in_position": create_label(),
        }

    def _create_status(self) -> dict[str, QLabel | list[QLabel]]:
        """Create the status.

        Returns
        -------
        `dict`
            System status.
        """

        position_actual = [
            create_label(tool_tip="Measured position of the rear access door (percent open).")
            for _ in range(RAD_NUM_DOORS)
        ]
        position_commanded = [
            create_label(tool_tip="Commanded position of the rear access door (percent open).")
            for _ in range(RAD_NUM_DOORS)
        ]

        drive_torque_actual = [create_label() for _ in range(RAD_NUM_DOORS)]
        drive_torque_commanded = [create_label() for _ in range(RAD_NUM_DOORS)]
        drive_current_actual = [create_label() for _ in range(RAD_NUM_DOORS)]
        drive_temperature = [create_label() for _ in range(RAD_NUM_DOORS)]

        return {
            "position_actual": position_actual,
            "position_commanded": position_commanded,
            "drive_torque_actual": drive_torque_actual,
            "drive_torque_commanded": drive_torque_commanded,
            "drive_current_actual": drive_current_actual,
            "drive_temperature": drive_temperature,
            "power_draw": create_label(tool_tip="Total power drawn by all rear access door drives."),
        }

    def _create_indicators(self) -> dict[str, QRadioButton | list[QRadioButton]]:
        """Create the radio indicators.

        Returns
        -------
        `dict`
            Dictionary of the indicators.
        """

        return {
            "limit_switch_open": create_radio_indicators(RAD_NUM_LIMIT_SWITCHES),
            "limit_switch_close": create_radio_indicators(RAD_NUM_LIMIT_SWITCHES),
            "pin": create_radio_indicators(RAD_NUM_LOCKING_PINS),
            "brake": create_radio_indicators(RAD_NUM_DOORS),
            "photoelectric_sensor": create_radio_indicators(1)[0],
            "curtain": create_radio_indicators(1)[0],
        }

    def _create_figures(self) -> dict[str, TabFigure]:
        """Create the figures.

        Returns
        -------
        `dict`
            Figures.
        """

        return {
            "position": TabFigure(
                "Position",
                self.model,
                "%",
                ["commanded 0", "commanded 1", "actual 0", "actual 1"],
            ),
            "drive_torque": TabFigure(
                "Actual Drive Torque",
                self.model,
                "N*m",
                [str(idx) for idx in range(RAD_NUM_DOORS)],
            ),
            "drive_current": TabFigure(
                "Actual Drive Current",
                self.model,
                "A",
                [str(idx) for idx in range(RAD_NUM_DOORS)],
            ),
            "drive_temperature": TabFigure(
                "Drive Temperature",
                self.model,
                "deg C",
                [str(idx) for idx in range(RAD_NUM_DOORS)],
            ),
            "resolver": TabFigure(
                "Calibrated Resolver",
                self.model,
                "deg",
                [str(idx) for idx in range(RAD_NUM_DOORS)],
            ),
            "power": TabFigure(
                "Total Power",
                self.model,
                "W",
                ["power"],
            ),
        }

    def _create_buttons(self) -> dict[str, QPushButton]:
        """Create the buttons.

        Returns
        -------
        buttons : `dict`
            Buttons.
        """

        names = [
            "Position",
            "Drive Torque",
            "Drive Current",
            "Drive Temperature",
            "Resolver",
            "Power",
        ]
        return create_buttons_with_tabs(names, self._figures)

    def create_layout(self) -> QHBoxLayout:
        # First column
        layout_state = QVBoxLayout()
        layout_state.addWidget(self._create_group_state())
        layout_state.addWidget(self._create_group_position())

        # Second column
        layout_status = QVBoxLayout()
        layout_status.addWidget(self._create_group_drive_torque())
        layout_status.addWidget(self._create_group_drive_temperature())
        layout_status.addWidget(self._create_group_power())

        # Third column
        layout_realtime = QVBoxLayout()
        layout_realtime.addWidget(self._create_group_safety())
        layout_realtime.addWidget(self._create_group_realtime_chart())

        layout = QHBoxLayout()
        layout.addLayout(layout_state)
        layout.addLayout(layout_status)
        layout.addLayout(layout_realtime)

        return layout

    def _create_group_state(self) -> QGroupBox:
        """Create the group of state.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_form = QFormLayout()
        layout_form.addRow("State:", self._states["state"])
        layout_form.addRow("Motion:", self._states["motion"])
        layout_form.addRow("In position:", self._states["in_position"])

        layout = QVBoxLayout()
        layout.addLayout(layout_form)
        layout.addWidget(self._window_fault_code)

        return create_group_box("State", layout)

    def _create_group_position(self) -> QGroupBox:
        """Create the group of position.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        for idx in range(RAD_NUM_DOORS):
            layout.addRow(
                f"Position {idx} (commanded):",
                self._status["position_commanded"][idx],
            )
            layout.addRow(
                f"Position {idx} (actual):",
                self._status["position_actual"][idx],
            )

            if idx != (RAD_NUM_DOORS - 1):
                add_empty_row_to_form_layout(layout)

        return create_group_box("Position", layout)

    def _create_group_drive_torque(self) -> QGroupBox:
        """Create the group of drive torque.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        for idx in range(RAD_NUM_DOORS):
            layout.addRow(
                f"Torque {idx} (commanded):",
                self._status["drive_torque_commanded"][idx],
            )
            layout.addRow(f"Torque {idx} (actual):", self._status["drive_torque_actual"][idx])
            add_empty_row_to_form_layout(layout)

        for idx in range(RAD_NUM_DOORS):
            layout.addRow(f"Current {idx} (actual):", self._status["drive_current_actual"][idx])

        return create_group_box("Drive Torque", layout)

    def _create_group_drive_temperature(self) -> QGroupBox:
        """Create the group of drive temperature.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        for idx in range(RAD_NUM_DOORS):
            layout.addRow(f"Temperature {idx}:", self._status["drive_temperature"][idx])

        return create_group_box("Drive Temperature", layout)

    def _create_group_power(self) -> QGroupBox:
        """Create the group of power.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Power:", self._status["power_draw"])

        return create_group_box("Power", layout)

    def _create_group_safety(self) -> QGroupBox:
        """Create the group of safety.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow(
            "Open limit switch engaged:",
            combine_indicators(self._indicators["limit_switch_open"]),
        )
        layout.addRow(
            "Close limit switch engaged:",
            combine_indicators(self._indicators["limit_switch_close"]),
        )

        add_empty_row_to_form_layout(layout)

        layout.addRow("Locking pins:", combine_indicators(self._indicators["pin"]))
        layout.addRow("Brakes engaged:", combine_indicators(self._indicators["brake"]))

        add_empty_row_to_form_layout(layout)

        layout.addRow("Photoelectric sensor clear:", self._indicators["photoelectric_sensor"])
        layout.addRow("Light curtain clear:", self._indicators["curtain"])

        return create_group_box("Safety", layout)

    def _create_group_realtime_chart(self) -> QGroupBox:
        """Create the group of real-time chart.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()
        for button in self._buttons.values():
            layout.addWidget(button)

        return create_group_box("Real-time Chart", layout)

    def _set_signal_telemetry(self, signal: SignalTelemetry) -> None:
        """Set the telemetry signal.

        Parameters
        ----------
        signal : `SignalTelemetry`
            Signal.
        """

        signal.rad.connect(self._callback_telemetry)

    @asyncSlot()
    async def _callback_telemetry(self, telemetry: dict) -> None:
        """Callback to update the telemetry.

        Parameters
        ----------
        telemetry : `dict`
            Telemetry.
        """

        # Label
        position_commanded = telemetry["positionCommanded"]
        position_actual = telemetry["positionActual"]
        for idx in range(RAD_NUM_DOORS):
            self._status["position_commanded"][idx].setText(f"{position_commanded[idx]:.2f} %")
            self._status["position_actual"][idx].setText(f"{position_actual[idx]:.2f} %")

            self._status["drive_torque_commanded"][idx].setText(
                f"{telemetry['driveTorqueCommanded'][idx]:.2f} N*m"
            )
            self._status["drive_torque_actual"][idx].setText(f"{telemetry['driveTorqueActual'][idx]:.2f} N*m")
            self._status["drive_current_actual"][idx].setText(f"{telemetry['driveCurrentActual'][idx]:.2f} A")

        for idx in range(RAD_NUM_DOORS):
            self._status["drive_temperature"][idx].setText(f"{telemetry['driveTemperature'][idx]:.2f} deg C")

        power = telemetry["powerDraw"]
        self._status["power_draw"].setText(f"{power:.2f} W")  # type: ignore[union-attr]

        # Real-time chart
        self._figures["position"].append_data(position_commanded + position_actual)

        self._figures["drive_torque"].append_data(telemetry["driveTorqueActual"])
        self._figures["drive_current"].append_data(telemetry["driveCurrentActual"])
        self._figures["drive_temperature"].append_data(telemetry["driveTemperature"])

        self._figures["resolver"].append_data(telemetry["resolverHeadCalibrated"])

        self._figures["power"].append_data([power])

        # Indicators
        names = [
            "limit_switch_open",
            "limit_switch_close",
            "pin",
            "brake",
            "photoelectric_sensor",
            "curtain",
        ]
        fields = [
            "openLimitSwitchEngaged",
            "closeLimitSwitchEngaged",
            "lockingPins",
            "brakesEngaged",
            "photoelectricSensorClear",
            "lightCurtainClear",
        ]
        for name, field in zip(names, fields):
            indicators = self._indicators[name]
            values = telemetry[field]

            if isinstance(indicators, QRadioButton):
                update_boolean_indicator_status(indicators, values)
                continue

            for indicator, value in zip(indicators, values):
                # TODO: Wait for the DM-48350 to give the detail of enum
                # value.
                if field == "lockingPins":
                    update_boolean_indicator_status(indicator, bool(value))
                else:
                    update_boolean_indicator_status(indicator, value)

    def _set_signal_state(self, signal: SignalState) -> None:
        """Set the state signal.

        Parameters
        ----------
        signal : `SignalState`
            Signal.
        """

        signal.rear_access_door.connect(self._callback_update_state)

    @asyncSlot()
    async def _callback_update_state(self, state: int) -> None:
        """Callback to update the state.

        Parameters
        ----------
        state : `int`
            State.
        """

        self._states["state"].setText(MTDome.EnabledState(state).name)

    def _set_signal_motion(self, signal: SignalMotion) -> None:
        """Set the motion signal.

        Parameters
        ----------
        signal : `SignalMotion`
            Signal.
        """

        signal.rear_access_door.connect(self._callback_update_motion)

    @asyncSlot()
    async def _callback_update_motion(self, motion: tuple[list[MTDome.MotionState], list[bool]]) -> None:
        """Callback to update the motion state.

        Parameters
        ----------
        motion : `tuple`
            A tuple of (motion_states, in_positions).
        """

        self._states["motion"].setText(", ".join([value.name for value in motion[0]]))
        self._states["in_position"].setText(", ".join([str(value) for value in motion[1]]))

    def _set_signal_fault_code(self, signal: SignalFaultCode) -> None:
        """Set the fault code signal.

        Parameters
        ----------
        signal : `SignalFaultCode`
            Signal.
        """

        signal.rear_access_door.connect(self._callback_update_fault_code)

    @asyncSlot()
    async def _callback_update_fault_code(self, fault_code: str) -> None:
        """Callback to update the fault code.

        Parameters
        ----------
        fault_code : `str`
            Fault code.
        """

        self._window_fault_code.clear()

        if fault_code != "":
            self._window_fault_code.setPlainText(fault_code)
