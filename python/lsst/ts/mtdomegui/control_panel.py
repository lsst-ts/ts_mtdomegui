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

__all__ = ["ControlPanel"]

from functools import partial

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QFormLayout, QGroupBox, QVBoxLayout, QWidget
from qasync import asyncSlot

from lsst.ts.guitool import (
    ButtonStatus,
    create_group_box,
    create_label,
    set_button,
    update_button_color,
)

# TODO: OSW-1538, remove the Brake and ControlMode after the ts_xml: 24.4.
from lsst.ts.mtdomecom import Brake, ControlMode
from lsst.ts.xml.enums import MTDome

from .model import Model
from .signals import SignalInterlock, SignalState
from .tab import TabBrake, TabInterlock
from .utils import add_empty_row_to_form_layout


class ControlPanel(QWidget):
    """Control panel.

    Parameters
    ----------
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    def __init__(self, model: Model) -> None:
        super().__init__()

        self.model = model

        self._tab_interlock = TabInterlock("Interlock", self.model)
        self._tab_brake = TabBrake("Brake", self.model)

        self._button_interlock = set_button(
            "",
            self._tab_interlock.show,
            tool_tip="Click to show the interlocks.",
        )
        self._button_brake_engaged = set_button(
            "",
            self._tab_brake.show,
            tool_tip="Click to show the engaged brakes.",
        )

        self._labels = {
            "locking_pin": create_label(),
            "azimuth_axis": create_label(),
            "elevation_axis": create_label(),
            "aperture_shutter": create_label(),
            "louvers": create_label(),
            "rear_access_door": create_label(),
            "calibration_screen": create_label(),
            "power_mode": create_label(),
            "control_mode": create_label(),
        }

        self.setLayout(self._create_layout())

        signals = self.model.reporter.signals
        self._set_signal_interlock(signals["interlock"])  # type: ignore[arg-type]
        self._set_signal_state(signals["state"])  # type: ignore[arg-type]

    def _create_layout(self) -> QVBoxLayout:
        """Set the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()
        layout.addWidget(self._create_group_summary())

        return layout

    def _create_group_summary(self) -> QGroupBox:
        """Create the group of summary.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("Interlock:", self._button_interlock)
        layout.addRow("Locking pin:", self._labels["locking_pin"])

        add_empty_row_to_form_layout(layout)

        layout.addRow("Brake engaged:", self._button_brake_engaged)
        layout.addRow("Azimuth axis:", self._labels["azimuth_axis"])
        layout.addRow("Elevation axis:", self._labels["elevation_axis"])
        layout.addRow("Aperture shutter:", self._labels["aperture_shutter"])
        layout.addRow("Louvers:", self._labels["louvers"])
        layout.addRow("Rear access door:", self._labels["rear_access_door"])
        layout.addRow("Calibration screen:", self._labels["calibration_screen"])

        add_empty_row_to_form_layout(layout)

        layout.addRow("Power mode:", self._labels["power_mode"])
        layout.addRow("Control mode:", self._labels["control_mode"])

        return create_group_box("Summary", layout)

    def _set_signal_interlock(self, signal: SignalInterlock) -> None:
        """Set the interlock signal.

        Parameters
        ----------
        signal : `SignalInterlock`
        """

        signal.interlock.connect(self._callback_interlock)
        signal.locking_pins_engaged.connect(partial(self._callback_update_label, "locking_pin"))

    @asyncSlot()
    async def _callback_interlock(self, interlocks: list[bool]) -> None:
        """Callback to update the interlock.

        Parameters
        ----------
        interlocks : `list` [`bool`]
            Status of the interlocks. True is latched. Otherwise, False.
        """

        for index, is_triggered in enumerate(interlocks):
            self._tab_interlock.update_interlock_status(index, is_triggered)

        self._update_button_interlock(any(interlocks))

    def _update_button_interlock(self, is_triggered: bool) -> None:
        """Update the button of interlock.

        Parameters
        ----------
        is_triggered : `bool`
            Is triggered or not.
        """

        name = MTDome.OnOff.ON.name if is_triggered else MTDome.OnOff.OFF.name
        self._button_interlock.setText(name)

        button_status = ButtonStatus.Error if is_triggered else ButtonStatus.Normal
        update_button_color(self._button_interlock, QPalette.Button, button_status)

    @asyncSlot()
    async def _callback_update_label(
        self,
        field: str,
        value: int,
        enum: MTDome.EnabledState | MTDome.PowerManagementMode | ControlMode | None = None,
    ) -> None:
        """Callback to update the label.

        Parameters
        ----------
        field : `str`
            Field.
        value : `int`
            Value.
        enum: `MTDome.EnabledState` or `MTDome.PowerManagementMode` or
        `lsst.ts.mtdome.ControlMode` or None
            Enum to convert the value. If None, the hex value will be shown.
        """

        # TODO: OSW-1538, update the annotation of enum and related doc string
        # to use the MTDome.ControlMode after ts_xml 24.4.

        if enum is None:
            self._labels[field].setText(hex(value))
        else:
            self._labels[field].setText(enum(value).name)

    def _set_signal_state(self, signal: SignalState) -> None:
        """Set the state signal.

        Parameters
        ----------
        signal : `SignalState`
            Signal.
        """

        signal.brake_engaged.connect(self._callback_update_brake_engaged)
        signal.azimuth_axis.connect(
            partial(self._callback_update_label, "azimuth_axis", enum=MTDome.EnabledState)
        )
        signal.elevation_axis.connect(
            partial(self._callback_update_label, "elevation_axis", enum=MTDome.EnabledState)
        )
        signal.aperture_shutter.connect(
            partial(
                self._callback_update_label,
                "aperture_shutter",
                enum=MTDome.EnabledState,
            )
        )
        signal.louvers.connect(
            partial(
                self._callback_update_label,
                "louvers",
                enum=MTDome.EnabledState,
            )
        )
        signal.rear_access_door.connect(
            partial(
                self._callback_update_label,
                "rear_access_door",
                enum=MTDome.EnabledState,
            )
        )
        signal.calibration_screen.connect(
            partial(
                self._callback_update_label,
                "calibration_screen",
                enum=MTDome.EnabledState,
            )
        )

        signal.power_mode.connect(
            partial(
                self._callback_update_label,
                "power_mode",
                enum=MTDome.PowerManagementMode,
            )
        )

        # TODO: OSW-1538, use the MTDome.ControlMode after the ts_xml: 24.4.
        signal.control_mode.connect(
            partial(
                self._callback_update_label,
                "control_mode",
                enum=ControlMode,
            )
        )

    @asyncSlot()
    async def _callback_update_brake_engaged(self, brake_engaged: int) -> None:
        """Callback to update the brake engaged button.

        Parameters
        ----------
        brake_engaged : `int`
            Brake engaged bitmask.
        """

        self._button_brake_engaged.setText(hex(brake_engaged))

        for idx, specific_brake in enumerate(Brake):
            is_engaged = bool(brake_engaged & (1 << specific_brake.value))
            self._tab_brake.update_brake_status(idx, is_engaged)
