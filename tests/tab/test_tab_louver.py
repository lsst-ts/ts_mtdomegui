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
from lsst.ts.mtdomegui import Model
from lsst.ts.mtdomegui.tab import TabLouver
from lsst.ts.xml.enums import MTDome
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabLouver:
    widget = TabLouver("Louver", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabLouver) -> None:

    assert len(widget._buttons["louver"]) == len(MTDome.Louver)
    assert len(widget._tabs) == len(MTDome.Louver)


@pytest.mark.asyncio
async def test_show_figure(qtbot: QtBot, widget: TabLouver) -> None:

    assert widget._figure.isVisible() is False

    qtbot.mouseClick(widget._buttons["power"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._figure.isVisible() is True


@pytest.mark.asyncio
async def test_show_louver(qtbot: QtBot, widget: TabLouver) -> None:

    assert widget._tabs[0].isVisible() is False

    qtbot.mouseClick(widget._buttons["louver"][0], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._tabs[0].isVisible() is True
