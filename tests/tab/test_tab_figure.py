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
from pytestqt.qtbot import QtBot

from lsst.ts.mtdomegui import Model
from lsst.ts.mtdomegui.tab import TabFigure


@pytest.fixture
def widget(qtbot: QtBot) -> TabFigure:
    widget = TabFigure("Figure", Model(logging.getLogger()), "y", ["a", "b"])
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabFigure) -> None:
    assert len(widget._data) == 2
    assert len(widget._data[0]) == 200
    assert len(widget._data[1]) == 200


def test_append_data(widget: TabFigure) -> None:
    # Not visible
    widget.append_data([1.0, 2.0])

    assert len(widget._data[0]) == 200
    assert len(widget._data[1]) == 200

    assert widget._data[0][-1] == 1.0
    assert widget._data[1][-1] == 2.0

    assert len(widget._figure.get_points(0)) == 0

    # Visible
    widget.setVisible(True)

    assert len(widget._figure.get_points(0)) == 200
    assert widget._figure.get_points(0)[-1].y() == 1.0
    assert widget._figure.get_points(1)[-1].y() == 2.0

    # Add the new data
    widget.append_data([3.0, 4.0])

    assert len(widget._figure.get_points(0)) == 200
    assert widget._figure.get_points(0)[-2].y() == 1.0
    assert widget._figure.get_points(1)[-2].y() == 2.0

    assert widget._figure.get_points(0)[-1].y() == 3.0
    assert widget._figure.get_points(1)[-1].y() == 4.0

    # Not visible again and add the new data
    widget.setVisible(False)
    widget.append_data([5.0, 6.0])

    assert widget._data[0][-1] == 5.0
    assert widget._data[1][-1] == 6.0

    assert len(widget._figure.get_points(0)) == 200
    assert widget._figure.get_points(0)[-1].y() == 3.0
    assert widget._figure.get_points(1)[-1].y() == 4.0
