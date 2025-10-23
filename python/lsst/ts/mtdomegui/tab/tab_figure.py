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

__all__ = ["TabFigure"]

from lsst.ts.guitool import FigureConstant, TabTemplate
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QVBoxLayout

from ..model import Model


class TabFigure(TabTemplate):
    """Table of the figure.

    Parameters
    ----------
    title : `str`
        Table's title.
    model : `Model`
        Model class.
    title_y : `str`
        Title of the y axis.
    legends : `list` [`str`]
        Legends. Each line should have a legend item.
    num_realtime : `int`, optional
        Number of the realtime data (>=0). (the default is 200)

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    MIN_WIDTH = 150

    def __init__(
        self,
        title: str,
        model: Model,
        title_y: str,
        legends: list[str],
        num_realtime: int = 200,
    ) -> None:
        super().__init__(title)

        self.model = model

        self._data = [[0.0] * num_realtime for _ in range(len(legends))]
        self._figure = self._create_figure(title_y, legends, num_realtime)

        self.set_widget_and_layout()

    def _create_figure(
        self,
        title_y: str,
        legends: list[str],
        num_realtime: int,
    ) -> FigureConstant:
        """Create the figure to show the temperature.

        Parameters
        ----------
        title_y : `str`
            Title of the y axis.
        legends : `list` [`str`]
            Legends. The number of elements should be the same as num_lines,
            otherwise, there will be the IndexError.
        num_realtime : `int`
            Number of the realtime data (>=0).

        Returns
        -------
        figure : `FigureConstant`
            Figure.
        """

        figure = FigureConstant(
            1,
            num_realtime,
            num_realtime,
            "Data Point",
            title_y,
            "",
            legends,
            num_lines=len(legends),
            is_realtime=True,
        )
        figure.axis_x.setLabelFormat("%d")

        return figure

    def create_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        self._figure.setMinimumWidth(self.MIN_WIDTH)
        layout.addWidget(self._figure)

        return layout

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)

        # Draw the cached data
        for idx, points in enumerate(self._data):
            for point in points:
                self._figure.append_data(point, idx=idx)

    def append_data(self, new_data: list[float]) -> None:
        """Append the data to the internal cache while keeping the same length.
        The figure will only be updated when it is visible to save the CPU
        usage.

        Parameters
        ----------
        new_data : `list` [`float`]
            New data.
        """

        for idx, value in enumerate(new_data):
            # Cache the new data
            self._data[idx].pop(0)
            self._data[idx].append(value)

            # Only update the figure when it is visible
            if self.isVisible():
                self._figure.append_data(value, idx=idx)
