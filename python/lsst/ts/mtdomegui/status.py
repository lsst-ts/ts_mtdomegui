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

__all__ = ["Status"]

from dataclasses import dataclass, field

from lsst.ts.mtdomecom import CBCS_NUM_CAPACITOR_BANKS, MON_NUM_SENSORS
from lsst.ts.xml.enums import MTDome


@dataclass
class Status:
    """System status."""

    # Interlocks.
    interlocks: list[bool] = field(default_factory=lambda: [False] * MON_NUM_SENSORS)

    # System state. See the `SignalState` for the enum of each field.
    # Put the default values of "lockingPinsEngaged" and "brakeEngaged" to -1
    # because the related details are not defined yet.
    state: dict[str, int] = field(
        default_factory=lambda: {
            "lockingPinsEngaged": -1,
            "brakeEngaged": -1,
            "azimuthAxis": 0,
            "elevationAxis": 0,
            "apertureShutter": 0,
            "powerMode": 0,
        }
    )

    # List of the enum `MTDome.OperationalMode` for each subsystem.
    # The order is the same as the enum of `MTDome.SubSystemId`.
    operational_modes: list[int] = field(
        default_factory=lambda: [0] * len(MTDome.SubSystemId)
    )

    # Capacitor bank status.
    capacitor_bank: dict[str, list[bool]] = field(
        default_factory=lambda: (
            {
                "fuseIntervention": [False] * CBCS_NUM_CAPACITOR_BANKS,
                "smokeDetected": [False] * CBCS_NUM_CAPACITOR_BANKS,
                "highTemperature": [False] * CBCS_NUM_CAPACITOR_BANKS,
                "lowResidualVoltage": [False] * CBCS_NUM_CAPACITOR_BANKS,
                "doorOpen": [False] * CBCS_NUM_CAPACITOR_BANKS,
            }
        )
    )

    # Configuration of the azimuth motion control system (AMCS).
    config_amcs: dict[str, float] = field(
        default_factory=lambda: {
            "jmax": 0.0,
            "amax": 0.0,
            "vmax": 0.0,
        }
    )

    # Configuration of the light and wind screen control system (LWSCS).
    config_lwscs: dict[str, float] = field(
        default_factory=lambda: {
            "jmax": 0.0,
            "amax": 0.0,
            "vmax": 0.0,
        }
    )
