class Element:
    def asDisplay(self) -> str:
        return ""

    @classmethod
    def get_ability_id(cls) -> str:
        return f"msg_element::{cls.__name__}"
