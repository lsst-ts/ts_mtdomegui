# This file is part of ts_mtdomegui.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import logging

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot

from lsst.ts.mtdomegui import Model
from lsst.ts.mtdomegui.tab import TabSensorRotating


@pytest.fixture
def widget(qtbot: QtBot) -> TabSensorRotating:
    widget = TabSensorRotating("Sensor (Rotating Part)", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabSensorRotating) -> None:
    interlocks_and_sensors = widget.model.reporter.status.interlocks_and_sensors
    indicators = widget._indicators

    assert len(indicators) == 17
    for key in interlocks_and_sensors.keys():
        if key.startswith("sensorsRotatingPart"):
            assert len(indicators[key]) == len(interlocks_and_sensors[key])


def test_update_sensor_status(widget: TabSensorRotating) -> None:
    interlocks_and_sensors = widget.model.reporter.status.interlocks_and_sensors

    group_name = "sensorsRotatingPartSelectors"
    interlocks_and_sensors[group_name]["llbvRadLouverSelected"] = 0
    interlocks_and_sensors[group_name]["llbvLocalBox1LouverSelected"] = 1

    widget.update_sensor_status(group_name, interlocks_and_sensors[group_name])

    assert widget._indicators[group_name]["llbvRadLouverSelected"].text() == "None"
    assert widget._indicators[group_name]["llbvLocalBox1LouverSelected"].text() == "A1"


def test_update_boolean_indicator_status(widget: TabSensorRotating) -> None:
    indicator = widget._indicators["sensorsRotatingPartLines24V"]["pilzHmi"]
    widget._update_boolean_indicator_status(indicator, False)

    assert indicator.palette().color(QPalette.Base) == Qt.gray

    widget._update_boolean_indicator_status(indicator, True)

    assert indicator.palette().color(QPalette.Base) == Qt.yellow
