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

import logging

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot

from lsst.ts.mtdomegui import Model
from lsst.ts.mtdomegui.tab import TabInterlock


@pytest.fixture
def widget(qtbot: QtBot) -> TabInterlock:
    widget = TabInterlock("Interlock", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabInterlock) -> None:
    interlocks_and_sensors = widget.model.reporter.status.interlocks_and_sensors
    indicators = widget._indicators

    assert len(indicators) == 8
    for key in interlocks_and_sensors.keys():
        if key.startswith("interlocks"):
            assert len(indicators[key]) == len(interlocks_and_sensors[key])


def test_update_interlock_status(widget: TabInterlock) -> None:
    indicator = widget._indicators["interlocksAMCS"]["gisA3Active"]
    assert indicator.palette().color(QPalette.Base) != Qt.green

    widget.update_interlock_status("interlocksAMCS", {"gisA3Active": False})

    assert indicator.palette().color(QPalette.Base) == Qt.green

    widget.update_interlock_status("interlocksAMCS", {"gisA3Active": True})

    assert indicator.palette().color(QPalette.Base) == Qt.red
