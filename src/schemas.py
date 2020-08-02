from pydantic import BaseModel, validator


class Customer(BaseModel):
    id: int
    active: int


class IPBlacklist(BaseModel):
    ip: str


class UABlacklist(BaseModel):
    ua: str


class Request(BaseModel):
    customerID: int
    tagID: int
    userID: str
    remoteIP: str
    timestamp: int

    @validator("customerID")
    def id_must_be_positive(cls, v):
        if v <= 1:
            raise ValueError("Customer id must be positive")
        return v
    
    @validator("timestamp")
    def timestamp_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Timestamp must be positive [after 1970-01-01")
        return v


class HourlyStats(BaseModel):
    customer_id: int
    time: int
    is_valid_request: bool
