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

__all__ = ["TabLouverSingle"]

from lsst.ts.guitool import TabTemplate, create_group_box, create_label
from lsst.ts.mtdomecom import LCS_NUM_MOTORS_PER_LOUVER
from lsst.ts.xml.enums import MTDome
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


class TabLouverSingle(TabTemplate):
    """Table of the single louver.

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

    def _create_states(self) -> dict[str, QLabel]:
        """Create the states.

        Returns
        -------
        `dict`
            System states.
        """

        return {
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

        drive_torque_actual = [create_label() for _ in range(LCS_NUM_MOTORS_PER_LOUVER)]
        drive_torque_commanded = [create_label() for _ in range(LCS_NUM_MOTORS_PER_LOUVER)]
        drive_current_actual = [create_label() for _ in range(LCS_NUM_MOTORS_PER_LOUVER)]
        drive_temperature = [create_label() for _ in range(LCS_NUM_MOTORS_PER_LOUVER)]

        return {
            "position_actual": create_label(tool_tip="Measured position of louver (percent open)."),
            "position_commanded": create_label(tool_tip="Commanded position of louver (percent open)."),
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

        louver_name = self.windowTitle()

        return {
            "position": TabFigure(f"{louver_name} Position", self.model, "%", ["commanded", "actual"]),
            "drive_torque": TabFigure(
                f"{louver_name} Actual Drive Torque",
                self.model,
                "N*m",
                [str(idx) for idx in range(LCS_NUM_MOTORS_PER_LOUVER)],
            ),
            "drive_current": TabFigure(
                f"{louver_name} Actual Drive Current",
                self.model,
                "A",
                [str(idx) for idx in range(LCS_NUM_MOTORS_PER_LOUVER)],
            ),
            "drive_temperature": TabFigure(
                f"{louver_name} Drive Temperature",
                self.model,
                "deg C",
                [str(idx) for idx in range(LCS_NUM_MOTORS_PER_LOUVER)],
            ),
            "encoder_head": TabFigure(
                f"{louver_name} Calibrated Encoder Head",
                self.model,
                "deg",
                [str(idx) for idx in range(LCS_NUM_MOTORS_PER_LOUVER)],
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
        ]
        return create_buttons_with_tabs(names, self._figures)

    def create_layout(self) -> QHBoxLayout:
        # First column
        layout_status = QVBoxLayout()
        layout_status.addWidget(self._create_group_state())
        layout_status.addWidget(self._create_group_position())
        layout_status.addWidget(self._create_group_drive_torque())
        layout_status.addWidget(self._create_group_drive_temperature())

        # Second column
        layout_realtime = QVBoxLayout()
        layout_realtime.addWidget(self._create_group_realtime_chart())

        layout = QHBoxLayout()
        layout.addLayout(layout_status)
        layout.addLayout(layout_realtime)

        return layout

    def _create_group_state(self) -> QGroupBox:
        """Create the group of state.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_form = QFormLayout()
        layout_form.addRow("Motion:", self._states["motion"])
        layout_form.addRow("In position:", self._states["in_position"])

        layout = QVBoxLayout()
        layout.addLayout(layout_form)

        return create_group_box("State", layout)

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

        for idx in range(LCS_NUM_MOTORS_PER_LOUVER):
            layout.addRow(
                f"Torque {idx} (commanded):",
                self._status["drive_torque_commanded"][idx],
            )
            layout.addRow(f"Torque {idx} (actual):", self._status["drive_torque_actual"][idx])
            add_empty_row_to_form_layout(layout)

        for idx in range(LCS_NUM_MOTORS_PER_LOUVER):
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

        for idx in range(LCS_NUM_MOTORS_PER_LOUVER):
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

    def update_motion_state(self, motion_state: MTDome.MotionState, in_position: bool) -> None:
        """Update the motion state.

        Parameters
        ----------
        motion_state : enum `MTDome.MotionState`
            Motion state
        in_position : `bool`
            True if the louver is in position. Otherwise, False.
        """

        self._states["motion"].setText(motion_state.name)
        self._states["in_position"].setText(str(in_position))

    def update_position(self, position_commanded: float, position_actual: float) -> None:
        """Update the position.

        Parameters
        ----------
        position_commanded : `float`
            Commanded position.
        position_actual : `float`
            Actual position.
        """

        self._status["position_commanded"].setText(f"{position_commanded:.2f} %")  # type: ignore[union-attr]
        self._status["position_actual"].setText(f"{position_actual:.2f} %")  # type: ignore[union-attr]

        self._figures["position"].append_data([position_commanded, position_actual])

    def update_drive(
        self,
        torque_commanded: list[float],
        torque_actual: list[float],
        current_actual: list[float],
        encoder_head: list[float],
    ) -> None:
        """Update the drive.

        Parameters
        ----------
        torque_commanded : `list` [`float`]
            Commanded torque in N*m.
        torque_actual : `list` [`float`]
            Actual torque in N*m.
        current_actual : `list` [`float`]
            Actual current in A.
        encoder_head : `list` [`float`]
            Calibrated encoder head in deg.
        """

        for idx in range(LCS_NUM_MOTORS_PER_LOUVER):
            self._status["drive_torque_commanded"][idx].setText(f"{torque_commanded[idx]:.2f} N*m")
            self._status["drive_torque_actual"][idx].setText(f"{torque_actual[idx]:.2f} N*m")
            self._status["drive_current_actual"][idx].setText(f"{current_actual[idx]:.2f} A")

        self._figures["drive_torque"].append_data(torque_actual)
        self._figures["drive_current"].append_data(current_actual)

        self._figures["encoder_head"].append_data(encoder_head)

    def update_temperature(self, temperature: list[float]) -> None:
        """Update the temperature.

        Parameters
        ----------
        temperature : `list` [`float`]
            Temperature in deg C.
        """

        for idx in range(LCS_NUM_MOTORS_PER_LOUVER):
            self._status["drive_temperature"][idx].setText(f"{temperature[idx]:.2f} deg C")

        self._figures["drive_temperature"].append_data(temperature)
