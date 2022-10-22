"""The rpi_rf component."""
import rpi_rf
from typing import Protocol

def configure_custom_protocol():
    # Add a bunch of nonsense protocols
    # rpi_rf library has correct TX encoding hardcoded for Protocol 6 only
    rpi_rf.PROTOCOLS = (None,
        rpi_rf.rpi_rf.Protocol(100, 1,  1, 1, 1, 1, 1),
        rpi_rf.rpi_rf.Protocol(100, 1,  1, 1, 1, 1, 1),
        rpi_rf.rpi_rf.Protocol(100, 1,  1, 1, 1, 1, 1),
        rpi_rf.rpi_rf.Protocol(240, 1, 10, 1, 1, 1, 6),  # DIO TX prococol with active RX
        rpi_rf.rpi_rf.Protocol(270, 1, 10, 1, 1, 1, 5),  # DIO RX protocol
        rpi_rf.rpi_rf.Protocol(290, 1,  9, 1, 1, 1, 5))  # DIO TX only protocol
    rpi_rf.MAX_CHANGES = 256

configure_custom_protocol()