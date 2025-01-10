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
    NUM_DRIVE_ELEVATION,
    NUM_TEMPERATURE_ELEVATION,
    Model,
    generate_dict_from_registry,
)
from lsst.ts.mtdomegui.tab import TabElevation
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabElevation:
    widget = TabElevation("Elevation", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabElevation) -> None:

    assert len(widget._status["drive_torque_actual"]) == NUM_DRIVE_ELEVATION
    assert len(widget._status["drive_temperature"]) == NUM_TEMPERATURE_ELEVATION


@pytest.mark.asyncio
async def test_show_figure(qtbot: QtBot, widget: TabElevation) -> None:

    assert widget._figures["position"].isVisible() is False

    qtbot.mouseClick(widget._buttons["position"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._figures["position"].isVisible() is True


@pytest.mark.asyncio
async def test_set_signal_telemetry(widget: TabElevation) -> None:

    widget.model.report_telemetry(
        "lwscs", generate_dict_from_registry(registry, "LWSCS", default_number=1.0)
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._status["position_commanded"].text() == "1.00 deg"
    assert widget._status["position_actual"].text() == "1.00 deg"

    assert widget._status["velocity_commanded"].text() == "1.00 deg/sec"
    assert widget._status["velocity_actual"].text() == "1.00 deg/sec"

    assert widget._status["drive_torque_commanded"][0].text() == "1.00 J"
    assert widget._status["drive_torque_actual"][0].text() == "1.00 J"
    assert widget._status["drive_current_actual"][0].text() == "1.00 A"

    assert widget._status["drive_temperature"][0].text() == "1.00 deg C"

    assert widget._status["power_draw"].text() == "1.00 W"

    for figure in widget._figures.values():
        assert figure._data[0][-1] == 1.0
