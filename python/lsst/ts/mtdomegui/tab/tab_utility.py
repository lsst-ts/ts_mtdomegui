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
from lsst.ts.xml.enums import MTDome
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QRadioButton, QVBoxLayout

from ..constants import SUBSYSTEMS
from ..model import Model
from ..utils import combine_indicators, update_boolean_indicator_status


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

        self.set_widget_and_layout()

        self._set_default()

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

    def _create_indicators(self) -> dict[str, list[QRadioButton]]:
        """Create the indicators of the capacitors.

        Returns
        -------
        `dict`
            Dictionary of the indicators of the capacitors.
        """

        return {
            "fuse": create_radio_indicators(2),
            "smoke": create_radio_indicators(2),
            "temperature": create_radio_indicators(2),
            "voltage": create_radio_indicators(2),
            "door": create_radio_indicators(2),
        }

    def create_layout(self) -> QVBoxLayout:

        layout = QVBoxLayout()
        layout.addWidget(self._create_group_mode())
        layout.addWidget(self._create_group_capacitor())

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

        names = [
            "Fuse intervention",
            "Smoke detected",
            "High temperature",
            "Low residual voltage",
            "Door open",
        ]

        layout = QFormLayout()
        for name, indicators in zip(names, self._indicators_capacitor.values()):
            layout.addRow(f"{name}:", combine_indicators(indicators))

        return create_group_box("Capacitor Banks", layout)

    def _set_default(self) -> None:
        """Set the default values."""

        for mode in self._modes.values():
            mode.setText(MTDome.OperationalMode.NORMAL.name)

        for indicators in self._indicators_capacitor.values():
            for indicator in indicators:
                update_boolean_indicator_status(indicator, False)
