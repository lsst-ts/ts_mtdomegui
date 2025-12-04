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

__all__ = ["TabBrake"]

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout

from lsst.ts.guitool import (
    ButtonStatus,
    TabTemplate,
    create_grid_layout_buttons,
    create_group_box,
    create_label,
    set_button,
    update_button_color,
)

# TODO: OSW-1538, use MTDome.Brake after the ts_xml: 24.4.
from lsst.ts.mtdomecom import Brake

from ..model import Model


class TabBrake(TabTemplate):
    """Table of the engaged brakes.

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

        self._indicators_brake = self._create_indicators_brake()

        self.set_widget_and_layout()

    def _create_indicators_brake(self) -> list[QPushButton]:
        """Creates the brake indicators.

        Returns
        -------
        indicators : `list`
            Brake indicators.
        """

        indicators = list()

        for idx, specific_brake in enumerate(Brake):
            indicator = set_button(
                f"{specific_brake.name} ({idx})", None, is_indicator=True, is_adjust_size=True
            )

            self._update_indicator_color(indicator, False)

            indicators.append(indicator)

        return indicators

    def _update_indicator_color(self, indicator: QPushButton, is_engaged: bool) -> None:
        """Update the indicator color.

        Parameters
        ----------
        indicator : `PySide6.QtWidgets.QPushButton`
            Indicator.
        is_engaged : `bool`
            Is engaged or not.
        """

        button_status = ButtonStatus.Warn if is_engaged else ButtonStatus.Normal
        update_button_color(indicator, QPalette.Button, button_status)

    def create_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(
            create_label(
                "If the brake is engaged, the indicator will be shown in yellow."
                " Otherwise, it will be shown in green."
            )
        )
        layout.addWidget(self._create_group_brake())

        return layout

    def _create_group_brake(self) -> QGroupBox:
        """Create the group of brake.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        num_column = len(Brake) // 10
        layout = create_grid_layout_buttons(self._indicators_brake, num_column)

        return create_group_box("Brake Status", layout)

    def update_brake_status(self, index: int, is_engaged: bool) -> None:
        """ "Update the brake status.

        Parameters
        ----------
        index : `int`
            Index of the brake.
        is_engaged : `bool`
            Is engaged or not.
        """

        self._update_indicator_color(self._indicators_brake[index], is_engaged)
