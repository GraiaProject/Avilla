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


class MessageEntityType(str, Enum):
    MENTION = "mention"
    HASH_TAG = "hashtag"
    CASHTAG = "cashtag"
    PHONE_NUMBER = "phone_number"
    BOT_COMMAND = "bot_command"
    URL = "url"
    EMAIL = "email"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    PRE = "pre"
    TEXT_LINK = "text_link"
    TEXT_MENTION = "text_mention"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    SPOILER = "spoiler"
    CUSTOM_EMOJI = "custom_emoji"
