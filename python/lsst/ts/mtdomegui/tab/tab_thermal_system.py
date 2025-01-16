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

__all__ = ["TabThermalSystem"]

import asyncio

from lsst.ts.guitool import (
    FigureConstant,
    TabTemplate,
    create_group_box,
    create_label,
    set_button,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..constants import NUM_TEMPERATURE_THERMAL
from ..model import Model
from ..signals import SignalTelemetry
from .tab_selector import TabSelector


class TabThermalSystem(TabTemplate):
    """Table of the thermal system.

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

    MIN_WIDTH = 150

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title)

        self.model = model

        self._sensors = self._create_sensors()
        self._temperatures = [0.0] * NUM_TEMPERATURE_THERMAL

        # By default, show all the temperature data on the real-time chart
        self._selections = list(range(NUM_TEMPERATURE_THERMAL))

        self._figure = self._create_figure()

        self._tab_selector = self._create_tab_selector()

        self._buttons = self._create_buttons()

        # Timer to update the realtime figure
        self._timer = self.create_and_start_timer(
            self._callback_time_out, self.model.duration_refresh
        )

        self.set_widget_and_layout()

        self._set_signal_telemetry(self.model.reporter.signals["telemetry"])  # type: ignore[arg-type]

    def _create_sensors(self) -> list[QLabel]:
        """Create the sensors.

        Returns
        -------
        `list`
            Sensors.
        """

        return [create_label() for _ in range(NUM_TEMPERATURE_THERMAL)]

    def _create_figure(self, num_realtime: int = 200) -> FigureConstant:
        """Create the figure to show the temperature.

        Parameters
        ----------
        num_realtime : `int`, optional
            Number of the realtime data (>=0). (the default is 200)

        Returns
        -------
        figure : `FigureConstant`
            Figure.
        """

        names = self._get_selection_names()

        figure = FigureConstant(
            1,
            num_realtime,
            num_realtime,
            "Data Point",
            "deg C",
            "Temperature",
            names,
            num_lines=len(names),
            is_realtime=True,
        )
        figure.axis_x.setLabelFormat("%d")

        figure.setMinimumWidth(self.MIN_WIDTH)

        return figure

    def _get_selection_names(self) -> list[str]:
        """Get the selection names.

        Returns
        -------
        `list` [`str`]
            Names.
        """

        return [str(selection) for selection in self._selections]

    def _create_tab_selector(self) -> TabSelector:
        """Create the selector tab.

        Returns
        -------
        tab : `TabSelector`
            Tab.
        """

        tab = TabSelector(
            "Sensor",
            self.model,
            self._get_selection_names(),
        )
        tab.select(self._selections)

        return tab

    def _create_buttons(self) -> dict[str, QPushButton]:
        """Create the buttons.

        Returns
        -------
        `dict`
            Buttons.
        """

        button_selector = set_button(
            "Select Sensor",
            self._tab_selector.show,
            tool_tip="Select the sensors to show on the real-time chart.",
        )

        button_update = set_button(
            "Update",
            self._callback_update,
            tool_tip="Update th real-time chart based on the selection.",
        )

        return {
            "selector": button_selector,
            "update": button_update,
        }

    @asyncSlot()
    async def _callback_update(self) -> None:
        """Callback of the update button to update the selections."""

        # Block the timeout signal first. Sleep a timeout cycle to make sure
        # there should be no timeout signal to be triggered when replacing
        # the figure widget.
        self._timer.blockSignals(True)
        await asyncio.sleep(self.model.duration_refresh / 1000.0)

        # Get the selections
        self._selections = self._tab_selector.get_selection()

        # Replace the figure with the new selection
        layout = self.widget().layout()

        new_figure = self._create_figure()
        layout.replaceWidget(self._figure, new_figure)

        self.setLayout(layout)

        # Update the figure
        self._figure = new_figure

        # Resume the timeout signal
        self._timer.blockSignals(False)

    def create_layout(self) -> QHBoxLayout:

        # First column
        layout_sensor = QVBoxLayout()
        layout_sensor.addWidget(self._create_group_sensor())

        # Second column
        layout_realtime = QVBoxLayout()
        layout_realtime.addWidget(self._figure)
        layout_realtime.addWidget(self._buttons["selector"])
        layout_realtime.addWidget(self._buttons["update"])

        layout = QHBoxLayout()
        layout.addLayout(layout_sensor)
        layout.addLayout(layout_realtime)

        return layout

    def _create_group_sensor(self) -> QGroupBox:
        """Create the group of sensor.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        for idx, sensor in enumerate(self._sensors):
            layout.addRow(f"Sensor {idx}:", sensor)

        return create_group_box("Sensor", layout)

    @asyncSlot()
    async def _callback_time_out(self) -> None:
        """Callback timeout function to update the realtime figure."""

        for idx, selection in enumerate(self._selections):
            self._figure.append_data(self._temperatures[selection], idx=idx)

        self.check_duration_and_restart_timer(self._timer, self.model.duration_refresh)

    def _set_signal_telemetry(self, signal: SignalTelemetry) -> None:
        """Set the telemetry signal.

        Parameters
        ----------
        signal : `SignalTelemetry`
            Signal.
        """

        signal.thcs.connect(self._callback_telemetry)

    @asyncSlot()
    async def _callback_telemetry(self, telemetry: dict) -> None:
        """Callback to update the telemetry.

        Parameters
        ----------
        telemetry : `dict`
            Telemetry.
        """

        self._temperatures = telemetry["temperature"]

        for sensor, temperature in zip(self._sensors, self._temperatures):
            sensor.setText(f"{temperature:.2f} deg C")
