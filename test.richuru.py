from richuru1 import install

install()


from loguru import logger

logger.opt(colors=True).info("<red>Hello <blue>world!</blue></red>")