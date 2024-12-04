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

__all__ = [
    "combine_indicators",
    "update_boolean_indicator_status",
    "add_empty_row_to_form_layout",
]

from lsst.ts.guitool import ButtonStatus, TabTemplate, set_button, update_button_color
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QPushButton, QRadioButton


def combine_indicators(indicators: list[QRadioButton]) -> QHBoxLayout:
    """Combine the indicators.

    Parameters
    ----------
    indicators : `list` [`QRadioButton`]
        Indicators.

    Returns
    -------
    combined_indicators : `QHBoxLayout`
        Combined indicators.
    """

    combined_indicators = QHBoxLayout()

    for indicator in indicators:
        combined_indicators.addWidget(indicator)

    return combined_indicators


def update_boolean_indicator_status(indicator: QRadioButton, is_fault: bool) -> None:
    """Update the boolean indicator status.

    Parameters
    ----------
    indicator : `QRadioButton`
        Indicator.
    is_fault : `bool`
        Is fault or not.
    """

    status = ButtonStatus.Error if is_fault else ButtonStatus.Normal
    update_button_color(indicator, QPalette.Base, status)


def add_empty_row_to_form_layout(layout: QFormLayout) -> None:
    """Add the empty row to the form layout.

    Parameters
    ----------
    layout : `PySide6.QtWidgets.QFormLayout`
        Layout.
    """
    layout.addRow(" ", None)


def create_buttons_with_tabs(
    names: list[str],
    tabs: dict[str, TabTemplate],
    tool_tip: str = "Click to open the real-time chart.",
) -> dict[str, QPushButton]:
    """Create the buttons that connect with the tabs. When the button
    is clicked, the tab will be shown.

    Parameters
    ----------
    names : `list` [`str`]
        Names of the buttons.
    tabs : `dict`
        Tabs. The key is the name of the tab. It should be the lower
        case of the name of the button with the replacement of space by
        "_". For example, if a button's name is "Drive Torque", the key of
        the tab needs to be "drive_torque".
    tool_tip : `str` or None, optional
        Tool tip. If None, there will be no tip. (the default is "Click to open
        the real-time chart.")

    Returns
    -------
    buttons : `dict`
        Buttons with the same keys as the tabs.
    """

    buttons = dict()
    for name in names:
        tab_name = name.replace(" ", "_").lower()
        buttons[tab_name] = set_button(
            name,
            tabs[tab_name].show,
            tool_tip=tool_tip,
        )

    return buttons
