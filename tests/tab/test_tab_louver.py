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
from lsst.ts.mtdomecom import LCS_NUM_LOUVERS, LOUVERS_ENABLED
from lsst.ts.mtdomecom.schema import registry
from lsst.ts.mtdomegui import Model, generate_dict_from_registry
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

    idx = LOUVERS_ENABLED[0].value - 1

    assert widget._tabs[idx].isVisible() is False

    qtbot.mouseClick(widget._buttons["louver"][idx], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._tabs[idx].isVisible() is True


@pytest.mark.asyncio
async def test_set_signal_telemetry(widget: TabLouver) -> None:

    widget.model.reporter.report_telemetry(
        "lcs", generate_dict_from_registry(registry, "LCS", default_number=1.0)
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._power.text() == "1.00 W"
    assert widget._figure._data[0][-1] == 1.0

    for louver in widget._tabs:
        assert louver._status["position_commanded"].text() == "1.00 %"
        assert louver._status["position_actual"].text() == "1.00 %"

        assert louver._status["drive_torque_commanded"][0].text() == "1.00 N*m"
        assert louver._status["drive_torque_actual"][0].text() == "1.00 N*m"
        assert louver._status["drive_current_actual"][0].text() == "1.00 A"

        assert louver._status["drive_temperature"][0].text() == "1.00 deg C"

        for figure in louver._figures.values():
            assert figure._data[0][-1] == 1.0


@pytest.mark.asyncio
async def test_set_signal_state(widget: TabLouver) -> None:

    widget.model.reporter.report_state_louvers(MTDome.EnabledState.ENABLED)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._state.text() == MTDome.EnabledState.ENABLED.name


@pytest.mark.asyncio
async def test_set_signal_motion(widget: TabLouver) -> None:

    widget.model.reporter.report_motion_louvers(
        [MTDome.MotionState.MOVING] * LCS_NUM_LOUVERS,
        [True] * LCS_NUM_LOUVERS,
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for tab_louver in widget._tabs:
        assert tab_louver._states["motion"].text() == MTDome.MotionState.MOVING.name
        assert tab_louver._states["in_position"].text() == str(True)


@pytest.mark.asyncio
async def test_set_signal_fault_code(widget: TabLouver) -> None:

    widget.model.reporter.report_fault_code_louvers("Error")

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._window_fault_code.toPlainText() == "Error"
