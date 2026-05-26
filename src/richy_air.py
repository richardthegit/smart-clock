import asyncio, time

from rb.core import Rebooter
from rb.core.richtext import rt
from rb.core.wifi import get_hostname
from rb.dev.ahtx0 import new_aht20
from rb.mqtt.config import mqtt_config, humidity, celcius, signal
from rb.mqtt.manager import MQTTManager


class RichyAirMQTT(MQTTManager):
    """
    Temperature and Humidity via Home Assistant.
    """
    def __init__(self):
        self.hostname = get_hostname('RichyAir')
        super().__init__(self.hostname)

        self.dev = {
            'identifiers': [self.hostname],
            'name': 'Richy Air',
            'model': 'ESP32 C3 Zero + AHT20',
            'manufacturer': 'Richy Corp',
        }

        self.c_topic = f'{self.hostname}/sensor/temp'
        self.h_topic = f'{self.hostname}/sensor/humidity'
        self.s_topic = f'{self.hostname}/sensor/signal'

    def connection_ready(self, has_session):
        rt.info('Publishing MQTT topics')

        self.config(f'homeassistant/sensor/{self.hostname}/temp/config',
                    celcius(mqtt_config(self.dev, 'Temperature', self.c_topic, f'{self.hostname}-temp')))

        self.config(f'homeassistant/sensor/{self.hostname}/humidity/config',
                    humidity(mqtt_config(self.dev, 'Relative Humidity', self.h_topic, f'{self.hostname}-humid')))

        self.config(f'homeassistant/sensor/{self.hostname}/signal/config',
                    signal(mqtt_config(self.dev, 'Wifi Signal', self.s_topic, f'{self.hostname}-signal')))

    async def run(self, sensor, wifi):
        rt.info('RichyAir running forever...')

        self.connect()

        while True:
            with Rebooter():
                # Note that we try not to hog the CPU for too long, hence we sleep 
                # between each publish.
                self.publish(self.c_topic, sensor.temperature)
                await asyncio.sleep(0)
                self.publish(self.h_topic, sensor.relative_humidity)
                await asyncio.sleep(0)
                self.publish(self.s_topic, wifi.signal_strength())
            
            await asyncio.sleep(10)
