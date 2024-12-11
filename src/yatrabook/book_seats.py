from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

ROWS = 12  # 11 rows with 7 seats + 1 row with 3 seats
SEATS_PER_ROW = [7] * 11 + [3]
seats = [[0 for _ in range(row)] for row in SEATS_PER_ROW]  # 0: available, 1: booked


class BookingRequest(BaseModel):
    seats_required: int


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    '''Renders HTML content'''
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/seats")
def get_seats():
    """Returns the current seating arrangement."""
    return {"seats": seats}


@app.post("/book")
def book_seats(request: BookingRequest):
    """Books the requested number of seats."""
    if request.seats_required < 1 or request.seats_required > 7:
        raise HTTPException(status_code=400, detail="You can book between 1 and 7 seats.")

    seats_required = request.seats_required
    for i, row in enumerate(seats):
        # Check if seats can fit in one row
        if row.count(0) >= seats_required:
            booked_seats = []
            for j in range(len(row)):
                if seats_required == 0:
                    break
                if row[j] == 0:
                    row[j] = 1
                    booked_seats.append(f"R{i+1}S{j+1}")
                    seats_required -= 1
            return {"message": "Seats booked successfully!", "booked_seats": booked_seats, "seats": seats}

    # If no single row has enough seats, find the closest seats
    booked_seats = []
    for i, row in enumerate(seats):
        for j in range(len(row)):
            if seats_required == 0:
                return {"message": "Seats booked successfully!", "booked_seats": booked_seats, "seats": seats}
            if row[j] == 0:
                row[j] = 1
                booked_seats.append(f"R{i+1}S{j+1}")
                seats_required -= 1

    raise HTTPException(status_code=400, detail="Not enough seats available.")
