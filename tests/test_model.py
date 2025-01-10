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
from copy import deepcopy

import pytest
from lsst.ts.mtdomegui import Model
from lsst.ts.xml.enums import MTDome
from pytestqt.qtbot import QtBot

TIMEOUT = 1000


@pytest.fixture
def model() -> Model:
    return Model(logging.getLogger())


def test_init(model: Model) -> None:
    assert len(model.signals) == 4


def test_report_default(qtbot: QtBot, model: Model) -> None:

    signals = [
        model.signals["interlock"].interlock,
        model.signals["interlock"].locking_pins_engaged,
        model.signals["state"].brake_engaged,
        model.signals["state"].azimuth_axis,
        model.signals["state"].elevation_axis,
        model.signals["state"].aperture_shutter,
        model.signals["state"].power_mode,
        model.signals["operational_mode"].subsystem_mode,
        model.signals["telemetry"].amcs,
        model.signals["telemetry"].apscs,
        model.signals["telemetry"].cbcs,
        model.signals["telemetry"].cscs,
        model.signals["telemetry"].lcs,
        model.signals["telemetry"].lwscs,
        model.signals["telemetry"].rad,
        model.signals["telemetry"].thcs,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model.report_default()


def test_report_interlocks(qtbot: QtBot, model: Model) -> None:

    interlocks = deepcopy(model.status.interlocks)
    interlocks[0] = True

    with qtbot.waitSignal(model.signals["interlock"].interlock, timeout=TIMEOUT):
        model.report_interlocks(interlocks)

    assert model.status.interlocks == interlocks


def test_report_state_locking_pins_engaged(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(
        model.signals["interlock"].locking_pins_engaged, timeout=TIMEOUT
    ):
        model.report_state_locking_pins_engaged(1)

    assert model.status.state["lockingPinsEngaged"] == 1


def test_report_state_brake_engaged(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["state"].brake_engaged, timeout=TIMEOUT):
        model.report_state_brake_engaged(1)

    assert model.status.state["brakeEngaged"] == 1


def test_report_system_azimuth_axis(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["state"].azimuth_axis, timeout=TIMEOUT):
        model.report_system_azimuth_axis(MTDome.EnabledState.ENABLED)

    assert model.status.state["azimuthAxis"] == MTDome.EnabledState.ENABLED.value


def test_report_system_elevation_axis(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["state"].elevation_axis, timeout=TIMEOUT):
        model.report_system_elevation_axis(MTDome.EnabledState.ENABLED)

    assert model.status.state["elevationAxis"] == MTDome.EnabledState.ENABLED.value


def test_report_system_aperture_shutter(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["state"].aperture_shutter, timeout=TIMEOUT):
        model.report_system_aperture_shutter(MTDome.EnabledState.ENABLED)

    assert model.status.state["apertureShutter"] == MTDome.EnabledState.ENABLED.value


def test_report_system_power_mode(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["state"].power_mode, timeout=TIMEOUT):
        model.report_system_power_mode(MTDome.PowerManagementMode.EMERGENCY)

    assert model.status.state["powerMode"] == MTDome.PowerManagementMode.EMERGENCY.value


def test_report_operational_mode(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(
        model.signals["operational_mode"].subsystem_mode, timeout=TIMEOUT
    ):
        model.report_operational_mode(
            MTDome.SubSystemId.LCS, MTDome.OperationalMode.DEGRADED
        )

    assert model.status.operational_modes[3] == MTDome.OperationalMode.DEGRADED.value


def test_report_capacitor_bank(qtbot: QtBot, model: Model) -> None:

    capacitor_bank = deepcopy(model.status.capacitor_bank)
    capacitor_bank["doorOpen"][0] = True

    with qtbot.waitSignal(model.signals["telemetry"].cbcs, timeout=TIMEOUT):
        model.report_capacitor_bank(capacitor_bank)

    assert model.status.capacitor_bank == capacitor_bank


def test_report_telemetry(qtbot: QtBot, model: Model) -> None:

    with qtbot.waitSignal(model.signals["telemetry"].amcs, timeout=TIMEOUT):
        model.report_telemetry("amcs", dict())
