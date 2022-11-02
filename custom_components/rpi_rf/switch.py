"""Support for a switch using a 433MHz module via GPIO on a Raspberry Pi."""
from __future__ import annotations

import os
import stat
import logging
import subprocess
from threading import RLock

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIQUE_ID,
    CONF_SWITCHES,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

REMOTE_ID = "remote_id"
SWITCH_ID = "switch_id"
CONF_GPIO = "gpio"
CONF_SIGNAL_REPETITIONS = "signal_repetitions"

DEFAULT_SIGNAL_REPETITIONS = 1

SWITCH_SCHEMA = vol.Schema(
    {
        vol.Required(REMOTE_ID): cv.positive_int,
        vol.Required(SWITCH_ID): cv.positive_int,
        vol.Optional(CONF_SIGNAL_REPETITIONS, default=DEFAULT_SIGNAL_REPETITIONS): cv.positive_int,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_GPIO): cv.positive_int,
        vol.Required(CONF_SWITCHES): vol.Schema({cv.string: SWITCH_SCHEMA}),
    }
)

WIRING_PI_GPIO = {
    17: 0,      18: 1,
    27: 2,
    22: 3,      23: 4,
                24: 5,
                26: 6
}

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Find and return switches controlled by a generic RF device via GPIO."""
    gpio = config[CONF_GPIO]
    rfdevice_lock = RLock()
    switches = config[CONF_SWITCHES]

    devices = []
    for dev_name, properties in switches.items():
        devices.append(
            ChaconSwitch(
                properties.get(CONF_NAME, dev_name),
                properties.get(CONF_UNIQUE_ID),
                gpio,
                rfdevice_lock,
                properties.get(REMOTE_ID),
                properties.get(SWITCH_ID),
                properties.get(CONF_SIGNAL_REPETITIONS)
            )
        )

    add_entities(devices)


class ChaconSwitch(SwitchEntity):
    """Representation of a GPIO RF switch."""

    def __init__(
        self,
        name,
        unique_id,
        gpio,
        lock,
        remote_id,
        switch_id,
        signal_repetitions,
    ):
        """Initialize the switch."""
        self._name = name
        self._attr_unique_id = unique_id if unique_id else "{}_{}".format(remote_id, switch_id)
        self._state = False
        self._gpio = WIRING_PI_GPIO[gpio]
        self._lock = lock
        self._remote_id = remote_id
        self._switch_id = switch_id
        self._tx_repeat = signal_repetitions

        chacon_path = os.path.realpath(os.path.dirname(__file__))
        self._chacon_env = os.environ.copy()
        try:
            self._chacon_env["LD_LIBRARY_PATH"] = f'{chacon_path}:' + self._chacon_env["LD_LIBRARY_PATH"]
        except KeyError:
            self._chacon_env["LD_LIBRARY_PATH"] = chacon_path

        self._chacon_send = os.path.join(chacon_path, "chacon_send")
        st = os.stat(self._chacon_send)
        os.chmod(self._chacon_send, st.st_mode | stat.S_IEXEC)

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.info(" ".join([self._chacon_send, f'{self._gpio}', f'{self._remote_id}', f'{self._switch_id}', "off", f'{self._tx_repeat}']))
        output = subprocess.run([self._chacon_send, f'{self._gpio}', f'{self._remote_id}', f'{self._switch_id}', "on", f'{self._tx_repeat}'],
                                env=self._chacon_env, capture_output=True)
        _LOGGER.info(output.stdout)
        if output.returncode == 0:
            self._state = True
            self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        _LOGGER.info(" ".join([self._chacon_send, f'{self._gpio}', f'{self._remote_id}', f'{self._switch_id}', "off", f'{self._tx_repeat}']))
        output = subprocess.run([self._chacon_send, f'{self._gpio}', f'{self._remote_id}', f'{self._switch_id}', "off", f'{self._tx_repeat}'],
                                env=self._chacon_env, capture_output=True)
        _LOGGER.info(output.stdout)
        if output.returncode == 0:
            self._state = False
            self.schedule_update_ha_state()
