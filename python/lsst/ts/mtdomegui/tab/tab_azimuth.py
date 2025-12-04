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

import numpy as np
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from qasync import asyncSlot

from lsst.ts.guitool import TabTemplate, create_group_box, create_label
from lsst.ts.mtdomecom import AMCS_NUM_MOTORS, AMCS_NUM_RESOLVERS
from lsst.ts.xml.enums import MTDome

from ..model import Model
from ..signals import (
    SignalFaultCode,
    SignalMotion,
    SignalState,
    SignalTarget,
    SignalTelemetry,
)
from ..utils import (
    add_empty_row_to_form_layout,
    create_buttons_with_tabs,
    create_window_fault_code,
)
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
        self._window_fault_code = create_window_fault_code()

        self._figures = self._create_figures()
        self._buttons = self._create_buttons()

        self.set_widget_and_layout()

        signals = self.model.reporter.signals
        self._set_signal_telemetry(signals["telemetry"])  # type: ignore[arg-type]
        self._set_signal_target(signals["target"])  # type: ignore[arg-type]
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

        drive_torque_actual = [create_label() for _ in range(AMCS_NUM_MOTORS)]
        drive_torque_commanded = [create_label() for _ in range(AMCS_NUM_MOTORS)]
        drive_current_actual = [create_label() for _ in range(AMCS_NUM_MOTORS)]

        return {
            "position_actual": create_label(),
            "position_commanded": create_label(),
            "velocity_actual": create_label(),
            "velocity_commanded": create_label(),
            "drive_torque_actual": drive_torque_actual,
            "drive_torque_commanded": drive_torque_commanded,
            "drive_current_actual": drive_current_actual,
        }

    def _create_figures(self) -> dict[str, TabFigure]:
        """Create the figures.

        Returns
        -------
        `dict`
            Figures.
        """

        return {
            "position": TabFigure("Position", self.model, "deg", ["commanded", "actual"]),
            "velocity": TabFigure("Velocity", self.model, "deg/sec", ["commanded", "actual"]),
            "drive_torque": TabFigure(
                "Actual Drive Torque",
                self.model,
                "N*m",
                [str(idx) for idx in range(AMCS_NUM_MOTORS)],
            ),
            "drive_current": TabFigure(
                "Actual Drive Current",
                self.model,
                "A",
                [str(idx) for idx in range(AMCS_NUM_MOTORS)],
            ),
            "encoder_head": TabFigure(
                "Calibrated Encoder Head",
                self.model,
                "deg",
                [str(idx) for idx in range(AMCS_NUM_MOTORS)],
            ),
            "position_encoder": TabFigure(
                "Calibrated Position Encoder",
                self.model,
                "deg",
                [str(idx) for idx in range(AMCS_NUM_RESOLVERS)],
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
        layout_realtime = QVBoxLayout()
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
        group : `PySide6.QtWidgets.QGroupBox`
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

        for idx in range(AMCS_NUM_MOTORS):
            layout.addRow(
                f"Torque {idx} (commanded):",
                self._status["drive_torque_commanded"][idx],
            )
            layout.addRow(f"Torque {idx} (actual):", self._status["drive_torque_actual"][idx])
            add_empty_row_to_form_layout(layout)

        for idx in range(AMCS_NUM_MOTORS):
            layout.addRow(f"Current {idx} (actual):", self._status["drive_current_actual"][idx])

        return create_group_box("Drive Torque", layout)

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

        signal.amcs.connect(self._callback_telemetry)

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
        self._status["position_commanded"].setText(  # type: ignore[union-attr]
            f"{position_commanded:.2f} deg"
        )
        self._status["position_actual"].setText(f"{position_actual:.2f} deg")  # type: ignore[union-attr]

        velocity_commanded = telemetry["velocityCommanded"]
        velocity_actual = telemetry["velocityActual"]
        self._status["velocity_commanded"].setText(  # type: ignore[union-attr]
            f"{velocity_commanded:.2f} deg/sec"
        )
        self._status["velocity_actual"].setText(f"{velocity_actual:.2f} deg/sec")  # type: ignore[union-attr]

        for idx in range(AMCS_NUM_MOTORS):
            self._status["drive_torque_commanded"][idx].setText(
                f"{telemetry['driveTorqueCommanded'][idx]:.2f} N*m"
            )
            self._status["drive_torque_actual"][idx].setText(f"{telemetry['driveTorqueActual'][idx]:.2f} N*m")
            self._status["drive_current_actual"][idx].setText(f"{telemetry['driveCurrentActual'][idx]:.2f} A")

        # Real-time chart

        # In the crawing, the commanded position is NaN
        if np.isnan(position_commanded):
            position_commanded = position_actual

        self._figures["position"].append_data([position_commanded, position_actual])
        self._figures["velocity"].append_data([velocity_commanded, velocity_actual])

        self._figures["drive_torque"].append_data(telemetry["driveTorqueActual"])
        self._figures["drive_current"].append_data(telemetry["driveCurrentActual"])

        self._figures["encoder_head"].append_data(telemetry["encoderHeadCalibrated"])
        self._figures["position_encoder"].append_data(telemetry["barcodeHeadCalibrated"])

    def _set_signal_target(self, signal: SignalTarget) -> None:
        """Set the target signal.

        Parameters
        ----------
        signal : `SignalTarget`
            Signal.
        """

        signal.position_velocity_azimuth.connect(self._callback_target)

    @asyncSlot()
    async def _callback_target(self, position_velocity: tuple[float, float]) -> None:
        """Callback to update the target.

        Parameters
        ----------
        position_velocity : `tuple`
            A tuple of (position, velocity) in deg and deg/sec at azimuth
            direction.
        """

        self._states["target_position"].setText(f"{position_velocity[0]:.2f} deg")
        self._states["target_velocity"].setText(f"{position_velocity[1]:.2f} deg/sec")

    def _set_signal_state(self, signal: SignalState) -> None:
        """Set the state signal.

        Parameters
        ----------
        signal : `SignalState`
            Signal.
        """

        signal.azimuth_axis.connect(self._callback_update_state)

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

        signal.azimuth_axis.connect(self._callback_update_motion)

    @asyncSlot()
    async def _callback_update_motion(self, motion: tuple[MTDome.MotionState, bool]) -> None:
        """Callback to update the motion state.

        Parameters
        ----------
        motion : `tuple`
            A tuple of (motion_state, in_position).
        """

        self._states["motion"].setText(motion[0].name)
        self._states["in_position"].setText(str(motion[1]))

    def _set_signal_fault_code(self, signal: SignalFaultCode) -> None:
        """Set the fault code signal.

        Parameters
        ----------
        signal : `SignalFaultCode`
            Signal.
        """

        signal.azimuth_axis.connect(self._callback_update_fault_code)

    @asyncSlot()
    async def _callback_update_fault_code(self, fault_code: str) -> None:
        """Callback to update the fault code.

        Parameters
        ----------
        fault_code : `tuple`
            Fault code.
        """

        self._window_fault_code.clear()

        if fault_code != "":
            self._window_fault_code.setPlainText(fault_code)
