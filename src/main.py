import asyncio

from rb.core.richtext import rt
from rb.core.wifi import Wifi
from rb.core.store import store
from rb.dev.ahtx0 import new_soft_aht20
from rb.mqtt.manager import get_mqtt_creds
from clock import ClockScreen
from richy_air import RichyAirMQTT

rt.title('Saved settings:')
store.dump()

wifi = Wifi()
wifi.on()

sensor = new_soft_aht20(scl = 0, sda = 1)
clock = ClockScreen(sensor, wifi, scl = 3, sda = 2)

# Also report temp/humid to HomeAssistant if it is configured.
if get_mqtt_creds()[0] != None:
    air = RichyAirMQTT()
else:
    air = None
    wifi.off()


async def main():
    asyncio.create_task(clock.run())

    if air: 
        asyncio.create_task(air.run(sensor, wifi))
    
    # Keep the main loop alive
    while True:
        await asyncio.sleep(1)

# Run the event loop
asyncio.run(main())
