import math
import uasyncio

# コールチンクラス
class CoroutineDistanceSensor:
    def __init__(self, distance_sensor, event):
        self.__distance_sensor = distance_sensor
        self.__event = event
        self.__distance = -1

    @property
    def distance(self):
        return self.__distance

    async def run(self):
        try:
            while True:
                await self.__done()
        finally:
            print("CoroutineDistanceSensor end!")

    async def __done(self):
        self.__distance = self.__distance_sensor.get_distance_cm()
        await uasyncio.sleep_ms(1)
        if self.__distance and self.__distance < 15:
            print("The wall is near!")
            self.__event.set()
            await uasyncio.sleep_ms(1)

if __file__.split('/')[3] == '__init__.mpy':
    print(__file__)
