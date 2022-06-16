from avilla.core.platform import Base
from avilla.core.selectors import mainline

avilla_platform_base = Base("GraiaProject@github", "avilla-protocol", "Avilla")
special_mainline = mainline.platform[avilla_platform_base].special[True]
