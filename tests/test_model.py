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
import pytest_asyncio
from lsst.ts.guitool import get_config_dir
from lsst.ts.mtdomecom import LCS_NUM_LOUVERS, LlcName, ResponseCode
from lsst.ts.mtdomegui import Model
from lsst.ts.xml.enums import MTDome
from pytestqt.qtbot import QtBot

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
    with qtbot.waitSignal(model_async.reporter.signals["telemetry"].amcs, timeout=TIMEOUT):
        await asyncio.sleep(1.0)


@pytest.mark.asyncio
async def test_report_exception_communication_error(
    qtbot: QtBot, model_async_communication_error: Model
) -> None:
    signals = [
        model_async_communication_error.reporter.signals["fault_code"].aperture_shutter,
        model_async_communication_error.reporter.signals["fault_code"].elevation_axis,
        model_async_communication_error.reporter.signals["fault_code"].louvers,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        await asyncio.sleep(5.0)


@pytest.mark.asyncio
async def test_report_exception_fault_code_rotating_part(qtbot: QtBot, model: Model) -> None:
    signals = [
        model.reporter.signals["state"].aperture_shutter,
        model.reporter.signals["state"].elevation_axis,
        model.reporter.signals["state"].louvers,
        model.reporter.signals["fault_code"].aperture_shutter,
        model.reporter.signals["fault_code"].elevation_axis,
        model.reporter.signals["fault_code"].louvers,
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
            {"code": 2, "description": "Errors 2"},
        ]
    }

    has_error, fault_code = model._get_fault_code(status_error)

    assert has_error is True
    assert fault_code == "1=Errors 1, 2=Errors 2"


def test_translate_motion_state_if_necessary(model: Model) -> None:
    assert model._translate_motion_state_if_necessary("STOPPED") == MTDome.MotionState.STOPPED

    assert model._translate_motion_state_if_necessary("STATIONARY") == MTDome.MotionState.STOPPED_BRAKED

    assert model._translate_motion_state_if_necessary("ABC") is None


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
