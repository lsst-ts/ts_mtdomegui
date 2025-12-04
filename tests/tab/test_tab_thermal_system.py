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

from lsst.ts.mtdomecom import (
    THCS_NUM_CABINET_TEMPERATURES,
    THCS_NUM_MOTOR_COIL_TEMPERATURES,
    THCS_NUM_MOTOR_DRIVE_TEMPERATURES,
)
from lsst.ts.mtdomecom.schema import registry
from lsst.ts.mtdomegui import Model, generate_dict_from_registry
from lsst.ts.mtdomegui.tab import TabThermalSystem


@pytest.fixture
def widget(qtbot: QtBot) -> TabThermalSystem:
    widget = TabThermalSystem("Thermal System", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabThermalSystem) -> None:
    num_motor_sensors = THCS_NUM_MOTOR_COIL_TEMPERATURES + THCS_NUM_MOTOR_DRIVE_TEMPERATURES
    assert len(widget._sensors["motor"]) == num_motor_sensors
    assert len(widget._sensors["cabinet"]) == THCS_NUM_CABINET_TEMPERATURES
    assert len(widget._tab_selector._buttons["selection"]) == num_motor_sensors

    for button in widget._tab_selector._buttons["selection"]:
        assert button.isChecked() is True


@pytest.mark.asyncio
async def test_show_selector(qtbot: QtBot, widget: TabThermalSystem) -> None:
    assert widget._tab_selector.isVisible() is False

    qtbot.mouseClick(widget._buttons["selector"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._tab_selector.isVisible() is True


@pytest.mark.asyncio
async def test_show_figure(qtbot: QtBot, widget: TabThermalSystem) -> None:
    assert widget._figures["cabinet"].isVisible() is False

    qtbot.mouseClick(widget._buttons["cabinet"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._figures["cabinet"].isVisible() is True


@pytest.mark.asyncio
async def test_callback_update(qtbot: QtBot, widget: TabThermalSystem) -> None:
    assert len(widget._figures["motor"].chart().series()) == (
        THCS_NUM_MOTOR_COIL_TEMPERATURES + THCS_NUM_MOTOR_DRIVE_TEMPERATURES
    )

    # New selections
    selections = [0, 3]
    widget._temperatures["motor"][0] = 0.1
    widget._temperatures["motor"][3] = 2.4
    widget._tab_selector.select(selections)

    qtbot.mouseClick(widget._buttons["update"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    await widget._callback_time_out()

    assert widget._selections == selections
    assert len(widget._figures["motor"].chart().series()) == len(selections)

    assert widget._figures["motor"].get_points(0)[-1].y() == 0.1
    assert widget._figures["motor"].get_points(1)[-1].y() == 2.4


@pytest.mark.asyncio
async def test_set_signal_telemetry(widget: TabThermalSystem) -> None:
    widget.model.reporter.report_telemetry(
        "thcs", generate_dict_from_registry(registry, "ThCS", default_number=1.0)
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._temperatures["motor"] == [1.0] * (
        THCS_NUM_MOTOR_DRIVE_TEMPERATURES + THCS_NUM_MOTOR_COIL_TEMPERATURES
    )
    assert widget._temperatures["cabinet"] == [1.0] * THCS_NUM_CABINET_TEMPERATURES

    for index, senser in enumerate(widget._sensors["motor"]):
        assert senser.text() == "1.00 deg C"

    for senser in widget._sensors["cabinet"]:
        assert senser.text() == "1.00 deg C"
