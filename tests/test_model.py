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

import asyncio
import logging
import math
from copy import deepcopy

import pytest
import pytest_asyncio
from pytestqt.qtbot import QtBot

from lsst.ts.guitool import get_config_dir
from lsst.ts.mtdomecom import LCS_NUM_LOUVERS, RAD_NUM_DOORS, LlcName, ResponseCode
from lsst.ts.mtdomegui import Model
from lsst.ts.xml.enums import MTDome

CONFIG_DIR = get_config_dir("MTDome/v4")
TIMEOUT = 1000


@pytest.fixture
def model() -> Model:
    return Model(logging.getLogger())


@pytest_asyncio.fixture
async def model_async() -> Model:
    async with Model(logging.getLogger(), config_dir=CONFIG_DIR, is_simulation_mode=True) as model_sim:
        await model_sim.connect()

        yield model_sim


@pytest_asyncio.fixture
async def model_async_communication_error() -> Model:
    async with Model(logging.getLogger(), config_dir=CONFIG_DIR, is_simulation_mode=True) as model_sim:
        await model_sim.connect()
        model_sim.communication_error = True

        yield model_sim


def test_init(model: Model) -> None:
    assert len(model.connection_information) == 2


@pytest.mark.asyncio
async def test_connect(model_async: Model) -> None:
    assert model_async.is_connected() is True


def test_assert_is_connected(model: Model) -> None:
    with pytest.raises(RuntimeError):
        model.assert_is_connected()


@pytest.mark.asyncio
async def test_disconnect(model_async: Model) -> None:
    await model_async.disconnect()

    assert model_async.is_connected() is False


