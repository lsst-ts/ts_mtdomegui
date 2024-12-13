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
    "MAX_JERK",
    "MAX_ACCELERATION",
    "MAX_VELOCITY",
    "MAX_POSITION",
    "MAX_TEMPERATURE",
    "NUM_INTERLOCK",
    "NUM_POSITION_AZIMUTH",
    "NUM_RESOLVER_ELEVATION",
    "NUM_RESOLVER_SHUTTER",
    "NUM_RESOLVER_DOOR",
    "NUM_DRIVE_AZIMUTH",
    "NUM_DRIVE_ELEVATION",
    "NUM_DRIVE_SHUTTER",
    "NUM_DRIVE_LOUVER",
    "NUM_DRIVE_DOOR",
    "NUM_TEMPERATURE_AZIMUTH",
    "NUM_TEMPERATURE_ELEVATION",
    "NUM_TEMPERATURE_SHUTTER",
    "NUM_TEMPERATURE_LOUVER",
    "NUM_TEMPERATURE_THERMAL",
    "NUM_TEMPERATURE_DOOR",
    "NUM_DOOR_LIMIT_SWITCH",
    "NUM_DOOR_LOCKING_PIN",
    "NUM_DOOR_BRAKE",
    "SUBSYSTEMS",
]


# Maximum jerk in degree/second^3
MAX_JERK = 40.0

# Maximum acceleration in degree/second^2
MAX_ACCELERATION = 10.0

# Maximum velocity in degree/second
MAX_VELOCITY = 3.5

# Maximum position in degree
MAX_POSITION = 360.0

# Maximum temperature in degree Celsius
MAX_TEMPERATURE = 10.0

# Number of the interlocks
NUM_INTERLOCK = 16

# Number of the azimuth position encoders
NUM_POSITION_AZIMUTH = 3

# Number of the elevation (light/wind screen) resolvers
NUM_RESOLVER_ELEVATION = 2

# Number of the aperture shutter resolvers
NUM_RESOLVER_SHUTTER = 4

# Number of the rear access door resolvers
NUM_RESOLVER_DOOR = 2

# Number of the azimuth drives
NUM_DRIVE_AZIMUTH = 5

# Number of the elevation (light/wind screen) drives
NUM_DRIVE_ELEVATION = 2

# Number of the aperture shutter drives
NUM_DRIVE_SHUTTER = 4

# Number of the drives per louver
NUM_DRIVE_LOUVER = 2

# Number of the rear access door drives
NUM_DRIVE_DOOR = 2

# Number of the azimuth temperature sensors
NUM_TEMPERATURE_AZIMUTH = 13

# Number of the elevation (light/wind screen) temperature sensors
NUM_TEMPERATURE_ELEVATION = 2

# Number of the aperture shutter temperature sensors
NUM_TEMPERATURE_SHUTTER = 4

# Number of the temperature sensors per louver
NUM_TEMPERATURE_LOUVER = 2

# Number of the thermal temperature sensors
NUM_TEMPERATURE_THERMAL = 13

# Number of the rear access door temperature sensors
NUM_TEMPERATURE_DOOR = 2

# Number of the rear access door limit switches
NUM_DOOR_LIMIT_SWITCH = 4

# Number of the rear access door locking pins
NUM_DOOR_LOCKING_PIN = 2

# Number of the rear access door brakes
NUM_DOOR_BRAKE = 2

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
]
