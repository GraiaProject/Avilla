from .selectors import entity, mainline
from .platform import Base

special_platform = Base("GraiaProject@github", "avilla-protocol", "Avilla")
special_mainline = mainline.platform[special_platform].special[True]
guest = entity.mainline[special_mainline].guest[True]

