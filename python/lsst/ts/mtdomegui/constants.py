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

__all__ = [
    "MAX_POSITION",
    "MAX_TEMPERATURE",
    "NUM_DRIVE_SHUTTER",
    "SUBSYSTEMS",
]

from lsst.ts.mtdomecom import APSCS_NUM_MOTORS_PER_SHUTTER, APSCS_NUM_SHUTTERS

# Maximum position in degree
MAX_POSITION = 360.0

# Maximum temperature in degree Celsius
MAX_TEMPERATURE = 10.0

# Number of the aperture shutter drives
NUM_DRIVE_SHUTTER = APSCS_NUM_MOTORS_PER_SHUTTER * APSCS_NUM_SHUTTERS

# Subsystems. This should be consistent with
# lsst.ts.xml.enums.MTDome.SubSystemId.
SUBSYSTEMS = [
    "Azimuth Motion Control System",
    "Light and Wind Screen Control System",
    "Aperture Shutter Control System",
    "Louvers Control System",
    "Thermal Control System",
    "Monitoring Control System",
    "Rear Access Door",
    "Calibration Screen Control System",
    "Overhead Bridge Crane",
    "Capacitor Banks Control System",
    "Software Control System",
]
