from typing import Any
from pydantic import BaseModel
from avilla.core import Avilla
from avilla.core.config import ConfigApplicant, ConfigFlushingMoment
from avilla.core.utilles.mock import ConfigMock


class TestConfig(BaseModel):
    test_field1: str
    test_field2: int
    field3: float
    field4: bool
    field5: Any


class TestApplicant(ConfigApplicant["TestConfig"]):
    init_moment = {TestConfig: ConfigFlushingMoment.before_prepare}
    config_model = TestConfig


cm = ConfigMock(
    {
        TestApplicant: TestConfig(
            test_field1="test_field1", test_field2=1, field3=1.1, field4=True, field5=None
        )
    }
)

print(cm.get_config(Avilla))
print(cm.get_config(TestApplicant))
