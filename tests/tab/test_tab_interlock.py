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
from lsst.ts.mtdomegui import NUM_INTERLOCK, Model
from lsst.ts.mtdomegui.tab import TabInterlock
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabInterlock:
    widget = TabInterlock("Interlock", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabInterlock) -> None:

    assert len(widget._indicators_interlock) == NUM_INTERLOCK


def test_update_indicator_color(widget: TabInterlock) -> None:

    indicator = widget._indicators_interlock[0]
    widget._update_indicator_color(indicator, False)

    assert indicator.palette().color(QPalette.Button) == Qt.green

    widget._update_indicator_color(indicator, True)

    assert indicator.palette().color(QPalette.Button) == Qt.red
