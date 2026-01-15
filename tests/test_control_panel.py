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
from copy import deepcopy

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot

# TODO: OSW-1538, remove the ControlMode after the ts_xml: 24.4.
from lsst.ts.mtdomecom import ControlMode
from lsst.ts.mtdomegui import ControlPanel, Model
from lsst.ts.xml.enums import MTDome


@pytest.fixture
def widget(qtbot: QtBot) -> ControlPanel:
    widget = ControlPanel(Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: ControlPanel) -> None:
    assert len(widget._labels) == 9


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


@pytest.mark.asyncio
async def test_set_signal_interlock(widget: ControlPanel) -> None:
    # Interlocks
    interlocks = deepcopy(widget.model.reporter.status.interlocks)
    interlocks[0] = True

    widget.model.reporter.report_interlocks(interlocks)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    widget._tab_interlock._indicators_interlock[0].palette().color(QPalette.Button) == Qt.red
    widget._button_interlock.palette().color(QPalette.Button) == Qt.red

    # Locking pins
    widget.model.reporter.report_state_locking_pins_engaged(1)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._labels["locking_pin"].text() == hex(1)


@pytest.mark.asyncio
async def test_set_signal_state(widget: ControlPanel) -> None:
    widget.model.reporter.report_state_azimuth_axis(MTDome.EnabledState.ENABLED)
    widget.model.reporter.report_state_elevation_axis(MTDome.EnabledState.ENABLED)
    widget.model.reporter.report_state_aperture_shutter(MTDome.EnabledState.ENABLED)
    widget.model.reporter.report_state_louvers(MTDome.EnabledState.ENABLED)
    widget.model.reporter.report_state_rear_access_door(MTDome.EnabledState.ENABLED)
    widget.model.reporter.report_state_calibration_screen(MTDome.EnabledState.ENABLED)
    widget.model.reporter.report_state_power_mode(MTDome.PowerManagementMode.EMERGENCY)
    widget.model.reporter.report_state_control_mode(ControlMode.local_keba)

    # 30 = 2 + 4 + 8 + 16 (first four brakes are engaged)
    widget.model.reporter.report_state_brake_engaged(30)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._labels["azimuth_axis"].text() == MTDome.EnabledState.ENABLED.name
    assert widget._labels["elevation_axis"].text() == MTDome.EnabledState.ENABLED.name
    assert widget._labels["aperture_shutter"].text() == MTDome.EnabledState.ENABLED.name
    assert widget._labels["louvers"].text() == MTDome.EnabledState.ENABLED.name
    assert widget._labels["rear_access_door"].text() == MTDome.EnabledState.ENABLED.name
    assert widget._labels["calibration_screen"].text() == MTDome.EnabledState.ENABLED.name
    assert widget._labels["power_mode"].text() == MTDome.PowerManagementMode.EMERGENCY.name
    assert widget._labels["control_mode"].text() == ControlMode.local_keba.name

    assert widget._button_brake_engaged.text() == "0x1e"

    for idx in range(5):
        widget._tab_brake._indicators_brake[idx].palette().color(QPalette.Button) == Qt.yellow

    widget._tab_brake._indicators_brake[5].palette().color(QPalette.Button) == Qt.green
