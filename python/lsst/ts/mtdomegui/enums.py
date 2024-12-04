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

__all__ = ["ResponseCode"]

from enum import IntEnum


# Copy from the ts_mtdome.
# TODO: Remove it in DM-48109.
class ResponseCode(IntEnum):
    """Response codes.

    The codes mean

        * 0, "OK", "Command received correctly and is being executed."
        * 1, Not used.
        * 2, "Unsupported", "A command was sent that is not supported by the
          lower level component, for instance park is sent to LCS or 'mooveAz'
          instead of 'moveAz' to AMCS."
        * 3, "Incorrect parameter(s)", "The command that was sent is supported
          by the lower level component but the parameters for the command are
          incorrect. This can mean not enough parameters, too many parameters
          or one or more parameters with the wrong name."
        * 4, "Incorrect source", "The current command source is not valid, e.g.
          a remote command arrives while the system is operated in local mode,
          like the push buttons for the Aperture Shutters."
        * 5, "Incorrect state", "The current command cannot be executed in
          current state, e.g. moveAz when the AMCS is in fault state."
        * 6, "Rotating part did not receive", "It was not possible to forward
          the command to the rotating part."
        * 7, "Rotating part did not reply", "The command was sent to the
          rotating part, but it did not send a reply before a timeout."
    """

    OK = 0
    UNSUPPORTED = 2
    INCORRECT_PARAMETERS = 3
    INCORRECT_SOURCE = 4
    INCORRECT_STATE = 5
    ROTATING_PART_NOT_RECEIVED = 6
    ROTATING_PART_NOT_REPLIED = 7
