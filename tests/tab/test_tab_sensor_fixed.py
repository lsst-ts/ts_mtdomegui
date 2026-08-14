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
from lsst.ts.mtdomegui.tab import TabSensorFixed


@pytest.fixture
def widget(qtbot: QtBot) -> TabSensorFixed:
    widget = TabSensorFixed("Sensor (Fixed Part)", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabSensorFixed) -> None:
    interlocks_and_sensors = widget.model.reporter.status.interlocks_and_sensors
    indicators = widget._indicators

    assert len(indicators) == 6
    for key in interlocks_and_sensors.keys():
        if key.startswith("sensorsFixedPart"):
            assert len(indicators[key]) == len(interlocks_and_sensors[key])


def test_update_sensor_status(widget: TabSensorFixed) -> None:
    interlocks_and_sensors = widget.model.reporter.status.interlocks_and_sensors

    group_name = "sensorsFixedPartValves"
    interlocks_and_sensors[group_name]["valve1AdbsCabinetValue"] = 12.345

    widget.update_sensor_status(group_name, interlocks_and_sensors[group_name])

    assert widget._indicators[group_name]["valve1AdbsCabinetValue"].text() == "12.35 %"
    assert widget._indicators[group_name]["valve2AdbsCabinetValue"].text() == "0.00 %"


def test_update_boolean_indicator_status(widget: TabSensorFixed) -> None:
    indicator = widget._indicators["sensorsFixedPartAlarms"]["accessPoint"]
    widget._update_boolean_indicator_status(indicator, False)

    assert indicator.palette().color(QPalette.Base) == Qt.gray

    widget._update_boolean_indicator_status(indicator, True)

    assert indicator.palette().color(QPalette.Base) == Qt.yellow
