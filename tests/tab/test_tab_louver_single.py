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
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from lsst.ts.mtdomegui import Model
from lsst.ts.mtdomegui.tab import TabLouverSingle


@pytest.fixture
def widget(qtbot: QtBot) -> TabLouverSingle:
    widget = TabLouverSingle("LouverSingle", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabLouverSingle) -> None:
    assert len(widget._states) == 2
    assert len(widget._status) == 6
    assert len(widget._figures) == len(widget._buttons)


@pytest.mark.asyncio
async def test_show_figure(qtbot: QtBot, widget: TabLouverSingle) -> None:
    name = "position"

    assert widget._figures[name].windowTitle() == "LouverSingle Position"
    assert widget._figures[name].isVisible() is False

    qtbot.mouseClick(widget._buttons[name], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._figures[name].isVisible() is True
