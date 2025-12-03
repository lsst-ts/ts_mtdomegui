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
import math

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from lsst.ts.mtdomecom import (
    AMCS_NUM_MOTORS,
    LCS_NUM_LOUVERS,
    LCS_NUM_MOTORS_PER_LOUVER,
    LWSCS_VMAX,
)
from lsst.ts.mtdomegui import MAX_POSITION, MAX_TEMPERATURE, NUM_DRIVE_SHUTTER, Model
from lsst.ts.mtdomegui.tab import TabCommand
from lsst.ts.xml.enums import MTDome


@pytest.fixture
def widget(qtbot: QtBot) -> TabCommand:
    model = Model(logging.getLogger())
    model.louvers_enabled = [MTDome.Louver.E1]

    widget = TabCommand("Command", model)
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabCommand) -> None:
    assert len(widget._command_parameters) == 14
    assert len(widget._commands) == 21

    assert widget._command_parameters["position"].maximum() == MAX_POSITION
    assert widget._command_parameters["position"].minimum() == -MAX_POSITION

    assert widget._command_parameters["velocity"].maximum() == math.degrees(LWSCS_VMAX)
    assert widget._command_parameters["velocity"].minimum() == -math.degrees(LWSCS_VMAX)

    assert widget._command_parameters["temperature"].maximum() == MAX_TEMPERATURE
    assert widget._command_parameters["temperature"].minimum() == -MAX_TEMPERATURE

    assert widget._command_parameters["percentage"].maximum() == 100.0


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


def test_get_selected_command(widget: TabCommand) -> None:
    for name, command in widget._commands.items():
        command.setChecked(True)

        assert widget._get_selected_command() == name


def test_get_louver_percentages(widget: TabCommand) -> None:
    # No selected louver
    assert widget._get_louver_percentages() == [-1.0] * len(MTDome.Louver)

    # There are selected louvers
    widget._command_parameters["percentage"].setValue(50.0)

    selections = [louver.value - 1 for louver in widget.model.louvers_enabled]
    widget._tabs["louver"].select(selections)

    for idx, value in enumerate(widget._get_louver_percentages()):
        if idx in selections:
            assert value == 50.0
        else:
            assert value == -1.0


def test_get_subsystem_bitmask(widget: TabCommand) -> None:
    assert widget._get_subsystem_bitmask() == MTDome.SubSystemId.AMCS.value

    widget._command_parameters["subsystem"].setCurrentIndex(3)

    assert widget._get_subsystem_bitmask() == MTDome.SubSystemId.LCS.value


def test_get_direction(widget: TabCommand) -> None:
    combo_box = widget._command_parameters["direction"]

    assert widget._get_direction(combo_box) == MTDome.OpenClose.OPEN

    combo_box.setCurrentIndex(1)
    assert widget._get_direction(combo_box) == MTDome.OpenClose.CLOSE


def test_get_on_off(widget: TabCommand) -> None:
    combo_box = widget._command_parameters["engage_brakes"]

    assert widget._get_on_off(combo_box) is None

    for idx, value in zip([1, 2], [MTDome.OnOff.ON, MTDome.OnOff.OFF]):
        combo_box.setCurrentIndex(idx)
        assert widget._get_on_off(combo_box) == value


def test_get_operational_mode(widget: TabCommand) -> None:
    combo_box = widget._command_parameters["operation_mode"]

    for idx, mode in enumerate(MTDome.OperationalMode):
        combo_box.setCurrentIndex(mode.value - 1)
        assert widget._get_operational_mode() == mode


def test_get_reset_drives_azimuth(widget: TabCommand) -> None:
    # No selected drives
    assert widget._get_reset_drives_azimuth() == [0] * AMCS_NUM_MOTORS

    # Has selected drives
    selections = [1, 2]
    widget._tabs["drive_az"].select(selections)

    assert widget._get_reset_drives_azimuth() == [0, 1, 1, 0, 0]


def test_get_reset_drives_aperture_shutter(widget: TabCommand) -> None:
    # No selected drives
    assert widget._get_reset_drives_aperture_shutter() == [0] * NUM_DRIVE_SHUTTER

    # Has selected drives
    selections = [1, 2]
    widget._tabs["drive_shuttor"].select(selections)

    assert widget._get_reset_drives_aperture_shutter() == [0, 1, 1, 0]


def test_get_reset_drives_louver(widget: TabCommand) -> None:
    # Set all the louvers to be enabled first
    for idx in range(LCS_NUM_LOUVERS):
        widget._tabs["louver"].set_selection_enabled(idx, True)

    # No selected drives
    assert widget._get_reset_drives_louver() == [0] * LCS_NUM_MOTORS_PER_LOUVER * LCS_NUM_LOUVERS

    # Has selected drives
    selections = [0, 1, 33]
    widget._tabs["louver"].select(selections)

    assert widget._get_reset_drives_louver()[0:6] == [1, 1, 1, 1, 0, 0]
    assert widget._get_reset_drives_louver()[-4:] == [0, 0, 1, 1]


def test_get_power_mode(widget: TabCommand) -> None:
    combo_box = widget._command_parameters["power_mode"]

    for idx, mode in enumerate(MTDome.PowerManagementMode):
        combo_box.setCurrentIndex(mode.value - 1)
        assert widget._get_power_mode() == mode
