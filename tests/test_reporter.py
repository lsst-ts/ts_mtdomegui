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
from lsst.ts.mtdomecom import APSCS_NUM_SHUTTERS
from lsst.ts.mtdomegui import Reporter
from lsst.ts.xml.enums import MTDome
from pytestqt.qtbot import QtBot

TIMEOUT = 1000


@pytest.fixture
def reporter() -> Reporter:
    return Reporter(logging.getLogger())


def test_init(reporter: Reporter) -> None:
    assert len(reporter.signals) == 8


def test_report_default(qtbot: QtBot, reporter: Reporter) -> None:

    signals = [
        reporter.signals["interlock"].interlock,
        reporter.signals["interlock"].locking_pins_engaged,
        reporter.signals["state"].brake_engaged,
        reporter.signals["state"].azimuth_axis,
        reporter.signals["state"].elevation_axis,
        reporter.signals["state"].aperture_shutter,
        reporter.signals["state"].power_mode,
        reporter.signals["operational_mode"].subsystem_mode,
        reporter.signals["telemetry"].amcs,
        reporter.signals["telemetry"].apscs,
        reporter.signals["telemetry"].cbcs,
        reporter.signals["telemetry"].cbcs_voltage,
        reporter.signals["telemetry"].cscs,
        reporter.signals["telemetry"].lcs,
        reporter.signals["telemetry"].lwscs,
        reporter.signals["telemetry"].rad,
        reporter.signals["telemetry"].thcs,
        reporter.signals["target"].position_velocity_azimuth,
        reporter.signals["target"].position_velocity_elevation,
        reporter.signals["motion"].azimuth_axis,
        reporter.signals["motion"].elevation_axis,
        reporter.signals["motion"].aperture_shutter,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        reporter.report_default()


def test_report_interlocks(qtbot: QtBot, reporter: Reporter) -> None:

    interlocks = deepcopy(reporter.status.interlocks)
    interlocks[0] = True

    with qtbot.waitSignal(reporter.signals["interlock"].interlock, timeout=TIMEOUT):
        reporter.report_interlocks(interlocks)

    assert reporter.status.interlocks == interlocks


def test_report_state_locking_pins_engaged(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(
        reporter.signals["interlock"].locking_pins_engaged, timeout=TIMEOUT
    ):
        reporter.report_state_locking_pins_engaged(1)

    assert reporter.status.state["lockingPinsEngaged"] == 1


def test_report_state_brake_engaged(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(reporter.signals["state"].brake_engaged, timeout=TIMEOUT):
        reporter.report_state_brake_engaged(1)

    assert reporter.status.state["brakeEngaged"] == 1


def test_report_state_azimuth_axis(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(reporter.signals["state"].azimuth_axis, timeout=TIMEOUT):
        reporter.report_state_azimuth_axis(MTDome.EnabledState.ENABLED)

    assert reporter.status.state["azimuthAxis"] == MTDome.EnabledState.ENABLED.value


def test_report_state_elevation_axis(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(reporter.signals["state"].elevation_axis, timeout=TIMEOUT):
        reporter.report_state_elevation_axis(MTDome.EnabledState.ENABLED)

    assert reporter.status.state["elevationAxis"] == MTDome.EnabledState.ENABLED.value


def test_report_state_aperture_shutter(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(reporter.signals["state"].aperture_shutter, timeout=TIMEOUT):
        reporter.report_state_aperture_shutter(MTDome.EnabledState.ENABLED)

    assert reporter.status.state["apertureShutter"] == MTDome.EnabledState.ENABLED.value


def test_report_state_power_mode(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(reporter.signals["state"].power_mode, timeout=TIMEOUT):
        reporter.report_state_power_mode(MTDome.PowerManagementMode.EMERGENCY)

    assert (
        reporter.status.state["powerMode"] == MTDome.PowerManagementMode.EMERGENCY.value
    )


def test_report_operational_mode(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(
        reporter.signals["operational_mode"].subsystem_mode, timeout=TIMEOUT
    ):
        reporter.report_operational_mode(
            MTDome.SubSystemId.LCS, MTDome.OperationalMode.DEGRADED
        )

    assert reporter.status.operational_modes[3] == MTDome.OperationalMode.DEGRADED.value


def test_report_capacitor_bank(qtbot: QtBot, reporter: Reporter) -> None:

    capacitor_bank = deepcopy(reporter.status.capacitor_bank)
    capacitor_bank["doorOpen"][0] = True
    capacitor_bank["dcBusVoltage"] = 1.0

    with qtbot.waitSignals(
        [
            reporter.signals["telemetry"].cbcs,
            reporter.signals["telemetry"].cbcs_voltage,
        ],
        timeout=TIMEOUT,
    ):
        reporter.report_capacitor_bank(capacitor_bank)

    assert reporter.status.capacitor_bank == capacitor_bank
    assert "dcBusVoltage" not in capacitor_bank


def test_report_config_azimuth(qtbot: QtBot, reporter: Reporter) -> None:

    config = {
        "jmax": 0.1,
        "amax": 0.2,
        "vmax": 0.3,
    }
    with qtbot.waitSignal(reporter.signals["config"].amcs, timeout=TIMEOUT):
        reporter.report_config_azimuth(config)

    assert reporter.status.config_amcs == config


def test_report_config_elevation(qtbot: QtBot, reporter: Reporter) -> None:

    config = {
        "jmax": 0.1,
        "amax": 0.2,
        "vmax": 0.3,
    }
    with qtbot.waitSignal(reporter.signals["config"].lwscs, timeout=TIMEOUT):
        reporter.report_config_elevation(config)

    assert reporter.status.config_lwscs == config


def test_report_telemetry(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(reporter.signals["telemetry"].amcs, timeout=TIMEOUT):
        reporter.report_telemetry("amcs", dict())


def test_report_target_azimuth(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(
        reporter.signals["target"].position_velocity_azimuth, timeout=TIMEOUT
    ):
        reporter.report_target_azimuth(0.0, 0.0)


def test_report_target_elevation(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(
        reporter.signals["target"].position_velocity_elevation, timeout=TIMEOUT
    ):
        reporter.report_target_elevation(0.0, 0.0)


def test_report_motion_azimuth_axis(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(reporter.signals["motion"].azimuth_axis, timeout=TIMEOUT):
        reporter.report_motion_azimuth_axis(MTDome.MotionState.MOVING, True)


def test_report_motion_elevation_axis(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(reporter.signals["motion"].elevation_axis, timeout=TIMEOUT):
        reporter.report_motion_elevation_axis(MTDome.MotionState.MOVING, True)


def test_report_motion_aperture_shutter(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(reporter.signals["motion"].aperture_shutter, timeout=TIMEOUT):
        reporter.report_motion_aperture_shutter(
            [MTDome.MotionState.MOVING] * APSCS_NUM_SHUTTERS,
            [True] * APSCS_NUM_SHUTTERS,
        )


def test_report_fault_code_azimuth_axis(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(reporter.signals["fault_code"].azimuth_axis, timeout=TIMEOUT):
        reporter.report_fault_code_azimuth_axis("No error")


def test_report_fault_code_elevation_axis(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(
        reporter.signals["fault_code"].elevation_axis, timeout=TIMEOUT
    ):
        reporter.report_fault_code_elevation_axis("No error")


def test_report_fault_code_aperture_shutter(qtbot: QtBot, reporter: Reporter) -> None:

    with qtbot.waitSignal(
        reporter.signals["fault_code"].aperture_shutter, timeout=TIMEOUT
    ):
        reporter.report_fault_code_aperture_shutter("No error")
