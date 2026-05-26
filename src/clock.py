import asyncio, time
from machine import Pin, I2C

from rb.core import ScreenContext
from rb.core.constants import MONTHS_3, DAYS
from rb.core.richtext import rt
from rb.core.store import store
from rb.core.tz import get_tz, local_secs
from rb.core.wifi import get_wifi_creds
from rb.dev.ssd1306 import SSD1306_I2C
from text import scaled_text


class ClockScreen:
    """
    Time/date display on an SSD1306 128*64 screen.
    """
    def __init__(self, th_sensor, wifi, scl = 3, sda = 2):
        """
        Note: This will create a hardware I2C device; if the microcontroller
        only has support for one hardware device be sure to use a software 
        one for the passed temperature sensor.
        """
        self.th = th_sensor
        self.wifi = wifi

        screen = I2C(0, scl = Pin(scl), sda = Pin(sda))
        self.fb = SSD1306_I2C(128, 64, screen, addr = 0x3C)        

        # Get current time via NTP.
        ssid, pw = get_wifi_creds()
        with ScreenContext(self.fb):
            self.fb.text('NTP Update...', 0, 0, 1)
            self.fb.text('Wifi SSID:', 0, 12, 1)
            self.fb.text(ssid, 0, 24, 1)

        wifi.ntp()

    def layout(self):
        # Air
        y = 0
        self.fb.text('Temp', 0, y, 1)
        self.fb.text(f'{"Humid":>16}', 0, y, 1)

        y += 11
        scaled_text(self.fb, f'{round(self.th.relative_humidity):>7}%', 0, y, 2, 1)
        scaled_text(self.fb, f'{round(self.th.temperature, 1):.1f}', 0, y, 2, 1)

        y += 20
        x = 128 - (16*3) - 13
        w = 9
        self.fb.rect(x, 0, w, y, 1, True)
        self.fb.rect(0, y, 128, 2, 1, True)
        self.fb.hline(x - 1, y - 2, w + 2, 1)
        self.fb.hline(x - 2, y - 1, w + 4, 1)
        y += 1 + 6

        # Time
        year, month, day, h, m, s, weekday, yearday = time.localtime(local_secs())
        tz, offset = get_tz()
        scaled_text(self.fb, f'{h:02d}:{m:02d}:{s:02d}', 0, y, 2, 1)

        y = self.fb.height - 8
        if s % 2:                    
            self.fb.text(f'{day:02d} {MONTHS_3[month - 1]}', 0, y, 1)
        else:
            self.fb.text(f'{DAYS[weekday]}', 0, y, 1)

        self.fb.text(tz, 128 - (8 * 3), y, 1)

    def refresh(self):
        with ScreenContext(self.fb):
            self.layout()

    async def run(self):
        """
        Run forever.
        """
        rt.info('ClockScreen running forever...')
        
        last_update = 0
        while True:
            now = int(time.time())
            if now != last_update:
                self.refresh()
                last_update = now

            await asyncio.sleep(1 / 100)
