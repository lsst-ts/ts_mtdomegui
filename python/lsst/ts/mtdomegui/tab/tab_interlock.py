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

__all__ = ["TabInterlock"]

from PySide6.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QRadioButton, QVBoxLayout
from qasync import asyncSlot

from lsst.ts.guitool import (
    TabTemplate,
    create_group_box,
    create_radio_indicators,
)

from ..model import Model
from ..signals import SignalInterlock
from ..utils import update_boolean_indicator_status


class TabInterlock(TabTemplate):
    """Table of the interlock.

    Parameters
    ----------
    title : `str`
        Table's title.
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title)

        self.model = model

        self._indicators = self._create_indicators()

        self.set_widget_and_layout()

        signals = self.model.reporter.signals
        self._set_signal_interlock(signals["interlock"])  # type: ignore[arg-type]

    def _create_indicators(self) -> dict[str, dict[str, QRadioButton]]:
        """Creates the interlock indicators.

        Returns
        -------
        indicators : `dict` [`str`, `dict`]
            Interlock indicators.
        """

        interlocks_and_sensors = self.model.reporter.status.interlocks_and_sensors

        indicators: dict[str, dict[str, QRadioButton]] = dict()
        for key in interlocks_and_sensors.keys():
            if key.startswith("interlocks"):
                indicators[key] = dict()

                num = len(interlocks_and_sensors[key].keys())
                radio_indicators = create_radio_indicators(num)
                for idx, interlock in enumerate(interlocks_and_sensors[key].keys()):
                    indicators[key][interlock] = radio_indicators[idx]

        return indicators

    def create_layout(self) -> QVBoxLayout:
        layout = QHBoxLayout()

        counter_max = 15
        counter_current = 0
        layout_internal = QVBoxLayout()
        for group_key in self._indicators.keys():
            group, num = self._create_group_interlock(group_key)
            layout_internal.addWidget(group)
            counter_current += num

            if counter_current >= counter_max:
                layout.addLayout(layout_internal)
                layout_internal = QVBoxLayout()
                counter_current = 0

        if counter_current > 0:
            layout.addLayout(layout_internal)

        return layout

    def _create_group_interlock(self, group_key: str) -> tuple[QGroupBox, int]:
        """Create the group of interlock.

        Parameters
        ----------
        group_key : `str`
            Group key of the interlocks.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        `int`
            Number of the indicators.
        """

        layout = QFormLayout()

        indicators = self._indicators[group_key]
        for key in indicators.keys():
            layout.addRow(f"{key}:", indicators[key])

        return create_group_box(group_key, layout), len(indicators)

    def _set_signal_interlock(self, signal: SignalInterlock) -> None:
        """Set the interlock signal.

        Parameters
        ----------
        signal : `SignalInterlock`
            Interlock signal.
        """

        signal.amcs.connect(self._callback_interlock_amcs)
        signal.lwscs.connect(self._callback_interlock_lwscs)
        signal.apscs.connect(self._callback_interlock_apscs)
        signal.lcs.connect(self._callback_interlock_lcs)
        signal.obc.connect(self._callback_interlock_obc)
        signal.rad.connect(self._callback_interlock_rad)
        signal.cscs.connect(self._callback_interlock_cscs)
        signal.locking_pins.connect(self._callback_interlock_locking_pins)

    @asyncSlot()
    async def _callback_interlock_amcs(self, interlocks: dict[str, bool]) -> None:
        """Callback to update the interlock of AMCS.

        Parameters
        ----------
        interlocks : `dict` [`str`, `bool`]
            Status of the interlocks. True is engaged. Otherwise, False.
        """

        self.update_interlock_status("interlocksAMCS", interlocks)

    @asyncSlot()
    async def _callback_interlock_lwscs(self, interlocks: dict[str, bool]) -> None:
        """Callback to update the interlock of LWSCS.

        Parameters
        ----------
        interlocks : `dict` [`str`, `bool`]
            Status of the interlocks. True is engaged. Otherwise, False.
        """

        self.update_interlock_status("interlocksLWSCS", interlocks)

    @asyncSlot()
    async def _callback_interlock_apscs(self, interlocks: dict[str, bool]) -> None:
        """Callback to update the interlock of ApSCS.

        Parameters
        ----------
        interlocks : `dict` [`str`, `bool`]
            Status of the interlocks. True is engaged. Otherwise, False.
        """

        self.update_interlock_status("interlocksApSCS", interlocks)

    @asyncSlot()
    async def _callback_interlock_lcs(self, interlocks: dict[str, bool]) -> None:
        """Callback to update the interlock of LCS.

        Parameters
        ----------
        interlocks : `dict` [`str`, `bool`]
            Status of the interlocks. True is engaged. Otherwise, False.
        """

        self.update_interlock_status("interlocksLCS", interlocks)

    @asyncSlot()
    async def _callback_interlock_obc(self, interlocks: dict[str, bool]) -> None:
        """Callback to update the interlock of OBC.

        Parameters
        ----------
        interlocks : `dict` [`str`, `bool`]
            Status of the interlocks. True is engaged. Otherwise, False.
        """

        self.update_interlock_status("interlocksOBC", interlocks)

    @asyncSlot()
    async def _callback_interlock_rad(self, interlocks: dict[str, bool]) -> None:
        """Callback to update the interlock of RAD.

        Parameters
        ----------
        interlocks : `dict` [`str`, `bool`]
            Status of the interlocks. True is engaged. Otherwise, False.
        """

        self.update_interlock_status("interlocksRAD", interlocks)

    @asyncSlot()
    async def _callback_interlock_cscs(self, interlocks: dict[str, bool]) -> None:
        """Callback to update the interlock of CSCS.

        Parameters
        ----------
        interlocks : `dict` [`str`, `bool`]
            Status of the interlocks. True is engaged. Otherwise, False.
        """

        self.update_interlock_status("interlocksCSCS", interlocks)

    @asyncSlot()
    async def _callback_interlock_locking_pins(self, interlocks: dict[str, bool]) -> None:
        """Callback to update the interlock of locking pins.

        Parameters
        ----------
        interlocks : `dict` [`str`, `bool`]
            Status of the interlocks. True is engaged. Otherwise, False.
        """

        self.update_interlock_status("interlocksLockingPins", interlocks)

    def update_interlock_status(self, group_name: str, interlocks: dict[str, bool]) -> None:
        """Update the interlock status.

        Parameters
        ----------
        group_name : `str`
            Group name.
        interlocks : `dict` [`str`, `bool`]
            Status of the interlocks. True is engaged. Otherwise, False.
        """

        for interlock, is_fault in interlocks.items():
            update_boolean_indicator_status(self._indicators[group_name][interlock], is_fault)
