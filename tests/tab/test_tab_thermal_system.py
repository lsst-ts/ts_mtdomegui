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
from lsst.ts.mtdomecom.schema import registry
from lsst.ts.mtdomegui import (
    NUM_TEMPERATURE_THERMAL,
    Model,
    generate_dict_from_registry,
)
from lsst.ts.mtdomegui.tab import TabThermalSystem
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabThermalSystem:
    widget = TabThermalSystem("Thermal System", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabThermalSystem) -> None:

    assert len(widget._sensors) == NUM_TEMPERATURE_THERMAL

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
async def test_callback_update(qtbot: QtBot, widget: TabThermalSystem) -> None:

    assert len(widget._figure.chart().series()) == NUM_TEMPERATURE_THERMAL

    # New selections
    selections = [0, 3]
    widget._temperatures[0] = 0.1
    widget._temperatures[3] = 2.4
    widget._tab_selector.select(selections)

    qtbot.mouseClick(widget._buttons["update"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    await widget._callback_time_out()

    assert widget._selections == selections
    assert len(widget._figure.chart().series()) == len(selections)

    assert widget._figure.get_points(0)[-1].y() == 0.1
    assert widget._figure.get_points(1)[-1].y() == 2.4


@pytest.mark.asyncio
async def test_set_signal_telemetry(widget: TabThermalSystem) -> None:

    widget.model.reporter.report_telemetry(
        "thcs", generate_dict_from_registry(registry, "ThCS", default_number=1.0)
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._temperatures[0] == 1.00

    for senser in widget._sensors:
        assert senser.text() == "1.00 deg C"
