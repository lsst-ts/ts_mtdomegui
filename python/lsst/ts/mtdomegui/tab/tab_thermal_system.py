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
from lsst.ts.mtdomecom import (
    THCS_NUM_CABINET_TEMPERATURES,
    THCS_NUM_MOTOR_COIL_TEMPERATURES,
    THCS_NUM_MOTOR_DRIVE_TEMPERATURES,
)
from lsst.ts.xml.enums import MTDome
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..model import Model
from ..signals import SignalTelemetry
from .tab_figure import TabFigure
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

        num_motor_sensors = (
            THCS_NUM_MOTOR_DRIVE_TEMPERATURES + THCS_NUM_MOTOR_COIL_TEMPERATURES
        )
        self._sensors = {
            "motor": self._create_sensors(num_motor_sensors),
            "cabinet": self._create_sensors(THCS_NUM_CABINET_TEMPERATURES),
        }
        self._temperatures = {
            "motor": [0.0] * num_motor_sensors,
            "cabinet": [0.0] * THCS_NUM_CABINET_TEMPERATURES,
        }

        # By default, show all the motor temperature data on the real-time
        # chart.
        self._selections = list(range(num_motor_sensors))

        self._figures = {
            "motor": self._create_figure(),
            "cabinet": TabFigure(
                "Cabinet",
                self.model,
                "deg C",
                [str(idx) for idx in range(THCS_NUM_CABINET_TEMPERATURES)],
            ),
        }

        self._tab_selector = self._create_tab_selector()

        self._buttons = self._create_buttons()

        # Timer to update the realtime figure
        self._timer = self.create_and_start_timer(
            self._callback_time_out, self.model.duration_refresh
        )

        self.set_widget_and_layout()

        self._set_signal_telemetry(self.model.reporter.signals["telemetry"])  # type: ignore[arg-type]

    def _create_sensors(self, num: int) -> list[QLabel]:
        """Create the sensors.

        Parameters
        ----------
        num : `int`
            Number of the sensors.

        Returns
        -------
        `list`
            Sensors.
        """

        return [create_label() for _ in range(num)]

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
            "Motor Temperature",
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
            "Motor Sensor",
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
            "Select Motor Sensor",
            self._tab_selector.show,
            tool_tip="Select the motor sensors to show on the real-time chart.",
        )

        button_update = set_button(
            "Update Motor Temperature",
            self._callback_update,
            tool_tip="Update th real-time chart based on the selection.",
        )

        button_cabinet = set_button(
            "Show Cabinet Temperature",
            self._figures["cabinet"].show,
            tool_tip="Click to open the real-time chart.",
        )

        return {
            "selector": button_selector,
            "update": button_update,
            "cabinet": button_cabinet,
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
        layout.replaceWidget(self._figures["motor"], new_figure)

        self.setLayout(layout)

        # Update the figure
        self._figures["motor"] = new_figure

        # Resume the timeout signal
        self._timer.blockSignals(False)

    def create_layout(self) -> QHBoxLayout:

        # First column
        layout_sensor = QVBoxLayout()
        layout_sensor.addWidget(
            self._create_group_sensor(
                self._sensors["cabinet"],
                "Cabinet",
                [sensor.name for sensor in MTDome.CabinetSensor],
                0,
                THCS_NUM_CABINET_TEMPERATURES,
            )
        )
        layout_sensor.addWidget(
            self._create_group_sensor(
                self._sensors["motor"],
                "Motor Drive",
                [sensor.name for sensor in MTDome.AzimuthMotorSensor],
                0,
                THCS_NUM_MOTOR_DRIVE_TEMPERATURES,
            )
        )
        layout_sensor.addWidget(
            self._create_group_sensor(
                self._sensors["motor"],
                "Motor Coil",
                [sensor.name for sensor in MTDome.AzimuthMotor],
                THCS_NUM_MOTOR_DRIVE_TEMPERATURES,
                THCS_NUM_MOTOR_DRIVE_TEMPERATURES + THCS_NUM_MOTOR_COIL_TEMPERATURES,
            )
        )

        for button in self._buttons.values():
            layout_sensor.addWidget(button)

        # Second column
        layout_realtime = QVBoxLayout()
        layout_realtime.addWidget(self._figures["motor"])

        layout = QHBoxLayout()
        layout.addLayout(layout_sensor)
        layout.addLayout(layout_realtime)

        return layout

    def _create_group_sensor(
        self,
        sensors: list[QLabel],
        name_group: str,
        name_sensor: list[str],
        idx_start: int,
        idx_end: int,
    ) -> QGroupBox:
        """Create the group of sensor.

        Parameters
        ----------
        sensors : `list`
            Sensors.
        name_group : `str`
            Group name.
        name_sensor : `list` [`str`]
            Sensor name.
        idx_start : `int`
            Starting index of the sensor.
        idx_end : `int`
            Ending index of the sensor.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        selected_sensors = sensors[idx_start:idx_end]
        for idx, sensor in enumerate(selected_sensors):
            layout.addRow(f"{name_sensor[idx]} ({idx_start + idx}):", sensor)

        return create_group_box(name_group, layout)

    @asyncSlot()
    async def _callback_time_out(self) -> None:
        """Callback timeout function to update the realtime figure."""

        for idx, selection in enumerate(self._selections):
            self._figures["motor"].append_data(
                self._temperatures["motor"][selection], idx=idx
            )

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

        self._temperatures["motor"] = (
            telemetry["driveTemperature"] + telemetry["motorCoilTemperature"]
        )
        self._temperatures["cabinet"] = telemetry["cabinetTemperature"]

        for atype in self._sensors.keys():
            for sensor, temperature in zip(
                self._sensors[atype], self._temperatures[atype]
            ):
                sensor.setText(f"{temperature:.2f} deg C")

        # Real-time chart. Note the self._figures["motor"] is put in the
        # sefl._callback_time_out() instead. This is because the
        # self._figures["cabinet"] will only show the chart when the user
        # clicks the self._buttons["cabinet"] button.
        self._figures["cabinet"].append_data(self._temperatures["cabinet"])
