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

__all__ = ["Model"]

import logging

from .reporter import Reporter


class Model:
    """Model class of the application.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.
    is_simulation_mode: `bool`, optional
        True if running in simulation mode. (the default is False)
    duration_refresh : `int`, optional
        Duration to refresh the data in milliseconds. (the default is 200)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    connection_information : `dict`
        TCP/IP connection information.
    duration_refresh : `int`
        Duration to refresh the data in milliseconds.
    reporter : `Reporter`
        Reporter to report the status and telemetry.
    """

    def __init__(
        self,
        log: logging.Logger,
        is_simulation_mode: bool = False,
        duration_refresh: int = 200,
    ) -> None:

        self.log = log
        self._is_simulation_mode = is_simulation_mode

        # TODO: Put this into the ts_config_mttcs in DM-48109.
        self.connection_information = {
            "host": "localhost",
            "port": 1000,
            "timeout_connection": 10.0,
        }

        self.duration_refresh = duration_refresh

        self.reporter = Reporter(self.log)
