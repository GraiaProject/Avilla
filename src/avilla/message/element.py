from pydantic import BaseModel  # pylint: ignore


class Element(BaseModel):
    def asDisplay(self) -> str:
        return ""
