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

from lsst.ts.mtdomecom import CBCS_NUM_CAPACITOR_BANKS
from lsst.ts.xml.enums import MTDome


@dataclass
class Status:
    """System status."""

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
            "louvers": 0,
            "rearAccessDoor": 0,
            "calibrationScreen": 0,
            "powerMode": 0,
            "controlMode": 0,
        }
    )

    # List of the enum `MTDome.OperationalMode` for each subsystem.
    # The order is the same as the enum of `MTDome.SubSystemId`.
    operational_modes: list[int] = field(default_factory=lambda: [0] * len(MTDome.SubSystemId))

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

    # Status of the interlocks and sensors.
    interlocks_and_sensors: dict[str, dict[str, bool | int | float]] = field(
        default_factory=lambda: {
            "interlocksAMCS": {
                "gisA3Active": False,
                "gisA11Active": False,
                "emergencyPushbuttonPressed": False,
                "cabinetDoorsOpenOnRotatingPart": False,
                "sealNotDeflated": False,
                "craneNotParkedOverrideNotActive": False,
                "smallAuxiliaryCraneNotParked": False,
                "azLockingPinNotRetracted": False,
                "lightBafflesNotClosed": False,
                "apsLowerGangwayHatchNotClosed": False,
                "apsTopExteriorLeftHatchNotClosed": False,
                "apsTopExteriorRightHatchNotClosed": False,
                "radNotClosed": False,
            },
            "interlocksLWSCS": {
                "gisA7Active": False,
                "emergencyPushbuttonPressed": False,
                "lockingPinsNotRetracted": False,
                "upperPowerOffLsEngaged": False,
                "lowerPowerOffLsEngaged": False,
                "chainNotPresentLeftSide": False,
                "chainNotPresentRightSide": False,
            },
            "interlocksApSCS": {
                "gisA7Active": False,
                "gisA9Active": False,
                "emergencyPushbuttonPressed": False,
                "lockingPinsNotRetracted": False,
                "apsLowerGangwayHatchNotClosedOverrideNotActive": False,
                "apsTopExteriorLeftHatchNotClosedOverrideNotActive": False,
                "apsTopExteriorRightHatchNotClosedOverrideNotActive": False,
                "upperPhotocellInterrupted": False,
                "lowerPhotocellInterrupted": False,
            },
            "interlocksLCS": {
                "gisA9Active": False,
                "emergencyPushbuttonPressed": False,
            },
            "interlocksOBC": {
                "gisA8Active": False,
                "emergencyPushbuttonPressed": False,
            },
            "interlocksRAD": {
                "gisA10Active": False,
                "emergencyPushbuttonPressed": False,
                "lockingPinsNotRetracted": False,
                "driveOverspeed": False,
                "photocellInterrupted": False,
                "lightCurtainInterrupted": False,
            },
            "interlocksCSCS": {
                "driveOverspeed": False,
                "emergencyPushbuttonPressed": False,
            },
            "interlocksLockingPins": {
                "gisA9Active": False,
                "emergencyPushbuttonPressed": False,
                "azCenteringLsNotEngaged": False,
                "azDomeNotParked": False,
                "azPositionOutOfTolerance": False,
                "azNotInLocalEui": False,
                "apsFinalLsNotEngaged": False,
                "radFinalLsNotEngaged": False,
            },
            "sensorsFixedPartAlarms": {
                "accessPoint": False,
                "surgeArrester": False,
                "ethernetSwitch": False,
                "insulationMonitorTrip": False,
            },
            "sensorsFixedPartInflatableSeal": {
                "compressedAirLinePressureOk": False,
                "compressedAirTankPressureOk": False,
                "sealInflated": False,
                "sealDeflated": False,
            },
            "sensorsFixedPartLines24V": {
                "crioPilzValves": False,
                "motorsSolenoids": False,
                "drives": False,
                "thermal": False,
            },
            "sensorsFixedPartSelectors": {
                "remoteOn": False,
                "hmiEnable": False,
                "manualRotation": False,
            },
            "sensorsFixedPartValves": {
                "valve1AdbsCabinetValue": 0.0,
                "valve2AdbsCabinetValue": 0.0,
                "valveAdbsMotor1Value": 0.0,
                "valveAdbsMotor2Value": 0.0,
                "valveAdbsMotor3Value": 0.0,
                "valveAdbsMotor4Value": 0.0,
                "valveAdbsMotor5Value": 0.0,
            },
            "sensorsFixedPart": {
                "adbsLocalBoxEmergencyPushbutton": False,
                "iftpPdc1Doors": False,
                "adbsLoto": False,
                "brakes": False,
            },
            "sensorsRotatingPartLines24V": {
                "pilzHmi": False,
                "sensors": False,
                "niCards": False,
                "tmplPdc1": False,
                "tmplAc1Redundancy": False,
                "tmplPdc1Redundancy": False,
                "tmplPdc2Redundancy": False,
                "tmplPdc5Ups": False,
                "tmplPdc5Aux": False,
                "tmplPdc6Ups": False,
                "tmplPdc6Aux": False,
                "tmplPdc7Drives": False,
                "tmplPdc7Pushbuttons": False,
                "tmplPdc8Ups": False,
                "tmplPdc8Aux": False,
                "tmplPdc9Ups": False,
                "tmplPdc9Aux": False,
                "tmplPdc10Ups": False,
                "tmplPdc10Aux": False,
                "tmplPdc11Drives": False,
                "tmplPdc11Pushbuttons": False,
                "tmplPdc12Ups": False,
                "tmplPdc12Aux": False,
                "tmplPdc13Ups": False,
                "tmplPdc13Aux": False,
                "tmplPdc14Ups": False,
                "tmplPdc14Aux": False,
                "tmplPdc15Ups": False,
                "tmplPdc15Aux": False,
                "tmplPdc16Ups": False,
                "tmplPdc16Aux": False,
                "tmplPdc17Ups": False,
                "tmplPdc17Aux": False,
                "tmplPdc18Drives": False,
                "tmplPdc18Pushbuttons": False,
                "tmplPdc19Ups": False,
                "tmplPdc19Aux": False,
                "tmplPdc20Ups": False,
                "tmplPdc20Aux": False,
                "tmplPdc21Ups": False,
                "tmplPdc21Aux": False,
                "tmplPdc22Drives": False,
                "tmplPdc22Pushbuttons": False,
                "tmplPdc23Ups": False,
                "tmplPdc23Aux": False,
                "tmplPdc24Ups": False,
                "tmplPdc24Aux": False,
            },
            "sensorsRotatingPartLockingPins": {
                "azFault": False,
                "azRunning": False,
                "azTorque": False,
                "azEngaged": False,
                "azDisengaged": False,
                "azEnabled": False,
                "apsLp1RightFault": False,
                "apsLp1RightRunning": False,
                "apsLp1RightTorque": False,
                "apsLp1RightEngaged": False,
                "apsLp1RightDisengaged": False,
                "apsLp2RightFault": False,
                "apsLp2RightRunning": False,
                "apsLp2RightTorque": False,
                "apsLp2RightEngaged": False,
                "apsLp2RightDisengaged": False,
                "apsLp3RightFault": False,
                "apsLp3RightRunning": False,
                "apsLp3RightTorque": False,
                "apsLp3RightEngaged": False,
                "apsLp3RightDisengaged": False,
                "apsLp1LeftFault": False,
                "apsLp1LeftRunning": False,
                "apsLp1LeftTorque": False,
                "apsLp1LeftEngaged": False,
                "apsLp1LeftDisengaged": False,
                "apsLp2LeftFault": False,
                "apsLp2LeftRunning": False,
                "apsLp2LeftTorque": False,
                "apsLp2LeftEngaged": False,
                "apsLp2LeftDisengaged": False,
                "apsLp3LeftFault": False,
                "apsLp3LeftRunning": False,
                "apsLp3LeftTorque": False,
                "apsLp3LeftEngaged": False,
                "apsLp3LeftDisengaged": False,
                "apsCentralFault": False,
                "apsCentralRunning": False,
                "apsCentralTorque": False,
                "apsCentralEngaged": False,
                "apsCentralDisengaged": False,
                "apsEnabled": False,
                "lwsLp1LowRightEngaged": False,
                "lwsLp1LowRightDisengaged": False,
                "lwsLp2LowRightEngaged": False,
                "lwsLp2LowRightDisengaged": False,
                "lwsLp3LowRightEngaged": False,
                "lwsLp3LowRightDisengaged": False,
                "lwsLp1LowLeftEngaged": False,
                "lwsLp1LowLeftDisengaged": False,
                "lwsLp2LowLeftEngaged": False,
                "lwsLp2LowLeftDisengaged": False,
                "lwsLp3LowLeftEngaged": False,
                "lwsLp3LowLeftDisengaged": False,
                "lwsLp1UpRightEngaged": False,
                "lwsLp1UpRightDisengaged": False,
                "lwsLp2UpRightEngaged": False,
                "lwsLp2UpRightDisengaged": False,
                "lwsLp3UpRightEngaged": False,
                "lwsLp3UpRightDisengaged": False,
                "lwsLp1UpLeftEngaged": False,
                "lwsLp1UpLeftDisengaged": False,
                "lwsLp2UpLeftEngaged": False,
                "lwsLp2UpLeftDisengaged": False,
                "lwsLp3UpLeftEngaged": False,
                "lwsLp3UpLeftDisengaged": False,
                "radRightEngaged": False,
                "radRightDisengaged": False,
                "radLeftEngaged": False,
                "radLeftDisengaged": False,
            },
            "sensorsRotatingPartAlarms": {
                "accessPoint": False,
                "mainEthernetSwitch": False,
                "secondaryEthernetSwitch": False,
            },
            "sensorsRotatingPartDoorsClosed": {
                "tmplAc1": False,
                "tmplPdc1": False,
                "tmplPdc2": False,
                "tmplPdc3": False,
                "tmplPdc4": False,
                "tmplPdc5": False,
                "tmplPdc6": False,
                "tmplPdc7": False,
                "tmplPdc8": False,
                "tmplPdc9": False,
                "tmplPdc10": False,
                "tmplPdc11": False,
                "tmplPdc12": False,
                "tmplPdc13": False,
                "tmplPdc14": False,
                "tmplPdc15": False,
                "tmplPdc16": False,
                "tmplPdc17": False,
                "tmplPdc18": False,
                "tmplPdc19": False,
                "tmplPdc20": False,
                "tmplPdc21": False,
                "tmplPdc22": False,
                "tmplPdc23": False,
                "tmplPdc24": False,
            },
            "sensorsRotatingPartCabinetFan": {
                "tmplAc1": False,
                "tmplPdc1": False,
            },
            "sensorsRotatingPartLimitSwitches": {
                "azLpCentered": False,
                "apsRightPrelimitOpen": False,
                "apsRightPrelimitClosed": False,
                "apsLeftPrelimitOpen": False,
                "apsLeftPrelimitClosed": False,
                "apsRightUpOpenFinal": False,
                "apsRightUpClosedFinal": False,
                "apsRightLowOpenFinal": False,
                "apsRightLowClosedFinal": False,
                "apsLeftUpOpenFinal": False,
                "apsLeftUpClosedFinal": False,
                "apsLeftLowOpenFinal": False,
                "apsLeftLowClosedFinal": False,
                "lwsLowRightDirectional": False,
                "lwsUpLeftDirectional": False,
                "lwsLowLeftDirectional": False,
                "lwsUpPowerOff": False,
                "lwsLowPowerOff": False,
                "radClosed": False,
                "louverF1": False,
                "louverG1": False,
                "lightBafflesA1A2": False,
                "lightBafflesB1B2B3": False,
                "lightBafflesC1C2C3": False,
                "lightBafflesD3": False,
                "lightBafflesD1D2": False,
                "lightBafflesE1E2E3": False,
                "lightBafflesF1F2F3": False,
                "lightBafflesG1G2G3": False,
                "lightBafflesH1H2H3": False,
                "lightBafflesI1I2": False,
                "lightBafflesI3": False,
                "lightBafflesL1L2L3": False,
                "lightBafflesM1M2M3": False,
                "lightBafflesN1N2": False,
            },
            "sensorsRotatingPartSelectors": {
                "apsPushbuttonEnable": False,
                "hmiEnable": False,
                "lwsPushbuttonEnable": False,
                "llbvRadPushbuttonEnable": False,
                "llbvRadLouverSelected": 0,
                "llbvLocalBox1Enable": False,
                "llbvLocalBox1LouverSelected": 0,
                "llbvLocalBox2Enable": False,
                "llbvLocalBox2LouverSelected": 0,
                "llbvLocalBox3Enable": False,
                "llbvLocalBox3LouverSelected": 0,
                "llbvLocalBox4Enable": False,
                "llbvLocalBox4LouverSelected": 0,
                "llbvLocalBox5Enable": False,
                "llbvLocalBox5LouverSelected": 0,
                "llbvLocalBox6Enable": False,
                "llbvLocalBox6LouverSelected": 0,
                "tmplAc1LampControl": False,
            },
            "sensorsRotatingPartEmergencyPushbuttons": {
                "apsLowRight": False,
                "apsLowLeft": False,
                "apsUpRight": False,
                "apsUpLeft": False,
                "lwsRight": False,
                "lwsLeft": False,
                "tmplPdc1": False,
                "tmplAc1": False,
                "llbvLocalBox1": False,
                "llbvLocalBox2": False,
                "llbvLocalBox3": False,
                "llbvLocalBox4": False,
                "llbvLocalBox5": False,
                "llbvLocalBox6": False,
            },
            "sensorsRotatingPartPowerAvailable": {
                "sraTemporaryBypass": False,
                "aps": False,
                "lws": False,
                "obcFromTmplPdc1": False,
                "obcFromObcLocalBox": False,
                "obcFromTelescopePlatformOn": False,
            },
            "sensorsRotatingPartHatches": {
                "apsLowerGangway": False,
                "apsLowerGangwayOverride": False,
                "apsTopExteriorRight": False,
                "apsTopExteriorLeft": False,
                "apsTopExteriorOverride": False,
                "lowPlatformOverride": False,
                "upperPlatformOverride": False,
            },
            "sensorsRotatingPartPhotocells": {
                "apsLower": False,
                "apsUpper": False,
                "apsSwitchedOn": False,
                "rad": False,
            },
            "sensorsRotatingPartLightCurtain": {
                "rad": False,
            },
            "sensorsRotatingPartOBC": {
                "parked": False,
                "overrideActive": False,
                "smallCraneParked": False,
                "enabled": False,
            },
            "sensorsRotatingPartAxialFans": {
                "enabled": False,
            },
            "sensorsRotatingPartLights": {
                "middle": False,
                "high": False,
                "apsPlatform": False,
                "leftAccess": False,
                "rightAccess": False,
                "obc": False,
                "mdp": False,
                "overrideActive": False,
            },
            "sensorsRotatingPartHeatingCables": {
                "right": False,
                "rightCentral": False,
                "left": False,
            },
            "sensorsRotatingPartBrakes": {
                "apsLeft": False,
                "apsRight": False,
                "apsManualDisengage": False,
                "lws": False,
                "rad": False,
            },
        }
    )
