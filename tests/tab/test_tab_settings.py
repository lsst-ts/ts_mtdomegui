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
import math

import pytest
from lsst.ts.guitool import (
    LOG_LEVEL_MAXIMUM,
    LOG_LEVEL_MINIMUM,
    POINT_SIZE_MAXIMUM,
    POINT_SIZE_MINIMUM,
    PORT_MAXIMUM,
    PORT_MINIMUM,
    REFRESH_FREQUENCY_MAXIMUM,
    REFRESH_FREQUENCY_MINIMUM,
)
from lsst.ts.mtdomecom import (
    AMCS_AMAX,
    AMCS_JMAX,
    AMCS_VMAX,
    LWSCS_AMAX,
    LWSCS_JMAX,
    LWSCS_VMAX,
)
from lsst.ts.mtdomegui import Model
from lsst.ts.mtdomegui.tab import TabSettings
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot
from qasync import QApplication


@pytest.fixture
def widget(qtbot: QtBot) -> TabSettings:
    widget = TabSettings("Settings", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabSettings) -> None:
    connection_information = widget.model.connection_information
    assert widget._settings_app["host"].text() == connection_information["host"]
    assert widget._settings_app["port"].value() == connection_information["port"]

    assert widget._settings_app["log_level"].value() == widget.model.log.level
    assert widget._settings_app["refresh_frequency"].value() == int(1000 / widget.model.duration_refresh)

    app = QApplication.instance()
    assert widget._settings_app["point_size"].value() == app.font().pointSize()

    assert widget._settings_app["port"].minimum() == PORT_MINIMUM
    assert widget._settings_app["port"].maximum() == PORT_MAXIMUM

    assert widget._settings_app["log_level"].minimum() == LOG_LEVEL_MINIMUM
    assert widget._settings_app["log_level"].maximum() == LOG_LEVEL_MAXIMUM

    line_edit = widget._settings_app["host"]
    font_metrics = line_edit.fontMetrics()
    assert line_edit.minimumWidth() == font_metrics.boundingRect(line_edit.text()).width() + 20

    assert widget._settings_app["refresh_frequency"].minimum() == REFRESH_FREQUENCY_MINIMUM
    assert widget._settings_app["refresh_frequency"].maximum() == REFRESH_FREQUENCY_MAXIMUM

    assert widget._settings_app["point_size"].minimum() == POINT_SIZE_MINIMUM
    assert widget._settings_app["point_size"].maximum() == POINT_SIZE_MAXIMUM

    assert widget._settings_amcs["jerk"].maximum() == pytest.approx(math.degrees(AMCS_JMAX))

    assert widget._settings_amcs["acceleration"].maximum() == pytest.approx(math.degrees(AMCS_AMAX))

    assert widget._settings_amcs["velocity"].maximum() == pytest.approx(math.degrees(AMCS_VMAX))

    assert widget._settings_lwscs["jerk"].maximum() == pytest.approx(math.degrees(LWSCS_JMAX))

    assert widget._settings_lwscs["acceleration"].maximum() == pytest.approx(math.degrees(LWSCS_AMAX))

    assert widget._settings_lwscs["velocity"].maximum() == pytest.approx(math.degrees(LWSCS_VMAX))


@pytest.mark.asyncio
async def test_callback_apply_host(qtbot: QtBot, widget: TabSettings) -> None:
    widget._settings_app["host"].setText("newHost")
    widget._settings_app["port"].setValue(1)

    qtbot.mouseClick(widget._buttons["apply_host"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    connection_information = widget.model.connection_information
    assert connection_information["host"] == "newHost"
    assert connection_information["port"] == 1


@pytest.mark.asyncio
async def test_callback_apply_general(qtbot: QtBot, widget: TabSettings) -> None:
    widget._settings_app["log_level"].setValue(11)
    widget._settings_app["refresh_frequency"].setValue(1)
    widget._settings_app["point_size"].setValue(12)

    qtbot.mouseClick(widget._buttons["apply_general"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.model.log.level == 11
    assert widget.model.duration_refresh == 1000

    app = QApplication.instance()
    assert app.font().pointSize() == 12


@pytest.mark.asyncio
async def test_set_signal_config(widget: TabSettings) -> None:
    config = {
        "jmax": 0.1,
        "amax": 0.2,
        "vmax": 0.3,
    }
    widget.model.reporter.report_config_azimuth(config)
    widget.model.reporter.report_config_elevation(config)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._settings_amcs["jerk"].value() == 0.1
    assert widget._settings_amcs["acceleration"].value() == 0.2
    assert widget._settings_amcs["velocity"].value() == 0.3

    assert widget._settings_lwscs["jerk"].value() == 0.1
    assert widget._settings_lwscs["acceleration"].value() == 0.2
    assert widget._settings_lwscs["velocity"].value() == 0.3
