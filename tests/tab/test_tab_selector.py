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
from lsst.ts.mtdomegui import Model
from lsst.ts.mtdomegui.tab import TabSelector
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabSelector:
    widget = TabSelector("Selector", Model(logging.getLogger()), ["a", "b", "c"])
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabSelector) -> None:
    assert len(widget._buttons["selection"]) == 3


@pytest.mark.asyncio
async def test_callback_select_all(widget: TabSelector) -> None:
    await widget._callback_select_all()

    for button in widget._buttons["selection"]:
        assert button.isChecked() is True


@pytest.mark.asyncio
async def test_callback_reset_all(widget: TabSelector) -> None:
    await widget._callback_select_all()

    await widget._callback_reset_all()

    for button in widget._buttons["selection"]:
        assert button.isChecked() is False


def test_select(widget: TabSelector) -> None:
    selections = [0, 2]
    widget.select(selections)

    for idx, button in enumerate(widget._buttons["selection"]):
        if idx in selections:
            assert button.isChecked() is True
        else:
            assert button.isChecked() is False


def test_get_selection(widget: TabSelector) -> None:
    assert widget.get_selection() == []

    selections = [0, 2]
    widget.select(selections)

    assert widget.get_selection() == selections


def test_set_selection_enabled(widget: TabSelector) -> None:
    widget.set_selection_enabled(1, False)

    assert widget._buttons["selection"][1].isEnabled() is False

    selections = [1, 2]
    widget.select(selections)

    assert widget.get_selection() == [2]
