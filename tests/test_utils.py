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

from lsst.ts.mtdomecom.schema import registry
from lsst.ts.mtdomegui import generate_dict_from_registry


def test_generate_dict_from_registry() -> None:

    data = generate_dict_from_registry(registry, "RAD", default_number=1.0)

    assert data["powerDraw"] == 1.0
    assert data["photoelectricSensorClear"] is False

    assert data["positionCommanded"][0] == 1.0
    assert data["openLimitSwitchEngaged"][0] is False
