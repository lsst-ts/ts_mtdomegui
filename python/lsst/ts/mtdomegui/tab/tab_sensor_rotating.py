# This file is part of ts_mtdomegui.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

__all__ = ["TabSensorRotating"]

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
from lsst.ts.xml.enums import MTDome

from ..model import Model
from ..signals import SignalSensor


class TabSensorRotating(TabTemplate):
    """Table of the sensor of rotating part.

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

        self.set_widget_and_layout(is_scrollable=True)

        signals = self.model.reporter.signals
        self._set_signal_sensor(signals["sensor"])  # type: ignore[arg-type]

    def _create_indicators(self) -> dict[str, dict[str, QRadioButton | QLabel]]:
        """Creates the sensor indicators.

        Returns
        -------
        indicators : `dict` [`str`, `dict`]
            Sensor indicators.
        """

        label_sensors = [
            "llbvRadLouverSelected",
            "llbvLocalBox1LouverSelected",
            "llbvLocalBox2LouverSelected",
            "llbvLocalBox3LouverSelected",
            "llbvLocalBox4LouverSelected",
            "llbvLocalBox5LouverSelected",
            "llbvLocalBox6LouverSelected",
        ]
        interlocks_and_sensors = self.model.reporter.status.interlocks_and_sensors

        indicators: dict[str, dict[str, QRadioButton | QLabel]] = dict()
        for key in interlocks_and_sensors.keys():
            # Create the indicators
            if key.startswith("sensorsRotatingPart"):
                indicators[key] = dict()

                num = len(interlocks_and_sensors[key].keys())
                radio_indicators = create_radio_indicators(num)
                for idx, sensor in enumerate(interlocks_and_sensors[key].keys()):
                    indicators[key][sensor] = (
                        create_label() if sensor in label_sensors else radio_indicators[idx]
                    )

                # Set the tool tip
                # Add the description from "moncs_status.json" in ts_mtdomecom.
                for sensor in indicators[key].keys():
                    match sensor:
                        case "radClosed":
                            indicators[key][sensor].setToolTip("Signal D11 sent to GIS.")

                        case "llbvRadLouverSelected":
                            indicators[key][sensor].setToolTip(
                                "Index of louver selected, among F1 (15), G1 (18),\nor none (value 0)."
                            )

                        case "llbvLocalBox1LouverSelected":
                            indicators[key][sensor].setToolTip(
                                "Index of louver selected, among A1 (1), A2 (2),\n"
                                "B1 (3), B2 (4), B3 (5), or none (value 0)."
                            )

                        case "llbvLocalBox2LouverSelected":
                            indicators[key][sensor].setToolTip(
                                "Index of louver selected, among C1 (6), C2 (7),\n"
                                "C3 (8), D1 (9), D2 (10), D3 (11) or none (value 0)."
                            )

                        case "llbvLocalBox3LouverSelected":
                            indicators[key][sensor].setToolTip(
                                "Index of louver selected, among E1 (12), E2 (13),\n"
                                "E3 (14), F2 (16), F3 (17), or none (value 0)."
                            )

                        case "llbvLocalBox4LouverSelected":
                            indicators[key][sensor].setToolTip(
                                "Index of louver selected, among G2 (19), G3 (20),\n"
                                "H1 (21), H2 (22), H3 (23), or none (value 0)."
                            )

                        case "llbvLocalBox5LouverSelected":
                            indicators[key][sensor].setToolTip(
                                "Index of louver selected, among I1 (24), I2 (25),\n"
                                "I3 (26), L1 (27), L2 (28), L3 (29) or none (value 0)."
                            )

                        case "llbvLocalBox6LouverSelected":
                            indicators[key][sensor].setToolTip(
                                "Index of louver selected, among M1 (30), M2 (31),\n"
                                "M3 (32), N1 (33), N2 (34), or none (value 0)."
                            )

                        case "apsSwitchedOn":
                            indicators[key][sensor].setToolTip(
                                "True means that the photocells are switched on.\n"
                                "False means that the photocells are switched off\n"
                                "to avoid light emission."
                            )

                        case _:
                            pass

        return indicators

    def create_layout(self) -> QVBoxLayout:
        layout = QHBoxLayout()

        max_num_form = 26

        counter_max = 17
        counter_current = 0
        layout_internal = QVBoxLayout()
        for group_key in self._indicators.keys():
            group, num = self._create_group_sensor(group_key, max_num_form)

            # Add the description from "moncs_status.json" in ts_mtdomecom.
            match group_key:
                case "sensorsRotatingPartLines24V":
                    group.setToolTip(
                        "Groups all 24 V lines feedback. True means that 24 V\nare present in the line."
                    )

                case "sensorsRotatingPartLockingPins":
                    group.setToolTip("Groups the status of all locking pins.")

                case "sensorsRotatingPartAlarms":
                    group.setToolTip("Indicates hardware alarms. True means the alarm is active.")

                case "sensorsRotatingPartDoorsClosed":
                    group.setToolTip(
                        "Indicates what cabinet doors are closed.\nTrue means the door is closed."
                    )

                case "sensorsRotatingPartCabinetFan":
                    group.setToolTip(
                        "Indicates if the fans of the following cabinets are\n"
                        "running. True means fan running."
                    )

                case "sensorsRotatingPartLimitSwitches":
                    group.setToolTip(
                        "Indicates the status of the limit switches in the\n"
                        "dome. True means limit switch engaged."
                    )

                case "sensorsRotatingPartSelectors":
                    group.setToolTip(
                        "Indicates the status of the selectors that enable the\n"
                        "local pushbuttons of the cabinets. The ones for the\n"
                        "louvers include also the currently selected louver\n"
                        "for a given group. For example, llbvLocalBox3LouverSelected\n"
                        "indicates with a number what is the louver selected\n"
                        "among E1, E2, E3, F2, F3."
                    )

                case "sensorsRotatingPartEmergencyPushbuttons":
                    group.setToolTip(
                        "Indicates which emergency pushbuttons are pressed.\n"
                        "True means emergency pushbutton pressed"
                    )

                case "sensorsRotatingPartPowerAvailable":
                    group.setToolTip(
                        "Indicates if the given subsystem receives input power.\n"
                        "True means power is received."
                    )

                case "sensorsRotatingPartHatches":
                    group.setToolTip(
                        "Indicates what hatches are closed and if the\n"
                        "corresponding override is active. True means hatch\n"
                        "closed, for the override signals it means override active."
                    )

                case "sensorsRotatingPartPhotocells":
                    group.setToolTip(
                        "Indicates if the photocell is not blocked by something.\nTrue means photocell clear."
                    )

                case "sensorsRotatingPartLightCurtain":
                    group.setToolTip(
                        "Indicates if the light curtain is not blocked by\n"
                        "something. True means light curtain clear."
                    )

                case "sensorsRotatingPartLights":
                    group.setToolTip(
                        "Indicates which light circuit is switched on at the\n"
                        "moment. True means circuit switched on."
                    )

                case "sensorsRotatingPartHeatingCables":
                    group.setToolTip("Indicates which heating cable is active. True means\ncable is heating.")

                case "sensorsRotatingPartBrakes":
                    group.setToolTip("Indicates which brakes are disengaged. True means\nbrakes disengaged.")

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

    def _create_group_sensor(self, group_key: str, counter_max: int) -> tuple[QGroupBox, int]:
        """Create the group of sensor.

        Parameters
        ----------
        group_key : `str`
            Group key of the sensors.
        counter_max : `int`
            Maximum number of indicators in a QFormLayout at each column.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        `int`
            Number of the indicators.
        """

        # Decide the number of QFormLayout
        indicators = self._indicators[group_key]
        num_form_layout = len(indicators) // counter_max + 1

        # Put the indicators to QFormLayout
        layout_forms = [QFormLayout() for _ in range(num_form_layout)]

        for idx, key in enumerate(indicators.keys()):
            layout_form = layout_forms[idx // counter_max]
            if len(layout_forms) > 1:
                layout_form.addRow(f"{key} ({idx}):", indicators[key])
            else:
                layout_form.addRow(f"{key}:", indicators[key])

        layout = QHBoxLayout()
        for layout_form in layout_forms:
            layout.addLayout(layout_form)

        return create_group_box(group_key, layout), len(indicators)

    def _set_signal_sensor(self, signal: SignalSensor) -> None:
        """Set the sensor signal.

        Parameters
        ----------
        signal : `SignalSensor`
            Sensor signal.
        """

        signal.rotating_part_lines_24v.connect(self._callback_sensor_lines_24v)
        signal.rotating_part_locking_pins.connect(self._callback_sensor_locking_pins)
        signal.rotating_part_alarms.connect(self._callback_sensor_alarms)
        signal.rotating_part_doors_closed.connect(self._callback_sensor_doors_closed)
        signal.rotating_part_cabinet_fan.connect(self._callback_sensor_cabinet_fan)
        signal.rotating_part_limit_switches.connect(self._callback_sensor_limit_switches)
        signal.rotating_part_selectors.connect(self._callback_sensor_selectors)
        signal.rotating_part_emergency_pushbuttons.connect(self._callback_sensor_emergency_pushbuttons)
        signal.rotating_part_power_available.connect(self._callback_sensor_power_available)
        signal.rotating_part_hatches.connect(self._callback_sensor_hatches)
        signal.rotating_part_photocells.connect(self._callback_sensor_photocells)
        signal.rotating_part_light_curtain.connect(self._callback_sensor_light_curtain)
        signal.rotating_part_obc.connect(self._callback_sensor_obc)
        signal.rotating_part_axial_fans.connect(self._callback_sensor_axial_fans)
        signal.rotating_part_lights.connect(self._callback_sensor_lights)
        signal.rotating_part_heating_cables.connect(self._callback_sensor_heating_cables)
        signal.rotating_part_brakes.connect(self._callback_sensor_brakes)

    @asyncSlot()
    async def _callback_sensor_lines_24v(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of line 24 V.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartLines24V", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_locking_pins(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of locking pins.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartLockingPins", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_alarms(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of alarms.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartAlarms", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_doors_closed(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of doors closed.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartDoorsClosed", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_cabinet_fan(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of cabinet fan.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartCabinetFan", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_limit_switches(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of limit switches.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartLimitSwitches", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_selectors(self, sensors: dict[str, bool | int]) -> None:
        """Callback to update the sensor of selectors.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool` | `int`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartSelectors", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_emergency_pushbuttons(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of emergency pushbuttons.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartEmergencyPushbuttons", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_power_available(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of power available.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartPowerAvailable", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_hatches(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of hatches.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartHatches", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_photocells(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of photocells.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartPhotocells", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_light_curtain(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of light curtain.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartLightCurtain", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_obc(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of obc.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartOBC", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_axial_fans(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of axial fans.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartAxialFans", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_lights(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of lights.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartLights", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_heating_cables(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of heating cables.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartHeatingCables", sensors)  # type: ignore[arg-type]

    @asyncSlot()
    async def _callback_sensor_brakes(self, sensors: dict[str, bool]) -> None:
        """Callback to update the sensor of brakes.

        Parameters
        ----------
        sensors : `dict` [`str`, `bool`]
            Status of the sensors.
        """

        self.update_sensor_status("sensorsRotatingPartBrakes", sensors)  # type: ignore[arg-type]

    def update_sensor_status(self, group_name: str, sensors: dict[str, bool | float]) -> None:
        """Update the sensor status.

        Parameters
        ----------
        group_name : `str`
            Group name.
        sensors : `dict` [`str`, `bool` | `float`]
            Status of the sensors.
        """

        if group_name == "sensorsRotatingPartSelectors":
            for sensor, value in sensors.items():
                if sensor.endswith("LouverSelected"):
                    louver = "None" if (value == 0) else MTDome.Louver(value).name
                    self._indicators[group_name][sensor].setText(f"{louver}")
                else:
                    self._update_boolean_indicator_status(self._indicators[group_name][sensor], value)  # type: ignore[arg-type]
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
