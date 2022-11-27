# Import libraries
import re
from datetime import date, datetime, time
from fastapi import APIRouter, HTTPException, status

from bson.objectid import ObjectId
from app.database import db

# Create router
router = APIRouter()

# Initialize DB
bookings = db["bookings"]
houses = db["houses"]
users = db["users"]

# Save possible states for later
states = ["Accepted", "Declined", "Requested", "Cancelled"]

#Constants
RNE = "Reserva no encontrada."

# API


@router.get("/")
def get():
    return list(bookings.find(projection={"_id": 0}))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(from_: date, to: date, cost: float, guestId: str, houseId: str, meetingLocation: str | None = None):
    try:
        house = houses.find_one({"_id": ObjectId(houseId)})
    except Exception:
        house = None

    if house is None:
        raise HTTPException(
            status_code=400, detail="No se ha encontrado ninguna casa con el ID proporcionado.")

    try:
        guest = users.find_one({"_id": ObjectId(guestId)})
    except Exception:
        guest = None

    if guest is None:
        raise HTTPException(
            status_code=400, detail="No se ha encontrado ningun usuario con el ID proporcionado.")

    # Comprobar si la id introducida corresponde a una casa

    from_ = datetime.combine(from_, time.min)
    to = datetime.combine(to, time.min)

    if cost > 0 and from_ < to:
        bookings.insert_one({"state": "Requested", "from_":  from_,
                            "to": to, "cost": cost, "guestId": guestId,
                            "guestName": guest["username"], "houseId": houseId,
                            "houseAddress": house["address"], "meetingLocation": meetingLocation})
    else:
        raise HTTPException(
            status_code=400, detail="Coste o fecha incorrectos.")


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
        booking = bookings.find_one(filter={"_id": ObjectId(id)}, projection={"_id": 0})
    except Exception:
        booking = None

    if booking is None:
        raise HTTPException(status_code=404, detail=RNE)

    return booking


# Get global


@router.get("/search/")
def search(guestName: str | None = None, houseId: str | None = None, state: str | None = None):
    if guestName is None and houseId is None and state is None:
        raise HTTPException(
            status_code=400, detail="No se han proporcionado parametros de busqueda.")

    params = dict()

    if guestName is not None:
        guestName = re.compile(".*" + guestName + ".*",
                               re.IGNORECASE)  # type: ignore
        params['guestName'] = {"$regex": guestName}

    if houseId is not None:
        params['houseId'] = houseId

    if state is not None:
        if state not in states:
            raise HTTPException(
                status_code=400, detail="El estado proporcionado no es valido.")
        params['state'] = state

    return list(bookings.find(filter=params, projection={"_id": 0}))


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
