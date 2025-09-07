from pydantic import BaseModel


class Config(BaseModel):
    coyote_time: int = 25


config = Config()
