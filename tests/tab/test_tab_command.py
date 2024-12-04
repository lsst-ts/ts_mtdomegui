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
from lsst.ts.mtdomegui import MAX_POSITION, MAX_TEMPERATURE, MAX_VELOCITY, Model
from lsst.ts.mtdomegui.tab import TabCommand
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabCommand:
    widget = TabCommand("Command", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabCommand) -> None:

    assert len(widget._command_parameters) == 13
    assert len(widget._commands) == 20

    assert widget._command_parameters["position"].maximum() == MAX_POSITION
    assert widget._command_parameters["position"].minimum() == -MAX_POSITION

    assert widget._command_parameters["velocity"].maximum() == MAX_VELOCITY
    assert widget._command_parameters["velocity"].minimum() == -MAX_VELOCITY

    assert widget._command_parameters["temperature"].maximum() == MAX_TEMPERATURE
    assert widget._command_parameters["temperature"].minimum() == -MAX_TEMPERATURE

    assert widget._command_parameters["percentage"].maximum() == 100.0
    assert widget._command_parameters["percentage"].minimum() == -1.0


@pytest.mark.asyncio
async def test_callback_command(qtbot: QtBot, widget: TabCommand) -> None:

    # Single command parameter
    qtbot.mouseClick(widget._commands["home"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._command_parameters["subsystem"].isEnabled() is True
    assert widget._command_parameters["position"].isEnabled() is False
    assert widget._command_parameters["velocity"].isEnabled() is False

    # Two command parameters
    qtbot.mouseClick(widget._commands["move_az"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._command_parameters["subsystem"].isEnabled() is False
    assert widget._command_parameters["position"].isEnabled() is True
    assert widget._command_parameters["velocity"].isEnabled() is True


@pytest.mark.asyncio
async def test_show_selector(qtbot: QtBot, widget: TabCommand) -> None:

    tab_names = ["louver", "drive_az", "drive_shuttor"]
    parameter_names = ["louver", "reset_drives_az", "reset_drives_shutter"]

    for tab_name, parameter_name in zip(tab_names, parameter_names):

        assert widget._tabs[tab_name].isVisible() is False

        qtbot.mouseClick(widget._command_parameters[parameter_name], Qt.LeftButton)

        # Sleep so the event loop can access CPU to handle the signal
        await asyncio.sleep(1)

        assert widget._tabs[tab_name].isVisible() is True
