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

__all__ = ["TabSettings"]

import math

from lsst.ts.guitool import (
    LOG_LEVEL_MAXIMUM,
    LOG_LEVEL_MINIMUM,
    POINT_SIZE_MAXIMUM,
    POINT_SIZE_MINIMUM,
    PORT_MAXIMUM,
    PORT_MINIMUM,
    REFRESH_FREQUENCY_MAXIMUM,
    REFRESH_FREQUENCY_MINIMUM,
    TIMEOUT_MINIMUM,
    TabTemplate,
    create_double_spin_box,
    create_group_box,
    set_button,
)
from lsst.ts.mtdomecom import (
    AMCS_AMAX,
    AMCS_JMAX,
    AMCS_VMAX,
    LWSCS_AMAX,
    LWSCS_JMAX,
    LWSCS_VMAX,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)
from qasync import QApplication, asyncSlot

from ..model import Model


class TabSettings(TabTemplate):
    """Table of the settings.

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

        self._settings_app = self._create_settings_app()
        self._settings_amcs = self._create_settings_cs(
            math.degrees(AMCS_JMAX), math.degrees(AMCS_AMAX), math.degrees(AMCS_VMAX)
        )
        self._settings_lwscs = self._create_settings_cs(
            math.degrees(LWSCS_JMAX), math.degrees(LWSCS_AMAX), math.degrees(LWSCS_VMAX)
        )

        self._buttons = self._create_buttons()

        self.set_widget_and_layout()

    def _create_settings_app(self) -> dict:
        """Create the application settings.

        Returns
        -------
        `dict`
            Settings.
        """

        settings = {
            "host": QLineEdit(),
            "port": QSpinBox(),
            "timeout_connection": QSpinBox(),
            "log_level": QSpinBox(),
            "refresh_frequency": QSpinBox(),
            "point_size": QSpinBox(),
        }

        settings["port"].setRange(PORT_MINIMUM, PORT_MAXIMUM)

        settings["timeout_connection"].setMinimum(TIMEOUT_MINIMUM)
        settings["timeout_connection"].setSuffix(" sec")

        settings["log_level"].setRange(LOG_LEVEL_MINIMUM, LOG_LEVEL_MAXIMUM)
        settings["log_level"].setToolTip(
            "CRITICAL (50), ERROR (40), WARNING (30), INFO (20), DEBUG (10)"
        )

        settings["refresh_frequency"].setRange(
            REFRESH_FREQUENCY_MINIMUM, REFRESH_FREQUENCY_MAXIMUM
        )
        settings["refresh_frequency"].setSuffix(" Hz")
        settings["refresh_frequency"].setToolTip(
            "Frequency to refresh the data on tables"
        )

        settings["point_size"].setRange(POINT_SIZE_MINIMUM, POINT_SIZE_MAXIMUM)
        settings["point_size"].setToolTip("Point size of the application.")

        # Set the default values
        connection_information = self.model.connection_information
        settings["host"].setText(connection_information["host"])
        settings["port"].setValue(connection_information["port"])
        settings["timeout_connection"].setValue(
            connection_information["timeout_connection"]
        )

        settings["log_level"].setValue(self.model.log.level)

        # The unit of self.model.duration_refresh is milliseconds
        frequency = int(1000 / self.model.duration_refresh)
        settings["refresh_frequency"].setValue(frequency)

        app = QApplication.instance()
        settings["point_size"].setValue(app.font().pointSize())

        self._set_minimum_width_line_edit(settings["host"])

        return settings

    def _set_minimum_width_line_edit(
        self, line_edit: QLineEdit, offset: int = 20
    ) -> None:
        """Set the minimum width of line edit.

        Parameters
        ----------
        line_edit : `PySide6.QtWidgets.QLineEdit`
            Line edit.
        offset : `int`, optional
            Offset of the width. (the default is 20)
        """

        font_metrics = line_edit.fontMetrics()

        text = line_edit.text()
        width = font_metrics.boundingRect(text).width()
        line_edit.setMinimumWidth(width + offset)

    def _create_settings_cs(
        self,
        max_jerk: float,
        max_acceleration: float,
        max_velocity: float,
        decimal: int = 3,
    ) -> dict:
        """Create the settings of the control system.

        Parameters
        ----------
        max_jerk : `float`
            Maximum jerk in deg/sec^3.
        max_acceleration : `float`
            Maximum acceleration in deg/sec^2.
        max_velocity : `float`
            Maximum velocity in deg/sec.
        decimal : `int`, optional
            Decimal. (the default is 3)

        Returns
        -------
        `dict`
            Settings of the control system.
        """

        tool_tip = "-1 means no value should be set."
        return {
            "jerk": create_double_spin_box(
                "deg/sec^3", decimal, maximum=max_jerk, minimum=-1.0, tool_tip=tool_tip
            ),
            "acceleration": create_double_spin_box(
                "deg/sec^2",
                decimal,
                maximum=max_acceleration,
                minimum=-1.0,
                tool_tip=tool_tip,
            ),
            "velocity": create_double_spin_box(
                "deg/sec",
                decimal,
                maximum=max_velocity,
                minimum=-1.0,
                tool_tip=tool_tip,
            ),
        }

    def _create_buttons(self) -> dict[str, QPushButton]:
        """Create the buttons.

        Returns
        -------
        `dict`
            Buttons. The keys are the names of the buttons and the values are
            the buttons.
        """

        apply_host = set_button("Apply Host Settings", self._callback_apply_host)
        apply_general = set_button(
            "Apply General Settings", self._callback_apply_general
        )
        apply_amcs = set_button(
            "Apply Azimuth Settings",
            self._callback_apply_amcs,
            tool_tip="Apply the azimuth settings to the controller.",
        )
        apply_lwscs = set_button(
            "Apply Elevation Settings",
            self._callback_apply_lwscs,
            tool_tip="Apply the elevation settings to the controller.",
        )

        return {
            "apply_host": apply_host,
            "apply_general": apply_general,
            "apply_amcs": apply_amcs,
            "apply_lwscs": apply_lwscs,
        }

    @asyncSlot()
    async def _callback_apply_host(self) -> None:
        """Callback of the apply-host-setting button. This will apply the
        new host settings to model."""

        connection_information = self.model.connection_information
        connection_information["host"] = self._settings_app["host"].text()
        connection_information["port"] = self._settings_app["port"].value()
        connection_information["timeout_connection"] = self._settings_app[
            "timeout_connection"
        ].value()

    @asyncSlot()
    async def _callback_apply_general(self) -> None:
        """Callback of the apply-general-settings button. This will apply the
        new general settings to model."""

        self.model.log.setLevel(self._settings_app["log_level"].value())

        # The unit of self.model.duration_refresh is milliseconds
        self.model.duration_refresh = int(
            1000.0 / self._settings_app["refresh_frequency"].value()
        )

        # Update the point size
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(self._settings_app["point_size"].value())
        app.setFont(font)

    @asyncSlot()
    async def _callback_apply_amcs(self) -> None:
        """Callback of the apply-azimuth-settings button. This will apply the
        new AMCS settings to controller."""

        self.model.log.info("Apply the AMCS settings to the controller.")

    @asyncSlot()
    async def _callback_apply_lwscs(self) -> None:
        """Callback of the apply-elevation-settings button. This will apply the
        new LWSCS settings to controller."""

        self.model.log.info("Apply the elevation (LWSCS) settings to the controller.")

    def create_layout(self) -> QVBoxLayout:

        # First column
        layout_app = QVBoxLayout()
        layout_app.addWidget(self._create_group_tcpip())
        layout_app.addWidget(self._create_group_application())

        # Second column
        layout_cs = QVBoxLayout()
        layout_cs.addWidget(self._create_group_amcs())
        layout_cs.addWidget(self._create_group_lwscs())

        layout = QHBoxLayout()
        layout.addLayout(layout_app)
        layout.addLayout(layout_cs)

        return layout

    def _create_group_tcpip(self) -> QGroupBox:
        """Create the group of TCP/IP connection.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_tcpip = QFormLayout()
        layout_tcpip.addRow("Host name:", self._settings_app["host"])
        layout_tcpip.addRow("Port:", self._settings_app["port"])
        layout_tcpip.addRow(
            "Connection timeout:", self._settings_app["timeout_connection"]
        )

        layout = QVBoxLayout()
        layout.addLayout(layout_tcpip)
        layout.addWidget(self._buttons["apply_host"])

        return create_group_box("Tcp/Ip Connection", layout)

    def _create_group_application(self) -> QGroupBox:
        """Create the group of application.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_app = QFormLayout()
        layout_app.addRow("Point size:", self._settings_app["point_size"])
        layout_app.addRow("Logging level:", self._settings_app["log_level"])
        layout_app.addRow("Refresh frequency:", self._settings_app["refresh_frequency"])

        layout = QVBoxLayout()
        layout.addLayout(layout_app)
        layout.addWidget(self._buttons["apply_general"])

        return create_group_box("Application", layout)

    def _create_group_amcs(self) -> QGroupBox:
        """Create the group of azimuth motion control system (AMCS).

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_amcs = QFormLayout()
        layout_amcs.addRow("Maximum jerk:", self._settings_amcs["jerk"])
        layout_amcs.addRow("Maximum acceleration:", self._settings_amcs["acceleration"])
        layout_amcs.addRow("Maximum velocity:", self._settings_amcs["velocity"])

        layout = QVBoxLayout()
        layout.addLayout(layout_amcs)
        layout.addWidget(self._buttons["apply_amcs"])

        return create_group_box("Azimuth Motion Control System", layout)

    def _create_group_lwscs(self) -> QGroupBox:
        """Create the group of elevation (light wind screen) control system
        (LWSCS) .

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_lwscs = QFormLayout()
        layout_lwscs.addRow("Maximum jerk:", self._settings_lwscs["jerk"])
        layout_lwscs.addRow(
            "Maximum acceleration:", self._settings_lwscs["acceleration"]
        )
        layout_lwscs.addRow("Maximum velocity:", self._settings_lwscs["velocity"])

        layout = QVBoxLayout()
        layout.addLayout(layout_lwscs)
        layout.addWidget(self._buttons["apply_lwscs"])

        return create_group_box("Elevation (Light Wind Screen) Control System", layout)
