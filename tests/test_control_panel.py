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

import asyncio
import logging

import pytest
from lsst.ts.mtdomegui import ControlPanel, Model
from lsst.ts.xml.enums import MTDome
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> ControlPanel:
    widget = ControlPanel(Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: ControlPanel) -> None:

    assert len(widget._labels) == 7


@pytest.mark.asyncio
async def test_show_interlock(qtbot: QtBot, widget: ControlPanel) -> None:

    assert widget._tab_interlock.isVisible() is False

    qtbot.mouseClick(widget._button_interlock, Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._tab_interlock.isVisible() is True


def test_update_button_interlock(widget: ControlPanel) -> None:

    widget._update_button_interlock(False)

    assert widget._button_interlock.text() == MTDome.OnOff.OFF.name
    assert widget._button_interlock.palette().color(QPalette.Button) == Qt.green

    widget._update_button_interlock(True)

    assert widget._button_interlock.text() == MTDome.OnOff.ON.name
    assert widget._button_interlock.palette().color(QPalette.Button) == Qt.red
