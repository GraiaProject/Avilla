from enum import Enum


class DiceEmoji(str, Enum):
    DICE = "Dice"
    """ 🎲 """

    DARTS = "Darts"
    """ 🎯 """

    BASKETBALL = "Basketball"
    """ 🏀 """

    FOOTBALL = "Football"
    """ ⚽ """

    SLOT_MACHINE = "SlotMachine"
    """ 🎰 """

    BOWLING = "Bowling"
    """ 🎳 """


class DiceLimit(int, Enum):
    MIN_VALUE = 1
    MAX_VALUE_DICE = 6
    MAX_VALUE_DARTS = 6
    MAX_VALUE_BASKETBALL = 5
    MAX_VALUE_FOOTBALL = 5
    MAX_VALUE_SLOT_MACHINE = 64
    MAX_VALUE_BOWLING = 6
