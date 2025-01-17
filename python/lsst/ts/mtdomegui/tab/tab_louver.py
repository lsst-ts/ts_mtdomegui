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

__all__ = ["TabLouver"]

from lsst.ts.guitool import (
    TabTemplate,
    create_grid_layout_buttons,
    create_group_box,
    create_label,
    set_button,
)
from lsst.ts.mtdomecom import LCS_NUM_MOTORS_PER_LOUVER
from lsst.ts.xml.enums import MTDome
from PySide6.QtWidgets import QFormLayout, QGroupBox, QPushButton, QVBoxLayout
from qasync import asyncSlot

from ..model import Model
from ..signals import SignalTelemetry
from .tab_figure import TabFigure
from .tab_louver_single import TabLouverSingle


class TabLouver(TabTemplate):
    """Table of the louver.

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

        self._power = create_label(tool_tip="Total power drawn by all louver drives.")
        self._figure = TabFigure(
            "Total Power",
            self.model,
            "W",
            ["power"],
        )

        self._tabs = self._create_tabs()
        self._buttons = self._create_buttons()

        self.set_widget_and_layout()

        self._set_signal_telemetry(self.model.reporter.signals["telemetry"])  # type: ignore[arg-type]

    def _create_tabs(self) -> list[TabLouverSingle]:
        """Create the tabs.

        Returns
        -------
        tabs : `list` [`TabLouverSingle`]
            Tabs.
        """

        names = self._get_louver_names()

        tabs = list()
        for name in names:
            tabs.append(TabLouverSingle(name, self.model))

        return tabs

    def _get_louver_names(self) -> list[str]:
        """Get the louver names.

        Returns
        -------
        names : `list`
            Names.
        """

        names = list()
        for idx, louver in enumerate(MTDome.Louver):
            names.append(f"{louver.name} ({idx})")

        return names

    def _create_buttons(self) -> dict[str, QPushButton | list[QPushButton]]:
        """Create the buttons.

        Returns
        -------
        buttons : `dict`
            Buttons.
        """

        tool_tip_louver = "Click to open the louver status."

        names = self._get_louver_names()

        buttons_louver = list()
        for name, tab in zip(names, self._tabs):
            button = set_button(
                name,
                tab.show,
                is_adjust_size=True,
                tool_tip=tool_tip_louver,
            )

            buttons_louver.append(button)

        return {
            "power": set_button(
                "Show Power",
                self._figure.show,
                tool_tip="Click to open the real-time chart.",
            ),
            "louver": buttons_louver,
        }

    def create_layout(self) -> QVBoxLayout:

        layout = QVBoxLayout()
        layout.addWidget(self._create_group_power())
        layout.addWidget(self._create_group_louver())

        return layout

    def _create_group_power(self) -> QGroupBox:
        """Create the group of power.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_form = QFormLayout()
        layout_form.addRow("Power:", self._power)

        layout = QVBoxLayout()
        layout.addLayout(layout_form)
        layout.addWidget(self._buttons["power"])

        return create_group_box("Power", layout)

    def _create_group_louver(self, num_column: int = 5) -> QGroupBox:
        """Create the group of louver.

        Parameters
        ----------
        num_column : `int`, optional
            Number of column on the grid layput. (the default is 5)

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = create_grid_layout_buttons(self._buttons["louver"], num_column)
        return create_group_box("Louver", layout)

    def _set_signal_telemetry(self, signal: SignalTelemetry) -> None:
        """Set the telemetry signal.

        Parameters
        ----------
        signal : `SignalTelemetry`
            Signal.
        """

        signal.lcs.connect(self._callback_telemetry)

    @asyncSlot()
    async def _callback_telemetry(self, telemetry: dict) -> None:
        """Callback to update the telemetry.

        Parameters
        ----------
        telemetry : `dict`
            Telemetry.
        """

        # Update each single louver
        num = len(self._get_louver_names())
        for idx in range(num):
            self._tabs[idx].update_position(
                telemetry["positionCommanded"][idx],
                telemetry["positionActual"][idx],
            )

        for idx in range(num):
            idx_start = idx * LCS_NUM_MOTORS_PER_LOUVER
            idx_end = idx_start + LCS_NUM_MOTORS_PER_LOUVER
            self._tabs[idx].update_drive(
                telemetry["driveTorqueCommanded"][idx_start:idx_end],
                telemetry["driveTorqueActual"][idx_start:idx_end],
                telemetry["driveCurrentActual"][idx_start:idx_end],
                telemetry["encoderHeadCalibrated"][idx_start:idx_end],
            )

        for idx in range(num):
            idx_start = idx * LCS_NUM_MOTORS_PER_LOUVER
            idx_end = idx_start + LCS_NUM_MOTORS_PER_LOUVER
            self._tabs[idx].update_temperature(
                telemetry["driveTemperature"][idx_start:idx_end],
            )

        power = telemetry["powerDraw"]
        self._power.setText(f"{power:.2f} W")  # type: ignore[union-attr]

        # Real-time chart
        self._figure.append_data([power])
