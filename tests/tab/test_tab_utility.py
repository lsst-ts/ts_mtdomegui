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
from lsst.ts.mtdomegui import Model, TabUtility
from lsst.ts.xml.enums import MTDome
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabUtility:
    widget = TabUtility("Utility", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabUtility) -> None:

    assert len(widget._modes) == len(MTDome.SubSystemId)
    assert len(widget._indicators_capacitor) == 6


@pytest.mark.asyncio
async def test_set_signal_operational_mode(widget: TabUtility) -> None:

    subsystem = MTDome.SubSystemId.MONCS
    mode = MTDome.OperationalMode.DEGRADED
    widget.model.reporter.report_operational_mode(subsystem, mode)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._modes[subsystem.name].text() == mode.name


@pytest.mark.asyncio
async def test_set_signal_telemetry(widget: TabUtility) -> None:

    capacitor_bank = deepcopy(widget.model.reporter.status.capacitor_bank)
    capacitor_bank["doorOpen"][0] = True
    capacitor_bank["dcBusVoltage"] = 1.2345

    widget.model.reporter.report_capacitor_bank(capacitor_bank)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    indicator = widget._indicators_capacitor["doorOpen"][0]
    assert indicator.palette().color(QPalette.Base) == Qt.red

    assert widget._indicators_capacitor["dcBusVoltage"].text() == "1.23 V"
