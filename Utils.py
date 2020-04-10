# https://git.botox.bz/CSSZombieEscape/Torchlight3/src/branch/master/Torchlight/Utils.py
import math


class DataHolder:
    def __init__(self, value=None, attr_name='value'):
        self._attr_name = attr_name
        self.set(value)

    def __call__(self, value):
        return self.set(value)

    def set(self, value):
        setattr(self, self._attr_name, value)
        return value

    def get(self):
        return getattr(self, self._attr_name)


class Utils():
    @staticmethod
    def GetNum(Text):
        Ret = ''
        for c in Text:
            if c.isdigit():
                Ret += c
            elif Ret:
                break
            elif c == '-':
                Ret += c
        return Ret

    @staticmethod
    def ParseTime(TimeStr):
        Negative = False
        Time = 0

        while TimeStr:
            Val = Utils.GetNum(TimeStr)
            if not Val:
                break

            Val = int(Val)
            if not Val:
                break

            if Val < 0:
                TimeStr = TimeStr[1:]
                if Time == 0:
                    Negative = True
            Val = abs(Val)

            ValLen = int(math.log10(Val)) + 1
            if len(TimeStr) > ValLen:
                Mult = TimeStr[ValLen].lower()
                TimeStr = TimeStr[ValLen + 1:]
                if Mult == 'h':
                    Val *= 3600
                elif Mult == 'm':
                    Val *= 60
            else:
                TimeStr = None

            Time += Val

        if Negative:
            return -Time
        else:
            return Time
