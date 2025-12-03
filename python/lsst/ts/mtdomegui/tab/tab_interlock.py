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

__all__ = ["TabInterlock"]

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout

from lsst.ts.guitool import (
    ButtonStatus,
    TabTemplate,
    create_grid_layout_buttons,
    create_group_box,
    set_button,
    update_button_color,
)
from lsst.ts.mtdomecom import MON_NUM_SENSORS

from ..model import Model


class TabInterlock(TabTemplate):
    """Table of the interlock.

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

        self._indicators_interlock = self._create_indicators_interlock(MON_NUM_SENSORS)

        self.set_widget_and_layout()

    def _create_indicators_interlock(self, number: int) -> list[QPushButton]:
        """Creates the interlock indicators.

        Parameters
        ----------
        number : `int`
            Total number of interlock.

        Returns
        -------
        indicators : `list`
            Interlock indicators.
        """

        indicators = list()

        for specific_id in range(number):
            indicator = set_button(str(specific_id), None, is_indicator=True, is_adjust_size=True)

            self._update_indicator_color(indicator, False)

            indicators.append(indicator)

        return indicators

    def _update_indicator_color(self, indicator: QPushButton, is_triggered: bool) -> None:
        """Update the indicator color.

        Parameters
        ----------
        indicator : `PySide6.QtWidgets.QPushButton`
            Indicator.
        is_triggered : `bool`
            Is triggered or not.
        """

        button_status = ButtonStatus.Error if is_triggered else ButtonStatus.Normal
        update_button_color(indicator, QPalette.Button, button_status)

    def create_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(self._create_group_interlock())

        return layout

    def _create_group_interlock(self) -> QGroupBox:
        """Create the group of interlock.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        num_column = MON_NUM_SENSORS // 4
        layout = create_grid_layout_buttons(self._indicators_interlock, num_column)

        return create_group_box("Interlock Status", layout)

    def update_interlock_status(self, index: int, is_triggered: bool) -> None:
        """ "Update the interlock status.

        Parameters
        ----------
        index : `int`
            Index of the interlock.
        is_triggered : `bool`
            Is triggered or not.
        """

        self._update_indicator_color(self._indicators_interlock[index], is_triggered)
