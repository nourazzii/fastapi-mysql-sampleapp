import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime

from . import models


def get_user_by_id(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_blacklisted_ip(db: Session, remote_ip: str = 0):
    return (
        db.query(models.IPBlacklist).filter(models.IPBlacklist.ip == remote_ip).first()
    )


def get_blacklisted_ua(db: Session, user_agent: str):
    return (
        db.query(models.UABlacklist).filter(models.UABlacklist.ua == user_agent).first()
    )


def get_statistics_by_customer_by_day(db: Session, customer_id, date):
    return (
        db.query(
            func.sum(models.HourlyStats.request_count).label("request_count"),
            func.sum(models.HourlyStats.invalid_count).label("invalid_count"),
        )
        .filter(
            models.HourlyStats.customer_id == customer_id,
            func.year(models.HourlyStats.time) == date.year,
            func.month(models.HourlyStats.time) == date.month,
            func.day(models.HourlyStats.time) == date.day,
        )
        .group_by(
            func.year(models.HourlyStats.time),
            func.month(models.HourlyStats.time),
            func.day(models.HourlyStats.time),
            models.HourlyStats.customer_id,
        )
        .all()
    )


def get_statistics_by_day(db: Session, date):
    return (
        db.query(
            func.sum(models.HourlyStats.request_count).label("request_count")
            + func.sum(models.HourlyStats.invalid_count).label("invalid_count")
        )
        .filter(
            func.year(models.HourlyStats.time) == date.year,
            func.month(models.HourlyStats.time) == date.month,
            func.day(models.HourlyStats.time) == date.day,
        )
        .group_by(
            func.year(models.HourlyStats.time),
            func.month(models.HourlyStats.time),
            func.day(models.HourlyStats.time),
        )
        .all()
    )


def update_user_requests_stats(
    db: Session, customer_id, request_time, is_valid_request
):
    is_valid_request = "true" if is_valid_request else "false"
    sql_query = sqlalchemy.text(
        "call update_hourly_stats({}, '{}', {});".format(
            customer_id, request_time, is_valid_request
        )
    )
    db.execute(sql_query)
    db.commit()
