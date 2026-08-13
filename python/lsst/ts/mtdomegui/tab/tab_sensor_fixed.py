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

__all__ = ["TabSensorFixed"]

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QLabel, QRadioButton, QVBoxLayout
from qasync import asyncSlot

from lsst.ts.guitool import (
    ButtonStatus,
    TabTemplate,
    create_group_box,
    create_label,
    create_radio_indicators,
    update_button_color,
)

from ..model import Model
from ..signals import SignalSensor


class TabSensorFixed(TabTemplate):
    """Table of the sensor of fixed part.

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

        self._indicators = self._create_indicators()

        self.set_widget_and_layout()

        signals = self.model.reporter.signals
        self._set_signal_sensor(signals["sensor"])  # type: ignore[arg-type]

    def _create_indicators(self) -> dict[str, dict[str, QRadioButton | QLabel]]:
        """Creates the sensor indicators.

        Returns
        -------
        indicators : `dict` [`str`, `dict`]
            Sensor indicators.
        """

        interlocks_and_sensors = self.model.reporter.status.interlocks_and_sensors

        indicators: dict[str, dict[str, QRadioButton | QLabel]] = dict()
        for key in interlocks_and_sensors.keys():
            if key.startswith("sensorsFixedPart"):
                # Create the indicators
                indicators[key] = dict()
                if key == "sensorsFixedPartValves":
                    for sensor in interlocks_and_sensors[key].keys():
                        indicators[key][sensor] = create_label()
                else:
                    num = len(interlocks_and_sensors[key].keys())
                    radio_indicators = create_radio_indicators(num)
                    for idx, sensor in enumerate(interlocks_and_sensors[key].keys()):
                        indicators[key][sensor] = radio_indicators[idx]

                # Set the tool tip
                # Add the description from "moncs_status.json" in ts_mtdomecom.
                for sensor in indicators[key].keys():
                    match sensor:
                        case "manualRotation":
                            indicators[key][sensor].setToolTip("True means manual rotation is active.")

                        case "adbsLocalBoxEmergencyPushbutton":
                            indicators[key][sensor].setToolTip(
                                "True means the emergency pushbutton is pressed."
                            )

                        case "iftpPdc1Doors":
                            indicators[key][sensor].setToolTip("True means the cabinet doors are closed.")

                        case "adbsLoto":
                            indicators[key][sensor].setToolTip(
                                "True if external LOTO mechanism at 6th floor is active."
                            )

                        case "brakes":
                            indicators[key][sensor].setToolTip("True if az brakes are disengaged.")

                        case _:
                            pass

        return indicators

    def create_layout(self) -> QVBoxLayout:
        layout = QHBoxLayout()

        counter_max = 15
        counter_current = 0
        layout_internal = QVBoxLayout()
        for group_key in self._indicators.keys():
            group, num = self._create_group_sensor(group_key)

            # Add the description from "moncs_status.json" in ts_mtdomecom.
            match group_key:
                case "sensorsFixedPartLines24V":
                    group.setToolTip(
                        "Groups all 24 V lines feedback. True means that 24 V\nare present in the line."
                    )

                case "sensorsFixedPartValves":
                    group.setToolTip(
                        "Percentage value of the valves used for thermal control\n"
                        "of +IFTP.PDC1 cabinet and azimuth motors."
                    )

                case _:
                    pass

            layout_internal.addWidget(group)
            counter_current += num

            if counter_current >= counter_max:
                layout.addLayout(layout_internal)
                layout_internal = QVBoxLayout()
                counter_current = 0

        if counter_current > 0:
            layout.addLayout(layout_internal)

        return layout

    def _create_group_sensor(self, group_key: str) -> tuple[QGroupBox, int]:
        """Create the group of sensor.

        Parameters
        ----------
        group_key : `str`
            Group key of the sensors.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        `int`
            Number of the indicators.
        """

        layout = QFormLayout()

        indicators = self._indicators[group_key]
        for key in indicators.keys():
            layout.addRow(f"{key}:", indicators[key])

        return create_group_box(group_key, layout), len(indicators)

    def _set_signal_sensor(self, signal: SignalSensor) -> None:
        """Set the sensor signal.

        Parameters
        ----------
        signal : `SignalSensor`
            Sensor signal.
        """

        signal.fixed_part_alarms.connect(self._callback_sensor_alarms)
        signal.fixed_part_inflatable_seal.connect(self._callback_sensor_inflatable_seal)
        signal.fixed_part_lines_24v.connect(self._callback_sensor_lines_24v)
        signal.fixed_part_selectors.connect(self._callback_sensor_selectors)
        signal.fixed_part_valves.connect(self._callback_sensor_valves)
        signal.fixed_part.connect(self._callback_sensor_fixed_part)

    @asyncSlot()
    async def _callback_sensor_alarms(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of alarms.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsFixedPartAlarms", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_inflatable_seal(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of inflatable seal.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsFixedPartInflatableSeal", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_lines_24v(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of lines 24v.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsFixedPartLines24V", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_selectors(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of selectors.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsFixedPartSelectors", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_valves(self, sensors: dict[str, float]) -> None:
        """Callback to update the sensor of valves.

        Parameters
        ----------
        sensors : `dict` [`str`, `float`]
            Value of the sensors.
        """

        self.update_sensor_status("sensorsFixedPartValves", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_fixed_part(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of fixed part.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsFixedPart", sensors)  # type: ignore[arg-type]

    def update_sensor_status(self, group_name: str, sensors: dict[str, bool | float]) -> None:
        """ "Update the sensor status.

        Parameters
        ----------
        group_name : `str`
            Group name.
        sensors : `dict` [`str`, `bool` | `float`]
            Status of the sensors.
        """

        if group_name == "sensorsFixedPartValves":
            for sensor, value in sensors.items():
                self._indicators[group_name][sensor].setText(f"{value:.2f} %")
        else:
            for sensor, is_triggered in sensors.items():
                self._update_boolean_indicator_status(self._indicators[group_name][sensor], is_triggered)  # type: ignore[arg-type]

    def _update_boolean_indicator_status(self, indicator: QRadioButton, is_triggered: bool) -> None:
        """Update the boolean indicator status.

        Parameters
        ----------
        indicator : `PySide6.QtWidgets.QRadioButton`
            Indicator.
        is_triggered : `bool`
            Is triggered or not.
        """

        status = ButtonStatus.Warn if is_triggered else ButtonStatus.Default
        update_button_color(indicator, QPalette.Base, status)
