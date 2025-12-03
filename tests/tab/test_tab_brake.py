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

# TODO: OSW-1538, use MTDome.Brake after the ts_xml: 24.4.
from lsst.ts.mtdomecom import Brake
from lsst.ts.mtdomegui import Model
from lsst.ts.mtdomegui.tab import TabBrake


@pytest.fixture
def widget(qtbot: QtBot) -> TabBrake:
    widget = TabBrake("Brake", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabBrake) -> None:
    assert len(widget._indicators_brake) == len(Brake)


def test_update_indicator_color(widget: TabBrake) -> None:
    indicator = widget._indicators_brake[0]
    widget._update_indicator_color(indicator, False)

    assert indicator.palette().color(QPalette.Button) == Qt.green

    widget._update_indicator_color(indicator, True)

    assert indicator.palette().color(QPalette.Button) == Qt.yellow
