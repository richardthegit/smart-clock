import asyncio, time
from machine import Pin, I2C

from rb.core import ScreenContext
from rb.core.constants import MONTHS_3, DAYS
from rb.core.richtext import rt
from rb.core.store import store
from rb.core.tz import get_tz, local_secs
from rb.core.wifi import get_wifi_creds
from rb.dev.ssd1306 import SSD1306_I2C

from fonts import (ezFBfont_helvR08_ascii_11, ezFBfont_helvB12_latin_20, 
                   ezFBfont_helvB18_latin_29, ezFBfont_helvB24_ascii_32)
from fonts.ezFBfont import ezFBfont


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
        self.big = store.get('big_clock', default = False)

        screen = I2C(0, scl = Pin(scl), sda = Pin(sda))
        self.fb = SSD1306_I2C(128, 64, screen, addr = 0x3C)

        self.font_md = ezFBfont(self.fb, ezFBfont_helvB12_latin_20)
        self.font_lg = ezFBfont(self.fb, ezFBfont_helvB18_latin_29)

        if self.big:
            self.font_xl = ezFBfont(self.fb, ezFBfont_helvB24_ascii_32)
        else:
            self.font_sm = ezFBfont(self.fb, ezFBfont_helvR08_ascii_11)

        # Get current time via NTP.
        ssid, pw = get_wifi_creds()
        with ScreenContext(self.fb):
            self.font_md.write(f'NTP Update...\nWifi SSID:\n{ssid}', 0, 0)

        wifi.ntp()

    def separator(self, x, y, w = 9, up = True):
        if up:
            h = self.fb.height - y
            self.fb.rect(x, 0, w, y, 1, True)
            self.fb.hline(x - 1, y - 2, w + 2, 1)
            self.fb.hline(x - 2, y - 1, w + 4, 1)
        else:
            self.fb.rect(x, y, w, self.fb.height - y, 1, True)
            self.fb.hline(x - 1, y + 2, w + 2, 1)
            self.fb.hline(x - 2, y + 1, w + 4, 1)

        self.fb.rect(0, y, 128, 2, 1, True)
        return y + 3

    def layout_detail(self):
        right = self.fb.width
        # Air
        y = 0
        self.font_md.write(f'{round(self.th.temperature, 1):.1f}°', 0, y)
        self.font_md.write(f'{round(self.th.relative_humidity)}%', right, y, halign = 'right')
        y += 23

        # Time
        year, month, day, h, m, s, weekday, yearday = time.localtime(local_secs())
        tz, offset = get_tz()
        self.font_lg.write(f'{h:02d}:{m:02d}:{s:02d}', 0, y - 3)
        self.font_sm.write(tz, right, y + 2, halign = 'right')

        self.separator(70, y - 2)
        self.separator(70, self.fb.height - 16, up = False) + 1

        y = self.fb.height
        self.font_sm.write(f'{DAYS[weekday]}', 0, y, valign = 'bottom')
        self.font_sm.write(f'{day} {MONTHS_3[month - 1]}', right, y, 
                           halign = 'right', valign = 'bottom')

    def layout_big(self):
        right = self.fb.width
        # Air
        y = 0
        self.font_lg.write(f'{round(self.th.temperature, 1):.1f}°', 0, y)
        self.font_lg.write(f'{round(self.th.relative_humidity)}%', right, y, halign = 'right')

        y = self.separator(62, y + 30)

        # Time
        year, month, day, h, m, s, weekday, yearday = time.localtime(local_secs())
        tz, offset = get_tz()
        self.font_xl.write(f'{h:02d}:{m:02d}', right / 2, y + 4, halign = 'center')

    def refresh(self):
        with ScreenContext(self.fb):
            if self.big:
                self.layout_big()
            else:
                self.layout_detail()

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


def config_clock():
    store.set('big_clock', input('Big clock? (y/N): ') == 'y')
