# Home Assistant Raspberry Pi Chacon RF switch custom integration

**This is a HA wrapper for Quentin Comte-Gaz's jarvis-chacon. DIO (Chacon) 433MHz emitter.**

## About
For this DIO Chacon emitters this is a replacement for Mark Breen's HA RPi RF integration for Chacon remote integration. This cirumnavigates the timing issues in rpi_rf when running on HASS OS.

[chacon_send](https://github.com/QuentinCG/jarvis-chacon)
[ha-rpi-rf](https://github.com/markvader/ha-rpi_rf)

Interoperable with codes sniffed via [the rpi-rf module](https://pypi.python.org/pypi/rpi-rf) or [rc-switch](https://github.com/sui77/rc-switch).
For more info see the PyPi module description: [rpi-rf](https://pypi.python.org/pypi/rpi-rf).

# Installation

### HACS

The recommended way to install `chacon_rpi_switch` is through [HACS](https://hacs.xyz/).

### Manual installation

Copy the `chacon_rpi_switch` folder and all of its contents into your Home Assistant's `custom_components` folder. This folder is usually inside your `/config` folder. If you are running Hass.io, use SAMBA to copy the folder over. You may need to create the `custom_components` folder and then copy the `rpi_rf` folder and all of its contents into it.

## Configuration

To enable, add the following to your `configuration.yaml`:

```yaml
# Example configuration.yaml entry
switch:
  - platform: chacon_rpi_switch
    gpio: 17
    switches:
      switch_1:
        unique_id: "unique device name"
        remote_id: 12345678
        switch_id: 0
      switch_2:
        remote_id: 12345678
        switch_id: 6
        signal_repetitions: 3
```

### Options

| Key                  | Required | Default | Type    | Description                                                                                                                   |
| -------------------- | -------- | ------- | ------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `gpio`               | yes      |         | integer | GPIO to which the data line of the TX module is connected.            |
| `switches`           | yes      |         | list    | The array that contains all switches.                                 |
| `entry`              | yes      |         | list    | Name of the switch. Multiple entries are possible.                    |
| `remote_id`          | yes      |         | integer | Decimal code representing the emulated transmitter ID.                |
| `switch_id`          | yes      |         | list    | Decimal code identifying the addressed switch (groups not supported). |
| `signal_repetitions` | no       |  `10`   | integer | Number of times to repeat transmission.                               |
| `unique_id`          | no       |         | string  | A Unique ID to set for a switch entity e.g "my aircon switch",        |
|                      |          |         |         | if not set one will be generated based on remote_id & switch_id.      |
|                      |          |         |         | Once set, it is unadvisable to change this, see note below.           |



## Sniffed Codes
If using codes sniffed with rpi-rf the switch_id and remote_id can be extraced using the following bitmask:
```
    switch_id = code & 0xF
    remote_id = code >> 6
```

## Background Info
http://blog.idleman.fr/raspberry-pi-10-commander-le-raspberry-pi-par-radio/


**An important note on unique ID's.**
- If not set manually in the configuration file, the unique_id for each entity is generated from the code_on & code_off values.
- Should you change the code_on or code_off values in the future and/or add additional code(s) to a code sequence, the unique_id will be regenerated and Home Assistant will recognise a new entity.
- Should you change the unique_id value in the configuration in the future, Home Assistant will recognise a new entity.
- It is safe to remove the old entity (It will show as "restored" in the list of entities).
- The old entity and its customisation (icon, area etc) will be lost and you will need to re-enter these customisations for the new entity.

- Additionally, you will be unable to have two entities with identical code_on & code_off values (not sure thats ever likely to happen as if you had more than one device in a home with the same RF codes as it would be impossible to control a single device.)
