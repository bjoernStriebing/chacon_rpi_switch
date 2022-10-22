import time
import logging

from . import rpi_rf

_LOGGER = logging.getLogger(__name__)


class RFDevice(rpi_rf.RFDevice):
    def rx_callback(self, gpio):
        """RX callback for GPIO event detection. Handle basic signal detection."""
        timestamp = int(time.perf_counter() * 1000000)
        duration = timestamp - self._rx_last_timestamp

        if duration > 2000:
            for pnum in range(1, len(rpi_rf.rpi_rf.PROTOCOLS)):
                if self._rx_waveform(pnum, self._rx_change_count, timestamp):
                    if ('0000' not in str(f'{self.rx_code:b}')) and (len(str(f'{self.rx_code:b}')) > 32):
                        _LOGGER.debug(f'RX protocol {pnum}, pluselength {self.rx_pulselength}, code {self.rx_code:b}, {self.rx_code:x}')
                        _LOGGER.debug(f'RX decode {self._rx_timings}')
            self._rx_timings = [0] * (rpi_rf.rpi_rf.MAX_CHANGES + 1)
            self._rx_change_count = 0

        if self._rx_change_count >= rpi_rf.rpi_rf.MAX_CHANGES:
            self._rx_timings = [0] * (rpi_rf.rpi_rf.MAX_CHANGES + 1)
            self._rx_change_count = 0
        self._rx_timings[self._rx_change_count] = duration
        self._rx_change_count += 1
        self._rx_last_timestamp = timestamp

    def _rx_waveform(self, pnum, change_count, timestamp):
        if self._rx_change_count > 48:
            return super(RFDevice, self)._rx_waveform(pnum, change_count, timestamp)
        return False

    def tx_code(self, code, tx_proto=None, tx_pulselength=None, tx_length=None):
        """
        Send a decimal code.
        Optionally set protocol, pulselength and code length.
        """
        if tx_proto:
            self.tx_proto = tx_proto
        else:
            self.tx_proto = 1
        if tx_pulselength:
            self.tx_pulselength = tx_pulselength
        elif not self.tx_pulselength:
            self.tx_pulselength = rpi_rf.rpi_rf.PROTOCOLS[self.tx_proto].pulselength
        if tx_length:
            self.tx_length = tx_length
        elif (code > 16777216):
            self.tx_length = 32
        else:
            self.tx_length = 24
        rawcode = format(code, '0{}b'.format(self.tx_length))
        nexacode = ""
        for b in rawcode:
            if b == '0':
                nexacode = nexacode + "01"
            if b == '1':
                nexacode = nexacode + "10"
        rawcode = f'1{nexacode}'
        self.tx_length = len(rawcode)
        _LOGGER.debug(f'TX code: {code}, (len {len(rawcode)})')
        return self.tx_bin(rawcode)

    def tx_bin(self, rawcode):
        """Send a binary code."""
        _LOGGER.debug("TX bin: " + str(rawcode))
        for _ in range(0, self.tx_repeat):
            if not self.tx_sync():
                return False
            for byte in range(0, self.tx_length):
                if rawcode[byte] == '0':
                    if not self.tx_l0():
                        return False
                else:
                    if not self.tx_l1():
                        return False
            if not self.tx_sync():
                return False
        return True

    def tx_sync(self):
        """Send a sync."""
        if not 0 < self.tx_proto < len(rpi_rf.rpi_rf.PROTOCOLS):
            _LOGGER.error("Unknown TX protocol")
            return False
        sync = self.tx_waveform(rpi_rf.rpi_rf.PROTOCOLS[self.tx_proto].sync_high,
                                rpi_rf.rpi_rf.PROTOCOLS[self.tx_proto].sync_low)
        sync &= self.tx_waveform(rpi_rf.rpi_rf.PROTOCOLS[self.tx_proto].sync_high,
                                rpi_rf.rpi_rf.PROTOCOLS[self.tx_proto].sync_high)
        return sync