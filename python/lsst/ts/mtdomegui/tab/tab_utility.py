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

__all__ = ["TabUtility"]

from lsst.ts.guitool import (
    TabTemplate,
    create_group_box,
    create_label,
    create_radio_indicators,
)
from lsst.ts.mtdomecom import CBCS_NUM_CAPACITOR_BANKS
from lsst.ts.xml.enums import MTDome
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QRadioButton, QVBoxLayout
from qasync import asyncSlot

from ..constants import SUBSYSTEMS
from ..model import Model
from ..signals import SignalOperationalMode, SignalTelemetry
from ..utils import (
    combine_indicators,
    create_buttons_with_tabs,
    update_boolean_indicator_status,
)
from .tab_figure import TabFigure


class TabUtility(TabTemplate):
    """Table of the utility.

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

        self._modes = self._create_modes()
        self._indicators_capacitor = self._create_indicators()

        self._figures = {"voltage": TabFigure("Voltage", self.model, "V", ["voltage"])}
        self._buttons = create_buttons_with_tabs(["Voltage"], self._figures)

        self.set_widget_and_layout()

        signals = self.model.reporter.signals
        self._set_signal_operational_mode(signals["operational_mode"])  # type: ignore[arg-type]
        self._set_signal_telemetry(signals["telemetry"])  # type: ignore[arg-type]

    def _create_modes(self) -> dict[str, QLabel]:
        """Create the operational modes of sub-systems.

        Returns
        -------
        `dict`
            Dictionary of the operational modes of sub-systems.
        """

        modes = dict()
        for system in MTDome.SubSystemId:
            modes[system.name] = create_label()

        return modes

    def _create_indicators(self) -> dict[str, list[QRadioButton] | QLabel]:
        """Create the indicators of the capacitors.

        Returns
        -------
        indicators : `dict`
            Dictionary of the indicators of the capacitors.
        """

        indicators = dict()
        for name in self.model.reporter.status.capacitor_bank.keys():
            indicators[name] = create_radio_indicators(CBCS_NUM_CAPACITOR_BANKS)

        indicators["dcBusVoltage"] = create_label()

        return indicators

    def create_layout(self) -> QVBoxLayout:

        layout = QVBoxLayout()
        layout.addWidget(self._create_group_mode())
        layout.addWidget(self._create_group_capacitor())
        layout.addWidget(self._create_group_realtime_chart())

        return layout

    def _create_group_mode(self) -> QGroupBox:
        """Create the group of operational mode.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        for sub_system, sub_system_id in zip(SUBSYSTEMS, MTDome.SubSystemId):
            layout.addRow(f"{sub_system}:", self._modes[sub_system_id.name])

        return create_group_box("Operational Mode", layout)

    def _create_group_capacitor(self) -> QGroupBox:
        """Create the group of capacitor.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("DC bus voltage:", self._indicators_capacitor["dcBusVoltage"])

        names = [
            "Fuse intervention",
            "Smoke detected",
            "High temperature",
            "Low residual voltage",
            "Door open",
        ]
        for name, indicators in zip(names, self._indicators_capacitor.values()):
            layout.addRow(f"{name}:", combine_indicators(indicators))

        return create_group_box("Capacitor Banks", layout)

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

    def _set_signal_operational_mode(self, signal: SignalOperationalMode) -> None:
        """Set the operational mode signal.

        Parameters
        ----------
        signal : `SignalOperationalMode`
            Signal.
        """

        signal.subsystem_mode.connect(self._callback_subsystem_mode)

    @asyncSlot()
    async def _callback_subsystem_mode(
        self, subsystem_mode: tuple[MTDome.SubSystemId, MTDome.OperationalMode]
    ) -> None:
        """Callback of the subsystem's operational mode.

        Parameters
        ----------
        subsystem_mode : `tuple`
            Subsystem's operational mode.
        """

        self._modes[subsystem_mode[0].name].setText(subsystem_mode[1].name)

    def _set_signal_telemetry(self, signal: SignalTelemetry) -> None:
        """Set the telemetry signal.

        Parameters
        ----------
        signal : `SignalTelemetry`
            Signal.
        """

        signal.cbcs.connect(self._callback_status_cbcs)
        signal.cbcs_voltage.connect(self._callback_status_cbcs_voltage)

    @asyncSlot()
    async def _callback_status_cbcs(self, cbcs: dict[str, list[bool]]) -> None:
        """Callback of the status of capacitor bank control system (CBCS).

        Parameters
        ----------
        cbcs : `dict`
            CBCS status.
        """

        for key, values in cbcs.items():
            indicators = self._indicators_capacitor[key]
            for indicator, value in zip(indicators, values):
                update_boolean_indicator_status(indicator, value)

    @asyncSlot()
    async def _callback_status_cbcs_voltage(self, voltage: float) -> None:
        """Callback of the capacitor bank voltage.

        Parameters
        ----------
        voltage : `float`
            Voltage of the capacitor bank.
        """

        self._indicators_capacitor["dcBusVoltage"].setText(f"{voltage:.2f} V")  # type: ignore[union-attr]
        self._figures["voltage"].append_data([voltage])
