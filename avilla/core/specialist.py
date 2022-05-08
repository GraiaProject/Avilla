from .platform import Base
from .selectors import entity, mainline

special_platform = Base("GraiaProject@github", "avilla-protocol", "Avilla")
special_mainline = mainline.platform[special_platform].special[True]
guest = entity.mainline[special_mainline].guest[True]

