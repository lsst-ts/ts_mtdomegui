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
from lsst.ts.mtdomecom import AMCS_NUM_MOTORS
from lsst.ts.mtdomecom.schema import registry
from lsst.ts.mtdomegui import Model, generate_dict_from_registry
from lsst.ts.mtdomegui.tab import TabAzimuth
from lsst.ts.xml.enums import MTDome
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabAzimuth:
    widget = TabAzimuth("Azimuth", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabAzimuth) -> None:

    assert len(widget._status["drive_torque_actual"]) == AMCS_NUM_MOTORS
    assert len(widget._status["drive_temperature"]) == AMCS_NUM_MOTORS


@pytest.mark.asyncio
async def test_show_figure(qtbot: QtBot, widget: TabAzimuth) -> None:

    assert widget._figures["position"].isVisible() is False

    qtbot.mouseClick(widget._buttons["position"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._figures["position"].isVisible() is True


@pytest.mark.asyncio
async def test_set_signal_telemetry(widget: TabAzimuth) -> None:

    widget.model.reporter.report_telemetry(
        "amcs", generate_dict_from_registry(registry, "AMCS", default_number=1.0)
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._status["position_commanded"].text() == "1.00 deg"
    assert widget._status["position_actual"].text() == "1.00 deg"

    assert widget._status["velocity_commanded"].text() == "1.00 deg/sec"
    assert widget._status["velocity_actual"].text() == "1.00 deg/sec"

    assert widget._status["drive_torque_commanded"][0].text() == "1.00 N*m"
    assert widget._status["drive_torque_actual"][0].text() == "1.00 N*m"
    assert widget._status["drive_current_actual"][0].text() == "1.00 A"

    assert widget._status["drive_temperature"][0].text() == "1.00 deg C"

    for figure in widget._figures.values():
        assert figure._data[0][-1] == 1.0


@pytest.mark.asyncio
async def test_set_signal_target(widget: TabAzimuth) -> None:

    widget.model.reporter.report_target_azimuth(1.0, 2.0)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._states["target_position"].text() == "1.00 deg"
    assert widget._states["target_velocity"].text() == "2.00 deg/sec"


@pytest.mark.asyncio
async def test_set_signal_state(widget: TabAzimuth) -> None:

    widget.model.reporter.report_state_azimuth_axis(MTDome.EnabledState.ENABLED)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._states["state"].text() == MTDome.EnabledState.ENABLED.name


@pytest.mark.asyncio
async def test_set_signal_motion(widget: TabAzimuth) -> None:

    widget.model.reporter.report_motion_azimuth_axis(MTDome.MotionState.MOVING, True)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._states["motion"].text() == MTDome.MotionState.MOVING.name
    assert widget._states["in_position"].text() == str(True)


@pytest.mark.asyncio
async def test_set_signal_fault_code(widget: TabAzimuth) -> None:

    widget.model.reporter.report_fault_code_azimuth_axis("Error")

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._window_fault_code.toPlainText() == "Error"
