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

from lsst.ts.guitool import (
    TabTemplate,
    create_group_box,
    create_label,
    create_radio_indicators,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from ..constants import (
    NUM_DOOR_BRAKE,
    NUM_DOOR_LIMIT_SWITCH,
    NUM_DOOR_LOCKING_PIN,
    NUM_DRIVE_DOOR,
    NUM_RESOLVER_DOOR,
    NUM_TEMPERATURE_DOOR,
)
from ..model import Model
from ..utils import (
    add_empty_row_to_form_layout,
    combine_indicators,
    create_buttons_with_tabs,
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

        self._status = self._create_status()
        self._indicators = self._create_indicators()

        self._figures = self._create_figures()
        self._buttons = self._create_buttons()

        self.set_widget_and_layout()

        self._set_default()

    def _create_status(self) -> dict[str, QLabel | list[QLabel]]:
        """Create the status.

        Returns
        -------
        `dict`
            System status.
        """

        position_actual = [
            create_label(
                tool_tip="Measured position of the rear access door (percent open)."
            )
            for _ in range(NUM_DRIVE_DOOR)
        ]
        position_commanded = [
            create_label(
                tool_tip="Commanded position of the rear access door (percent open)."
            )
            for _ in range(NUM_DRIVE_DOOR)
        ]

        drive_torque_actual = [create_label() for _ in range(NUM_DRIVE_DOOR)]
        drive_torque_commanded = [create_label() for _ in range(NUM_DRIVE_DOOR)]
        drive_current_actual = [create_label() for _ in range(NUM_DRIVE_DOOR)]
        drive_temperature = [create_label() for _ in range(NUM_DRIVE_DOOR)]

        return {
            "position_actual": position_actual,
            "position_commanded": position_commanded,
            "drive_torque_actual": drive_torque_actual,
            "drive_torque_commanded": drive_torque_commanded,
            "drive_current_actual": drive_current_actual,
            "drive_temperature": drive_temperature,
            "power_draw": create_label(
                tool_tip="Total power drawn by all rear access door drives."
            ),
        }

    def _create_indicators(self) -> dict[str, QRadioButton | list[QRadioButton]]:
        """Create the radio indicators.

        Returns
        -------
        `dict`
            Dictionary of the indicators.
        """

        return {
            "limit_switch_open": create_radio_indicators(NUM_DOOR_LIMIT_SWITCH),
            "limit_switch_close": create_radio_indicators(NUM_DOOR_LIMIT_SWITCH),
            "pin": create_radio_indicators(NUM_DOOR_LOCKING_PIN),
            "brake": create_radio_indicators(NUM_DOOR_BRAKE),
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
            "position": TabFigure("Position", self.model, "%", ["commanded", "actual"]),
            "drive_torque": TabFigure(
                "Actual Drive Torque",
                self.model,
                "J",
                [str(idx) for idx in range(NUM_DRIVE_DOOR)],
            ),
            "drive_current": TabFigure(
                "Actual Drive Current",
                self.model,
                "A",
                [str(idx) for idx in range(NUM_DRIVE_DOOR)],
            ),
            "drive_temperature": TabFigure(
                "Drive Temperature",
                self.model,
                "deg C",
                [str(idx) for idx in range(NUM_TEMPERATURE_DOOR)],
            ),
            "resolver": TabFigure(
                "Calibrated Resolver",
                self.model,
                "deg",
                [str(idx) for idx in range(NUM_RESOLVER_DOOR)],
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
        layout_status = QVBoxLayout()
        layout_status.addWidget(self._create_group_position())
        layout_status.addWidget(self._create_group_drive_torque())
        layout_status.addWidget(self._create_group_drive_temperature())
        layout_status.addWidget(self._create_group_power())

        # Second column
        layout_realtime = QVBoxLayout()
        layout_realtime.addWidget(self._create_group_safety())
        layout_realtime.addWidget(self._create_group_realtime_chart())

        layout = QHBoxLayout()
        layout.addLayout(layout_status)
        layout.addLayout(layout_realtime)

        return layout

    def _create_group_position(self) -> QGroupBox:
        """Create the group of position.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        for idx in range(NUM_DRIVE_DOOR):
            layout.addRow(
                f"Position {idx} (commanded):",
                self._status["position_commanded"][idx],
            )
            layout.addRow(
                f"Position {idx} (actual):",
                self._status["position_actual"][idx],
            )

            if idx != (NUM_DRIVE_DOOR - 1):
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

        for idx in range(NUM_DRIVE_DOOR):
            layout.addRow(
                f"Torque {idx} (commanded):",
                self._status["drive_torque_commanded"][idx],
            )
            layout.addRow(
                f"Torque {idx} (actual):", self._status["drive_torque_actual"][idx]
            )
            add_empty_row_to_form_layout(layout)

        for idx in range(NUM_DRIVE_DOOR):
            layout.addRow(
                f"Current {idx} (actual):", self._status["drive_current_actual"][idx]
            )

        return create_group_box("Drive Torque", layout)

    def _create_group_drive_temperature(self) -> QGroupBox:
        """Create the group of drive temperature.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        for idx in range(NUM_TEMPERATURE_DOOR):
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

        layout.addRow(
            "Photoelectric sensor clear:", self._indicators["photoelectric_sensor"]
        )
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

    def _set_default(self) -> None:
        """Set the default values."""

        for idx in range(NUM_DRIVE_DOOR):
            self._status["position_commanded"][idx].setText("0")
            self._status["position_actual"][idx].setText("0")

            self._status["drive_torque_commanded"][idx].setText("0 J")
            self._status["drive_torque_actual"][idx].setText("0 J")
            self._status["drive_current_actual"][idx].setText("0 A")

        for idx in range(NUM_TEMPERATURE_DOOR):
            self._status["drive_temperature"][idx].setText("0 deg C")

        self._status["power_draw"].setText("0 W")  # type: ignore[union-attr]

        for indicators in self._indicators.values():
            if isinstance(indicators, QRadioButton):
                update_boolean_indicator_status(indicators, False)
                continue

            for indicator in indicators:
                update_boolean_indicator_status(indicator, False)
