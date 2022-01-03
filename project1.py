# ステートクラス（基底クラス）
class State(object):
    def __init__(self, name: String):
        self.__name = name
        self.__action = None

    @property
    def name(self):
        return self.__name

    def entry(self):
        pass

    def do(self) -> String:
        return None

    def exit(self):
        pass

# ステートマシンクラス
class StateMachine(object):
    def __init__(self):
        self.__stateList = {}
        self.__now = None

    @property
    def currentState(self):
        return self.__now.name if self.__now else ""

    def add(self, state: State):
        self.__stateList[state.name] = state

    def changeTo(self, tag: String):
        if self.__now:
            self.__now.exit()
        self.__now = self.__stateList[tag]
        if self.__now:
            self.__now.entry()

    def run(self) -> String:
        if self.__now:
            return self.__now.do()
        return None

# 直進
class GoStraight(State):
    def __init__(self, name: String, wheels):
        super().__init__(name)
        self.__wheels = wheels

    def entry(self):
        self.__wheels.start(0, -20)

    def exit(self):
        self.__wheels.stop()

if __file__.split('/')[3] == '__init__.mpy':
    print(__file__)
