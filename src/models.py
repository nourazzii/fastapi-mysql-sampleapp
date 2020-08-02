from sqlalchemy import Column, UniqueConstraint, Integer, SMALLINT, BigInteger, VARCHAR

from .database import Base


class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR)
    active = Column(SMALLINT, default=True)


class IPBlacklist(Base):
    __tablename__ = "ip_blacklist"

    ip = Column(Integer, primary_key=True, index=True)


class UABlacklist(Base):
    __tablename__ = "ua_blacklist"

    ua = Column(VARCHAR, primary_key=True, index=True)


class HourlyStats(Base):
    __tablename__ = "hourly_stats"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer)
    time = Column(VARCHAR)
    request_count = Column(BigInteger, default=True)
    invalid_count = Column(BigInteger, default=True)

    UniqueConstraint(customer_id, time)
