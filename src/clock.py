import time
from machine import Pin, I2C

from rb.core import ScreenContext
from rb.core.store import store
from rb.core.time import get_tz
from rb.core.wifi import WifiManager, get_wifi_creds
from rb.dev.ahtx0 import new_soft_aht20
from rb.dev.ssd1306 import SSD1306_I2C
from text import scaled_text

class ClockScreen:
    """
    Time/date display on an SSD1306 128*64 screen.
    """
    def __init__(self, sda_pin = 2, scl_pin = 3):
        screen = I2C(0, sda = Pin(sda_pin), scl = Pin(scl_pin))
        self.fb = SSD1306_I2C(128, 64, screen, addr = 0x3C)
        self.th = new_soft_aht20(scl = 0, sda = 1)

        ssid, pw = get_wifi_creds()
        with ScreenContext(self.fb):
            self.fb.text('NTP Update...', 0, 0, 1)
            self.fb.text('Wifi SSID:', 0, 12, 1)
            self.fb.text(ssid, 0, 24, 1)

        with WifiManager() as wm:
            wm.wifi.ntp()

    def refresh(self):
        with ScreenContext(self.fb):
            # Time
            year, month, day, h, m, s, weekday, yearday = time.localtime(time.time())
            y = 4
            self.fb.text(f'{year:04d}-{month:02d}-{day:02d}'.center(16), 0, y, 1)
            y += 8 + 4
            self.fb.hline(0, y, 128, 1)
            y += 1 + 4
            scaled_text(self.fb, f'{h:02d}:{m:02d}:{s:02d}', 0, y, 2, 1)
            y += 16 + 4
            self.fb.hline(0, y, 128, 1)

            y += 1 + 4
            self.fb.text('Temp', 0, y, 1)
            self.fb.text(f'{"R/H%":>16}', 0, y, 1)

            tz, offset = get_tz()
            self.fb.text(tz, int((128 - (8*3)) / 2), y, 1)
            
            y += 8 + 2
            self.fb.text(f'{self.th.temperature:.1f}', 0, y, 1)
            self.fb.text(f'{self.th.relative_humidity:>16.1f}', 0, y, 1)

    def run(self):
        while True:
            self.refresh()
            time.sleep(1)