@pytest.mark.asyncio
async def test_low_level_component_status(qtbot: QtBot, model_async: Model) -> None:
    # Cache the interlocks_and_sensors in status
    reporter = model_async.reporter
    interlocks_and_sensors_cached = deepcopy(reporter.status.interlocks_and_sensors)

    # Reset the interlocks_and_sensors in status to empty dicts
    for key in reporter.status.interlocks_and_sensors.keys():
        reporter.status.interlocks_and_sensors[key] = dict()

    # Wait for the signals
    signals = [
        reporter.signals["telemetry"].amcs,
        reporter.signals["interlock"].amcs,
        reporter.signals["interlock"].lwscs,
        reporter.signals["interlock"].apscs,
        reporter.signals["interlock"].lcs,
        reporter.signals["interlock"].obc,
        reporter.signals["interlock"].rad,
        reporter.signals["interlock"].cscs,
        reporter.signals["interlock"].locking_pins,
        reporter.signals["sensor"].fixed_part_alarms,
        reporter.signals["sensor"].fixed_part_inflatable_seal,
        reporter.signals["sensor"].fixed_part_lines_24v,
        reporter.signals["sensor"].fixed_part_selectors,
        reporter.signals["sensor"].fixed_part_valves,
        reporter.signals["sensor"].fixed_part,
        reporter.signals["sensor"].rotating_part_lines_24v,
        reporter.signals["sensor"].rotating_part_locking_pins,
        reporter.signals["sensor"].rotating_part_alarms,
        reporter.signals["sensor"].rotating_part_doors_closed,
        reporter.signals["sensor"].rotating_part_cabinet_fan,
        reporter.signals["sensor"].rotating_part_limit_switches,
        reporter.signals["sensor"].rotating_part_selectors,
        reporter.signals["sensor"].rotating_part_emergency_pushbuttons,
        reporter.signals["sensor"].rotating_part_power_available,
        reporter.signals["sensor"].rotating_part_hatches,
        reporter.signals["sensor"].rotating_part_photocells,
        reporter.signals["sensor"].rotating_part_light_curtain,
        reporter.signals["sensor"].rotating_part_obc,
        reporter.signals["sensor"].rotating_part_axial_fans,
        reporter.signals["sensor"].rotating_part_lights,
        reporter.signals["sensor"].rotating_part_heating_cables,
        reporter.signals["sensor"].rotating_part_brakes,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        await asyncio.sleep(1.0)

    # Check the interlocks_and_sensors in status is updated and is the same
    # as the cached interlocks_and_sensors. By doing so, we can confirm the
    # default value of the interlocks_and_sensors in status is the same as the
    # simulation value in the low-level components.
    assert reporter.status.interlocks_and_sensors == interlocks_and_sensors_cached


@pytest.mark.asyncio
async def test_report_exception_communication_error(
    qtbot: QtBot, model_async_communication_error: Model
) -> None:
    signals = [
        model_async_communication_error.reporter.signals["fault_code"].aperture_shutter,
        model_async_communication_error.reporter.signals["fault_code"].elevation_axis,
        model_async_communication_error.reporter.signals["fault_code"].louvers,
        model_async_communication_error.reporter.signals["fault_code"].rear_access_door,
        model_async_communication_error.reporter.signals["fault_code"].calibration_screen,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        await asyncio.sleep(5.0)


@pytest.mark.asyncio
async def test_report_exception_fault_code_rotating_part(qtbot: QtBot, model: Model) -> None:
    signals = [
        model.reporter.signals["state"].aperture_shutter,
        model.reporter.signals["state"].elevation_axis,
        model.reporter.signals["state"].louvers,
        model.reporter.signals["state"].rear_access_door,
        model.reporter.signals["state"].calibration_screen,
        model.reporter.signals["fault_code"].aperture_shutter,
        model.reporter.signals["fault_code"].elevation_axis,
        model.reporter.signals["fault_code"].louvers,
        model.reporter.signals["fault_code"].rear_access_door,
        model.reporter.signals["fault_code"].calibration_screen,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        await model._report_exception_fault_code(
            LlcName.APSCS,
            ResponseCode.ROTATING_PART_NOT_RECEIVED,
            "exception message by the rotating part",
        )
        await model._report_exception_fault_code(
            LlcName.LWSCS,
            ResponseCode.ROTATING_PART_NOT_REPLIED,
            "exception message by the rotating part",
        )
        await model._report_exception_fault_code(
            LlcName.LCS,
            ResponseCode.ROTATING_PART_NOT_REPLIED,
            "exception message by the rotating part",
        )
        await model._report_exception_fault_code(
            LlcName.RAD,
            ResponseCode.ROTATING_PART_NOT_REPLIED,
            "exception message by the rotating part",
        )
        await model._report_exception_fault_code(
            LlcName.CSCS,
            ResponseCode.ROTATING_PART_NOT_REPLIED,
            "exception message by the rotating part",
        )


@pytest.mark.asyncio
async def test_report_exception_fault_code_lost_connection(model_async: Model) -> None:
    assert model_async.is_connected() is True

    await model_async._report_exception_fault_code(
        LlcName.APSCS,
        ResponseCode.NOT_CONNECTED,
        "exception message by the fixing part",
        is_prompted=False,
    )

    assert model_async.is_connected() is False


def test_report_operational_mode(model: Model) -> None:
    mode = MTDome.OperationalMode.DEGRADED

    model._report_operational_mode(LlcName.LWSCS, {"operationalMode": mode.name})

    assert model.reporter.status.operational_modes[1] == mode.value


def test_get_subsystem_id(model: Model) -> None:
    subsystem_id = model._get_subsystem_id(LlcName.LWSCS)

    assert subsystem_id == MTDome.SubSystemId.LWSCS


def test_report_configuration(model: Model) -> None:
    # AMCS
    data_amcs = {
        "appliedConfiguration": {
            "jmax": 1.0,
            "amax": 2.0,
            "vmax": 3.0,
        }
    }

    model._report_configuration(LlcName.AMCS, data_amcs)

    status = model.reporter.status
    assert status.config_amcs["jmax"] == math.degrees(1.0)
    assert status.config_amcs["amax"] == math.degrees(2.0)
    assert status.config_amcs["vmax"] == math.degrees(3.0)

    # LWSCS
    data_lwscs = {
        "appliedConfiguration": {
            "jmax": 4.0,
            "amax": 5.0,
            "vmax": 6.0,
        }
    }

    model._report_configuration(LlcName.LWSCS, data_lwscs)

    assert status.config_lwscs["jmax"] == math.degrees(4.0)
    assert status.config_lwscs["amax"] == math.degrees(5.0)
    assert status.config_lwscs["vmax"] == math.degrees(6.0)


def test_check_errors_and_report_azimuth(qtbot: QtBot, model: Model) -> None:
    status = {
        "messages": [{"code": 0, "description": "No Errors"}],
        "status": "STOPPED",
    }

    signals = [
        model.reporter.signals["state"].azimuth_axis,
        model.reporter.signals["fault_code"].azimuth_axis,
        model.reporter.signals["motion"].azimuth_axis,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model._check_errors_and_report_azimuth(status)


def test_get_fault_code(model: Model) -> None:
    # Normal data
    status_normal = {"messages": [{"code": 0, "description": "No Errors"}]}

    has_error, fault_code = model._get_fault_code(status_normal)

    assert has_error is False
    assert fault_code == ""

    # Error data
    status_error = {
        "messages": [
            {"code": 1, "description": "Errors 1"},
            {"code": ResponseCode.PHOTOCELLS_CODE.value, "description": "Errors 2"},
        ]
    }

    has_error, fault_code = model._get_fault_code(status_error)

    assert has_error is True
    assert fault_code == "1=Errors 1, 3037=Errors 2"

    # Since we have multiple messages, no bypass of codes.
    has_error, fault_code = model._get_fault_code(status_error, bypass_code=ResponseCode.PHOTOCELLS_CODE)

    assert has_error is True
    assert fault_code == "1=Errors 1, 3037=Errors 2"

    # Error data to be bypassed
    status_error_bypass = {
        "messages": [
            {"code": ResponseCode.PHOTOCELLS_CODE.value, "description": "Error photocells"},
        ]
    }

    has_error, fault_code = model._get_fault_code(
        status_error_bypass, bypass_code=ResponseCode.PHOTOCELLS_CODE
    )

    assert has_error is False
    assert fault_code == ""


def test_translate_motion_state_if_necessary(model: Model) -> None:
    assert model._translate_motion_state_if_necessary("STOPPED") == MTDome.MotionState.STOPPED

    assert model._translate_motion_state_if_necessary("STATIONARY") == MTDome.MotionState.STOPPED_BRAKED

    assert model._translate_motion_state_if_necessary("ABC") is None


def test_set_brakes_engaged_bit(model: Model) -> None:
    model._set_brakes_engaged_bit(MTDome.MotionState.BRAKES_ENGAGED, MTDome.Brake.AMCS.value)
    assert model._brakes_engaged_bitmask == 2

    model._set_brakes_engaged_bit(MTDome.MotionState.BRAKES_ENGAGED, MTDome.Brake.APSCS_LEFT_DOOR.value)
    model._set_brakes_engaged_bit(MTDome.MotionState.BRAKES_ENGAGED, MTDome.Brake.APSCS_RIGHT_DOOR.value)
    assert model._brakes_engaged_bitmask == 14

    model._set_brakes_engaged_bit(MTDome.MotionState.MOVING, MTDome.Brake.AMCS.value)
    assert model._brakes_engaged_bitmask == 12

    model._set_brakes_engaged_bit(MTDome.MotionState.MOVING, MTDome.Brake.APSCS_LEFT_DOOR.value)
    model._set_brakes_engaged_bit(MTDome.MotionState.MOVING, MTDome.Brake.APSCS_RIGHT_DOOR.value)
    assert model._brakes_engaged_bitmask == 0


def test_check_errors_and_report_elevation(qtbot: QtBot, model: Model) -> None:
    status = {
        "messages": [{"code": 0, "description": "No Errors"}],
        "status": "STOPPED",
    }

    signals = [
        model.reporter.signals["state"].elevation_axis,
        model.reporter.signals["fault_code"].elevation_axis,
        model.reporter.signals["motion"].elevation_axis,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model._check_errors_and_report_elevation(status)


def test_check_errors_and_report_aperture_shutter(qtbot: QtBot, model: Model) -> None:
    status = {
        "messages": [{"code": 0, "description": "No Errors"}],
        "status": ["STOPPED", "STOPPED"],
    }

    signals = [
        model.reporter.signals["state"].aperture_shutter,
        model.reporter.signals["fault_code"].aperture_shutter,
        model.reporter.signals["motion"].aperture_shutter,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model._check_errors_and_report_aperture_shutter(status)


def test_check_errors_and_report_louvers(qtbot: QtBot, model: Model) -> None:
    status = {
        "messages": [{"code": 0, "description": "No Errors"}],
        "status": ["STOPPED"] * LCS_NUM_LOUVERS,
    }

    signals = [
        model.reporter.signals["state"].louvers,
        model.reporter.signals["fault_code"].louvers,
        model.reporter.signals["motion"].louvers,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model._check_errors_and_report_louvers(status)


def test_check_errors_and_report_rear_access_door(qtbot: QtBot, model: Model) -> None:
    status = {
        "messages": [{"code": 0, "description": "No Errors"}],
        "status": ["STOPPED"] * RAD_NUM_DOORS,
    }

    signals = [
        model.reporter.signals["state"].rear_access_door,
        model.reporter.signals["fault_code"].rear_access_door,
        model.reporter.signals["motion"].rear_access_door,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model._check_errors_and_report_rear_access_door(status)


def test_check_errors_and_report_calibration_screen(qtbot: QtBot, model: Model) -> None:
    status = {
        "messages": [{"code": 0, "description": "No Errors"}],
        "status": "STOPPED",
    }

    signals = [
        model.reporter.signals["state"].calibration_screen,
        model.reporter.signals["fault_code"].calibration_screen,
        model.reporter.signals["motion"].calibration_screen,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model._check_errors_and_report_calibration_screen(status)
