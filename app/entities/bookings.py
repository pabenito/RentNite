# Import libraries
import re
from datetime import date, datetime, time
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, HTTPException, status
from pymongo.collection import Collection

from app.database import db
from .models import *

from ..entities import houses as houses_api
#from ..entities import users as users_api

# Create router
router = APIRouter()

# Initialize DB
bookings: Collection = db["bookings"]
houses: Collection = db["houses"]
users: Collection = db["users"]

# Save possible states for later
states = ["Accepted", "Declined", "Requested", "Cancelled"]

#Constants
RNE = "Reserva no encontrada."

# API
@router.get("/")
def get():
    bookings_list = list(bookings.find())
    result = []

    for b in bookings_list:
        result.append(Booking.parse_obj(b).to_response())

    return result


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(booking : BookingPost):
    new_booking: BookingConstructor = BookingConstructor()

    try:
        house : House = House.parse_obj(houses.find_one({"_id": ObjectId(booking.house_id)}))
        new_booking.house_id = str(house.id)
        new_booking.house_address = str(house.address)
    except:
        raise HTTPException(
            status_code=400, detail="No se ha encontrado ninguna casa con el ID proporcionado.")

    try:
        guest : User = User.parse_obj(users.find_one({"_id": ObjectId(booking.guest_id)}))
        new_booking.guest_id = str(guest.id)
        new_booking.guest_name = str(guest.username)
    except Exception:
        raise HTTPException(
            status_code=400, detail="No se ha encontrado ningun usuario con el ID proporcionado.")

    from_ = datetime.combine(booking.from_, time.min)
    to = datetime.combine(booking.to, time.min)
    
    new_booking.from_ = from_
    new_booking.to = to

    if booking.cost > 0 and booking.from_ < booking.to:
        new_booking.cost = booking.cost
    else:
        raise HTTPException(
            status_code=400, detail="Coste o fecha incorrectos.")

    if booking.meeting_location is not None:
        new_booking.meeting_location = booking.meeting_location

    new_booking.state = State.REQUESTED

    bookings.insert_one(jsonable_encoder(new_booking.exclude_unset()))

@router.put("/{id}")
async def update(id: str, state: str | None = None, from_: date | None = None, to: date | None = None, cost: float | None = None, meetingLocation: str | None = None):

    # Formatear las fechas correctamente si se han proporcionado
    if from_ is not None:
        from_ = datetime.combine(from_, time.min)
    if to is not None:
        to = datetime.combine(to, time.min)

    # Inicializar diccionario con todos los datos a introducir, borrando los que son None
    data = {"state": state, "from_": from_, "to": to, "cost": cost, "meetingLocation": meetingLocation}
    data = {k: v for k, v in data.items() if v is not None}

    # Comprobar si se han introducido 0 datos y lanzar una excepcion si se da el caso
    if len(data) == 0:
        raise HTTPException(
            status_code=400, detail="No hay nada que actualizar.")

    # Comprobar si el estado y el coste tienen un formato correcto y lanzar una excepcion en caso contrario
    if (state is not None and state not in states) or (cost is not None and cost <= 0):
        raise HTTPException(status_code=400, detail="Valores incorrectos.")

    try:
        booking = bookings.find_one({"_id": ObjectId(id)})
    except Exception:
        booking = None

    if booking is None:
        raise HTTPException(status_code=404, detail=RNE)

    # Usamos dos variables auxiliares para comprobar si "from_" es anterior a "to",
    # independientemente de si se ha introducido en el PUT o no
    dfrom_ = from_ or booking["from_"]
    dto = to or booking["to"]

    if not dfrom_ < dto:
        raise HTTPException(
            status_code=400, detail="La fecha de inicio no es anterior a la de fin.")

    booking = bookings.update_one(
        {"_id": ObjectId(id)}, {"$set": data})


@router.get("/{id}")
def get_by_id(id: str):
    try:
        return Booking.parse_obj(bookings.find_one({"_id" : ObjectId(id)})).to_response()
    except Exception:
        raise HTTPException(status_code=404, detail=RNE)


# Get global


@router.get("/search/")
def search(
    guest_name: str | None = None,
    guest_id: str | None = None,
    house_id: str | None = None,
    state: State | None = None
):
    if guest_name is None and guest_id is None and house_id is None and state is None:
        raise HTTPException(
            status_code=400, detail="No se han proporcionado parametros de busqueda.")

    params = dict()

    if guest_name is not None:
        guest_name = re.compile(".*" + guest_name + ".*",
                               re.IGNORECASE)  # type: ignore
        params['guestName'] = {"$regex": guest_name}

    if guest_id is not None:
        params['guestId'] = guest_id

    if house_id is not None:
        params['houseId'] = house_id

    if state is not None:
        params['state'] = state.value

    bookings_list = list(bookings.find(filter=params))
    result = []

    for b in bookings_list:
        result.append(Booking.parse_obj(b).to_response())

    return result


@ router.get("/range/")
async def get_range(size: int, offset: int = 0):
    if offset < 0 or size <= 0:
        raise HTTPException(
            status_code=400, detail="El tamaño o el offset no tienen un formato correcto.")

    return list(bookings.find(projection={"_id": 0}, skip=offset, limit=size))


@ router.delete("/{id}")
async def delete(id: str):
    try:
        booking = bookings.find_one_and_delete({"_id": ObjectId(id)})
    except Exception:
        booking = None

    if booking is None:
        raise HTTPException(status_code=404, detail=RNE)
