from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math
import json
import os
import uasyncio

# メモリ情報の出力
def print_mem_info():
    import gc
    import micropython
    print('-----------------------------')
    stat = os.statvfs('/')
    total_size = stat[0] * stat[2]
    free_size = stat[0] * stat[4]
    print('each block is {} bytes big'.format(stat[0]))
    print("in bytes, that's {} bytes free out of a total of {}".format(free_size, total_size))
    print('-----------------------------')
    gc.collect()
    micropython.mem_info()
    print('-----------------------------')
    print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
    print('-----------------------------')
    print(os.listdir('projects/{}'.format(cp.getID(0))))
    print('-----------------------------')

# 別スロットからのimport用コピー
class CopyProject:
    def __init__(self):
        f = open('projects/.slots', 'r')
        data = f.read()
        f.close()
        self.slots = json.loads(data.replace('\'', '"'))

    def getID(self, no):
        return self.slots[no]['id']

    def copy(self, no_from, no_to, name):
        from_path = 'projects/{}/__init__.mpy'.format(self.slots[no_from]['id'])
        to_path = 'projects/{}/{}.mpy'.format(self.slots[no_to]['id'], name)
        f = open(from_path, 'rb')
        data = f.read()
        f.close()
        f = open(to_path, 'wb')
        f.write(data)
        f.close()

cp = CopyProject()
cp.copy(1, 0, 'lib1')
cp.copy(2, 0, 'lib2')

from .lib1 import State, StateMachine, GoStraight
from .lib2 import CoroutineDistanceSensor

# オブジェクトの定義
app = App()
hub = MSHub()
wheels = MotorPair(MSHub.PORT_B, MSHub.PORT_A)
arm = Motor(MSHub.PORT_C)
distance_sensor = DistanceSensor(MSHub.PORT_D)
color_sensor = ColorSensor(MSHub.PORT_E)

# ステートの定義
STATE_EXIT = "exit"
STATE_GO_STRAIGHT = "GoStraight"

# メイン処理
class Main:
    def __init__(self):
        self.__stateMachine = StateMachine()
        self.__stateMachine.add(State(STATE_EXIT)) # プログラム終了ステート
        self.setup()
        uasyncio.run(self.run())

    def setup(self):
        # イベントの生成
        self.__eventNearBy = uasyncio.Event()
        # コールチンの登録
        self.__coroutines = []
        self.__coroutines.append(CoroutineDistanceSensor(distance_sensor, self.__eventNearBy))        
        # ステートの登録
        self.__stateMachine.add(GoStraight(STATE_GO_STRAIGHT, wheels))
        # 開始ステートへ切り替える
        self.__stateMachine.changeTo(STATE_GO_STRAIGHT)
        
    async def run(self):
        self.__tasks = []
        for c in self.__coroutines:
            self.__tasks.append(uasyncio.create_task(c.run()))
        while self.__stateMachine.currentState != STATE_EXIT:
            nextState = self.__stateMachine.run()
            await uasyncio.sleep_ms(1)
            if nextState:
                self.__stateMachine.changeTo(nextState)
            # イベントによるステート変更
            if self.__eventNearBy.is_set():
                self.__stateMachine.changeTo(STATE_EXIT)
            # 外部よりの終了指示
            if hub.right_button.is_pressed():
                print("right button is pressed !")
                self.__stateMachine.changeTo(STATE_EXIT)
            await uasyncio.sleep_ms(1)
        # 全てのコールチンを終了させる
        for task in self.__tasks:
            task.cancel()
        await uasyncio.sleep_ms(30)

if __file__.split('/')[3] == '__init__.mpy':
    print_mem_info()
    # プログラム開始指示を待つ
    hub.left_button.wait_until_pressed()
    hub.speaker.beep()
    # プログラム開始
    Main()
    # プログラム終了（メニューに戻る）
    raise SystemExit
