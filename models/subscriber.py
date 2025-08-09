from pydantic import BaseModel


class Subscriber(BaseModel):
    first_name: str
    phone_number: str
