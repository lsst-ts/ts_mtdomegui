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

__all__ = ["TabAzimuth"]

from lsst.ts.guitool import TabTemplate, create_group_box, create_label
from lsst.ts.xml.enums import MTDome
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ..constants import NUM_DRIVE_AZIMUTH, NUM_POSITION_AZIMUTH, NUM_TEMPERATURE_AZIMUTH
from ..enums import ResponseCode
from ..model import Model
from ..utils import add_empty_row_to_form_layout, create_buttons_with_tabs
from .tab_figure import TabFigure


class TabAzimuth(TabTemplate):
    """Table of the azimuth.

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

        self._figures = self._create_figures()
        self._buttons = self._create_buttons()

        self.set_widget_and_layout()

        self._set_default()

    def _create_states(self) -> dict[str, QLabel]:
        """Create the states.

        Returns
        -------
        `dict`
            System states.
        """

        return {
            "state": create_label(),
            "fault_code": create_label(),
            "motion": create_label(),
            "in_position": create_label(),
            "target_position": create_label(),
            "target_velocity": create_label(),
        }

    def _create_status(self) -> dict[str, QLabel | list[QLabel]]:
        """Create the status.

        Returns
        -------
        `dict`
            System status.
        """

        drive_torque_actual = [create_label() for _ in range(NUM_DRIVE_AZIMUTH)]
        drive_torque_commanded = [create_label() for _ in range(NUM_DRIVE_AZIMUTH)]
        drive_current_actual = [create_label() for _ in range(NUM_DRIVE_AZIMUTH)]
        drive_temperature = [create_label() for _ in range(NUM_TEMPERATURE_AZIMUTH)]

        return {
            "position_actual": create_label(),
            "position_commanded": create_label(),
            "velocity_actual": create_label(),
            "velocity_commanded": create_label(),
            "drive_torque_actual": drive_torque_actual,
            "drive_torque_commanded": drive_torque_commanded,
            "drive_current_actual": drive_current_actual,
            "drive_temperature": drive_temperature,
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
                "Position", self.model, "deg", ["commanded", "actual"]
            ),
            "velocity": TabFigure(
                "Velocity", self.model, "deg/sec", ["commanded", "actual"]
            ),
            "drive_torque": TabFigure(
                "Actual Drive Torque",
                self.model,
                "J",
                [str(idx) for idx in range(NUM_DRIVE_AZIMUTH)],
            ),
            "drive_current": TabFigure(
                "Actual Drive Current",
                self.model,
                "A",
                [str(idx) for idx in range(NUM_DRIVE_AZIMUTH)],
            ),
            "drive_temperature": TabFigure(
                "Drive Temperature",
                self.model,
                "deg C",
                [str(idx) for idx in range(NUM_TEMPERATURE_AZIMUTH)],
            ),
            "encoder_head": TabFigure(
                "Calibrated Encoder Head",
                self.model,
                "deg",
                [str(idx) for idx in range(NUM_DRIVE_AZIMUTH)],
            ),
            "position_encoder": TabFigure(
                "Calibrated Position Encoder",
                self.model,
                "deg",
                [str(idx) for idx in range(NUM_POSITION_AZIMUTH)],
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
            "Velocity",
            "Drive Torque",
            "Drive Current",
            "Drive Temperature",
            "Encoder Head",
            "Position Encoder",
        ]
        return create_buttons_with_tabs(names, self._figures)

    def create_layout(self) -> QHBoxLayout:

        # First column
        layout_state = QVBoxLayout()
        layout_state.addWidget(self._create_group_state())
        layout_state.addWidget(self._create_group_target())
        layout_state.addWidget(self._create_group_position())

        # Second column
        layout_status = QVBoxLayout()
        layout_status.addWidget(self._create_group_drive_torque())

        # Third column
        layout_temperature = QVBoxLayout()
        layout_temperature.addWidget(self._create_group_drive_temperature())

        # Fourth column
        layout_realtime = QVBoxLayout()
        layout_realtime.addWidget(self._create_group_realtime_chart())

        layout = QHBoxLayout()
        layout.addLayout(layout_state)
        layout.addLayout(layout_status)
        layout.addLayout(layout_temperature)
        layout.addLayout(layout_realtime)

        return layout

    def _create_group_state(self) -> QGroupBox:
        """Create the group of state.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("State:", self._states["state"])
        layout.addRow("Motion:", self._states["motion"])
        layout.addRow("In position:", self._states["in_position"])

        add_empty_row_to_form_layout(layout)

        layout.addRow("Fault code:", self._states["fault_code"])

        return create_group_box("State", layout)

    def _create_group_target(self) -> QGroupBox:
        """Create the group of target.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Position:", self._states["target_position"])
        layout.addRow("Velocity:", self._states["target_velocity"])

        return create_group_box("Target", layout)

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

        add_empty_row_to_form_layout(layout)

        layout.addRow("Velocity (commanded):", self._status["velocity_commanded"])
        layout.addRow("Velocity (actual):", self._status["velocity_actual"])

        return create_group_box("Position", layout)

    def _create_group_drive_torque(self) -> QGroupBox:
        """Create the group of drive torque.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        for idx in range(NUM_DRIVE_AZIMUTH):
            layout.addRow(
                f"Torque {idx} (commanded):",
                self._status["drive_torque_commanded"][idx],
            )
            layout.addRow(
                f"Torque {idx} (actual):", self._status["drive_torque_actual"][idx]
            )
            add_empty_row_to_form_layout(layout)

        for idx in range(NUM_DRIVE_AZIMUTH):
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

        for idx in range(NUM_TEMPERATURE_AZIMUTH):
            layout.addRow(f"Temperature {idx}:", self._status["drive_temperature"][idx])

        return create_group_box("Drive Temperature", layout)

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

        self._states["state"].setText(MTDome.EnabledState.DISABLED.name)
        self._states["motion"].setText(MTDome.MotionState.STOPPED.name)
        self._states["in_position"].setText("False")

        self._states["fault_code"].setText(ResponseCode.OK.name)

        self._states["target_position"].setText("0 deg")
        self._states["target_velocity"].setText("0 deg/sec")

        self._status["position_commanded"].setText("0 deg")  # type: ignore[union-attr]
        self._status["position_actual"].setText("0 deg")  # type: ignore[union-attr]

        self._status["velocity_commanded"].setText("0 deg/sec")  # type: ignore[union-attr]
        self._status["velocity_actual"].setText("0 deg/sec")  # type: ignore[union-attr]

        for idx in range(NUM_DRIVE_AZIMUTH):
            self._status["drive_torque_commanded"][idx].setText("0 J")
            self._status["drive_torque_actual"][idx].setText("0 J")
            self._status["drive_current_actual"][idx].setText("0 A")

        for idx in range(NUM_TEMPERATURE_AZIMUTH):
            self._status["drive_temperature"][idx].setText("0 deg C")
