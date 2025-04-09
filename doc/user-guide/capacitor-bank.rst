.. _Capacitor_Bank:

################
Capacitor Bank
################

The capacitor bank provides the power to the dome motors to be able to reach the full performance.
If it is not connected or has an issue, the dome will only have the degraded performance.

.. _Capacitor_Bank_Status:

Capacitor Bank Status
=====================

The capacitor banks are on the level 6 interior pier.
The following figure is that they are on and charged:

.. figure:: ../screenshot/capacitor_bank_on_and_charged.jpg
  :width: 550

  Capacitor banks are on and charged.

The lever at the bottom left is used to control the on/off.
If they are off and charged, it would be:

.. figure:: ../screenshot/capacitor_bank_off_and_charged.jpg
  :width: 550

  Capacitor banks are off and charged.

If they are discharged, you will see the red light on the middle left off and green light on the top left on.

.. _Charge_Capacitor_Bank:

Charge Capacitor Bank
=====================

The charge/discharge of capacitor banks is managed directly by the active front end (AFE).
The low-level control of MTDome can only command the AFE to be enabled.
The enable phase will charge the capacitors automatically.
The AFE is commanded to enable when transitioning from **PARKED** or **STATIONARY** state due to a ``moveAz()`` or ``crawlAz()`` command from the clients.

If the DC bus voltage is below 690 V, the dome will not move.
It will begin to move after the voltages of capacitor banks are above 690 V.
The charging time is about 30 seconds - 1 minute.

If the capacitor banks are not connected and you move the dome with the full performance, the DC bus voltage will drop below a certain threshold set by Phase.
The AFE will go to fault and consequently the dome goes to fault as well.

That means if the capacitor banks connect to the DC bus and there is no system fault, it should charge itself automatically and there is no additional command from the control system that is required.
The EtherCAT connection error might discharge the capacitor banks and gives the AFE error at the meantime.
You can try to execute the ``exitFault()`` command first to see this would help or not.
In principle, the ``exitFault()`` command tries to restore the EtherCAT connectivity if it was lost, and so it should be sufficient.
Otherwise, you might need to restart the control system to recover the EtherCAT connection and then, the charge of capacitor bank.
