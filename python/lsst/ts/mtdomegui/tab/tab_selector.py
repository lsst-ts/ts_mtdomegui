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

__all__ = ["TabSelector"]

from lsst.ts.guitool import (
    TabTemplate,
    create_grid_layout_buttons,
    create_group_box,
    set_button,
)
from PySide6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout
from qasync import asyncSlot

from ..model import Model


class TabSelector(TabTemplate):
    """Table of the selector.

    Parameters
    ----------
    title : `str`
        Table's title.
    model : `Model`
        Model class.
    names : `list` [`str`]
        Names of the selections.

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    def __init__(self, title: str, model: Model, names: list[str]) -> None:
        super().__init__(title)

        self.model = model

        self._buttons = self._create_buttons(names)

        self.set_widget_and_layout()

    def _create_buttons(self, names: list[str]) -> dict[str, QPushButton]:
        """Create the buttons.

        Parameters
        ----------
        names : `list` [`str`]
            Names of the selections.

        Returns
        -------
        `dict`
            Buttons.
        """

        buttons_selection = self._create_buttons_selection(names)

        button_select_all = set_button(
            "Select All",
            self._callback_select_all,
        )
        button_reset_all = set_button(
            "Reset All",
            self._callback_reset_all,
        )

        return {
            "selection": buttons_selection,
            "select_all": button_select_all,
            "reset_all": button_reset_all,
        }

    def _create_buttons_selection(self, names: list[str]) -> list[QPushButton]:
        """Creates the selection buttons.

        Parameters
        ----------
        names : `list` [`str`]
            Names of the selections.

        Returns
        -------
        buttons : `list`
            Selection buttons.
        """

        buttons = list()

        for idx, name in enumerate(names):
            button = set_button(
                name,
                None,
                is_checkable=True,
                is_adjust_size=True,
            )

            buttons.append(button)

        return buttons

    @asyncSlot()
    async def _callback_select_all(self) -> None:
        """Callback of the select-all button to select all the items."""

        self.select(list(range(len(self._buttons["selection"]))))

    def select(self, selections: list[int]) -> None:
        """Select the items.

        Parameters
        ----------
        selections : `list` [`int`]
            Selections.
        """

        for idx, button in enumerate(self._buttons["selection"]):
            if button.isEnabled():
                button.setChecked(idx in selections)

    @asyncSlot()
    async def _callback_reset_all(self) -> None:
        """Callback of the reset-all button to rest all the items."""

        self.select([])

    def create_layout(self) -> QVBoxLayout:

        layout = QVBoxLayout()
        layout.addWidget(self._create_group_selection())
        layout.addWidget(self._buttons["select_all"])
        layout.addWidget(self._buttons["reset_all"])

        return layout

    def _create_group_selection(self, num_column: int = 5) -> QGroupBox:
        """Create the group of selection.

        Parameters
        ----------
        num_column : `int`, optional
            Number of column on the grid layput. (the default is 5)

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = create_grid_layout_buttons(self._buttons["selection"], num_column)
        return create_group_box(self.windowTitle(), layout)

    def get_selection(self) -> list[int]:
        """Get the selection.

        Returns
        -------
        selection : `list` [`int`]
            Selected items.
        """

        selection = list()
        for idx, button in enumerate(self._buttons["selection"]):
            if button.isChecked():
                selection.append(idx)

        return selection

    def set_selection_enabled(self, index: int, is_enabled: bool) -> None:
        """Set the selection to be enabled or disabled.

        Parameters
        ----------
        index : `int`
            Index of the selection.
        is_enabled : `bool`
            Is enabled or disabled.
        """

        self._buttons["selection"][index].setEnabled(is_enabled)
