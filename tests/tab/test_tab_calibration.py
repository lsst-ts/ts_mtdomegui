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
from lsst.ts.mtdomegui import Model, generate_dict_from_registry
from lsst.ts.mtdomegui.tab import TabCalibration
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabCalibration:
    widget = TabCalibration("Calibration", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabCalibration) -> None:

    assert len(widget._status) == 7


@pytest.mark.asyncio
async def test_show_figure(qtbot: QtBot, widget: TabCalibration) -> None:

    assert widget._figures["position"].isVisible() is False

    qtbot.mouseClick(widget._buttons["position"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._figures["position"].isVisible() is True


@pytest.mark.asyncio
async def test_set_signal_telemetry(widget: TabCalibration) -> None:

    widget.model.reporter.report_telemetry(
        "cscs", generate_dict_from_registry(registry, "CSCS", default_number=1.0)
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._status["position_commanded"].text() == "1.00"
    assert widget._status["position_actual"].text() == "1.00"

    assert widget._status["drive_torque_commanded"].text() == "1.00 J"
    assert widget._status["drive_torque_actual"].text() == "1.00 J"
    assert widget._status["drive_current_actual"].text() == "1.00 A"

    assert widget._status["drive_temperature"].text() == "1.00 deg C"

    assert widget._status["power_draw"].text() == "1.00 W"

    for figure in widget._figures.values():
        assert figure._data[0][-1] == 1.0
