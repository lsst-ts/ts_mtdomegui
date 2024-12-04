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

__all__ = ["TabCalibration"]

from lsst.ts.guitool import TabTemplate, create_group_box, create_label
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ..model import Model
from ..utils import add_empty_row_to_form_layout, create_buttons_with_tabs
from .tab_figure import TabFigure


class TabCalibration(TabTemplate):
    """Table of the calibration screen.

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

        self._figures = self._create_figures()
        self._buttons = self._create_buttons()

        self.set_widget_and_layout()

        self._set_default()

    def _create_status(self) -> dict[str, QLabel]:
        """Create the status.

        Returns
        -------
        `dict`
            System status.
        """

        return {
            "position_actual": create_label(),
            "position_commanded": create_label(),
            "drive_torque_actual": create_label(),
            "drive_torque_commanded": create_label(),
            "drive_current_actual": create_label(),
            "drive_temperature": create_label(),
            "power_draw": create_label(
                tool_tip="Total power drawn by the calibration screen."
            ),
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
                "Position", self.model, "value", ["commanded", "actual"]
            ),
            "drive_torque": TabFigure(
                "Actual Drive Torque",
                self.model,
                "J",
                ["torque"],
            ),
            "drive_current": TabFigure(
                "Actual Drive Current",
                self.model,
                "A",
                ["current"],
            ),
            "drive_temperature": TabFigure(
                "Drive Temperature",
                self.model,
                "deg C",
                ["temperature"],
            ),
            "encoder_head": TabFigure(
                "Calibrated Encoder Head",
                self.model,
                "deg",
                ["encoder"],
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
            "Encoder Head",
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
        layout.addRow("Position (commanded):", self._status["position_commanded"])
        layout.addRow("Position (actual):", self._status["position_actual"])

        return create_group_box("Position", layout)

    def _create_group_drive_torque(self) -> QGroupBox:
        """Create the group of drive torque.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow(
            "Torque (commanded):",
            self._status["drive_torque_commanded"],
        )
        layout.addRow("Torque (actual):", self._status["drive_torque_actual"])
        add_empty_row_to_form_layout(layout)

        layout.addRow("Current (actual):", self._status["drive_current_actual"])

        return create_group_box("Drive Torque", layout)

    def _create_group_drive_temperature(self) -> QGroupBox:
        """Create the group of drive temperature.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Temperature:", self._status["drive_temperature"])

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

        self._status["position_commanded"].setText("0")
        self._status["position_actual"].setText("0")

        self._status["drive_torque_commanded"].setText("0 J")
        self._status["drive_torque_actual"].setText("0 J")
        self._status["drive_current_actual"].setText("0 A")

        self._status["drive_temperature"].setText("0 deg C")

        self._status["power_draw"].setText("0 W")
