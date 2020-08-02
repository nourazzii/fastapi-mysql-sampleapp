import time
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Header

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app: FastAPI = FastAPI(
    title="API to process user requests",
    description="<b>API for processing user requests and gathering stats per user.</b>",
    docs_url="/",
    version="0.1.0",
)


def get_db():
    """Create the DB connector

    Yields
    -------
    Session
        DB Session to be used to connect to MySQL
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def process_valid_request(request):
    """Process the request if it is valid

    Parameters
    ----------
    request : str
        A JSON object received by our collector
    """
    # stub function
    pass


@app.post("/api/v1/process", tags=["Processing"])
def process(
    request: schemas.Request,
    user_agent: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Process the request send by our collector.\\
    This endpoint expects a specific json object, it will fail if provided with a malformed JSON\\
    or an unvalid request (missing one or more fields)

    Returns
    -------
    dict\\
        A Python dict / JSON response with the relevant information

    Raises
    ------
    HTTPException \\
        401 if customer is disabled \\
        403 if blacklisted IP or User-Agent \\
        404 if the customer is not found \\
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    """
    customer_id = request.customerID
    timestamp = datetime.fromtimestamp(request.timestamp // 1000).replace(
        minute=0, second=0
    )
    valid_request = True

    customer = crud.get_user_by_id(db, customer_id=request.customerID)
    blacklisted_ip = crud.get_blacklisted_ip(db, remote_ip=request.remoteIP)
    blacklisted_ua = crud.get_blacklisted_ua(db, user_agent=user_agent)

    status_code = 200
    message = "Request was processed"

    # If the customer is not found in the DB
    if not customer:
        # We consider customer 1 as the 'sink' for all bad customer_ids
        customer_id = 1
        valid_request = False
        status_code = 404
        message = "Customer not found"
    # If the customer is found but is disabled
    elif not customer.active:
        valid_request = False
        status_code = 401
        message = "Not active customer"
    # If we receive a request from a blacklisted ip
    elif blacklisted_ip:
        valid_request = False
        status_code = 403
        message = "Remote IP is blocked"
    # If it is a blacklisted user-agent (sometimes a bot)
    elif blacklisted_ua:
        valid_request = False
        status_code = 403
        message = "User Agent is blocked"

    crud.update_user_requests_stats(db, customer_id, timestamp, valid_request)

    if not valid_request:
        raise HTTPException(status_code=status_code, detail=message)

    process_valid_request(request)

    return {"success": True, "message": message, "data": {}}


@app.get("/api/v1/stats", tags=["Statistics"])
def get_statistics(customer_id: int, date: str, db: Session = Depends(get_db)):
    """
    Endpoint to get the statistics for a specific customer and a specific day. \\
    The response also contains the total number of requests for that day.
    
    Parameters
    ----------
    customer_id : int\\
        A valid customer id\\
    date : str\\
        A date for which we need the stats\\
        Format has to be  day/month/year\\
        (ex: 02/08/2020)

    Returns
    -------
    dict
        Returns a json object of the form
        {
            "success": True,
            "message": "Returning User Stats",
            "data":{
                "customer":{
                    "id": customer_id,
                    "valid_requests_count": 0,
                    "invalid_requests_count": 0
                }            
                "daily_total_all_customers": 0
            }
        }
    """
    try:
        date_timestamp = time.mktime(datetime.strptime(date, "%d/%m/%Y").timetuple())
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Validation Error: Date should be in the format day/month/year. ex: 02/08/2020",
        )
    # Replace minutes and seconds with 0 to save requests of a specific hour together
    time_in_db = datetime.fromtimestamp(date_timestamp).replace(minute=0, second=0)
    # Get all requests done by a specific customer on a specific day
    statistics_customer_day = crud.get_statistics_by_customer_by_day(
        db, customer_id, time_in_db
    )
    # Get all requests of all customers for that day
    statistics_day = crud.get_statistics_by_day(db, time_in_db)
    response = {
        "success": True,
        "message": "Returning User Stats",
        "data": {
            "customer": {
                "id": customer_id,
                "valid_requests_count": 0,
                "invalid_requests_count": 0,
            },
            "daily_total_all_customers": 0,
        },
    }
    print(statistics_customer_day)
    if statistics_customer_day:
        response["data"]["customer"]["valid_requests_count"] = statistics_customer_day[
            0
        ][0]
        response["data"]["customer"][
            "invalid_requests_count"
        ] = statistics_customer_day[0][1]

    if statistics_day:
        response["data"]["daily_total_all_customers"] = statistics_day[0][0]

    return response
