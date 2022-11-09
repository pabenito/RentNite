# Import libraries
from fastapi import APIRouter, HTTPException
from database import db as db
from bson.objectid import ObjectId
from datetime import datetime, date, time
import re, pydantic

# Create router
router = APIRouter()

# Initialize DB
bookings = db["bookings"]
houses = db["houses"]

# Save possible states for later
states = ["Accepted", "Declined", "Requested", "Cancelled"]

# declare Objectid as str
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

# API
@router.get("/")
async def get():
    return list(bookings.find())



@router.post("/")
async def create(from_: date, to: date, cost: float, userName: str, houseId: str):
    try:
        house = houses.find_one({"_id": ObjectId(houseId)})
    except:
        house = None
    
    if house is None:
        raise HTTPException(
            status_code=400, detail="No se ha encontrado ninguna casa con la ID proporcionada.")

    # Comprobar si la id introducida corresponde a una casa

    from_ = datetime.combine(from_, time.min)
    to = datetime.combine(to, time.min)

    if cost > 0 and from_ < to:
        bookings.insert_one({"state": "Requested", "from_":  from_,
                            "to": to, "cost": cost, "userName": userName, "houseId": houseId, "houseAddress": house["address"]})
    else:
        raise HTTPException(
            status_code=400, detail="Coste o fecha incorrectos.")


@router.put("/{id}")
async def update(id: str, state: str | None = None, from_: date | None = None, to: date | None = None, cost: float | None = None):
    
    #Formatear las fechas correctamente si se han proporcionado
    if from_ is not None:
        from_ = datetime.combine(from_, time.min)
    if to is not None:
        to = datetime.combine(to, time.min)

    #Inicializar diccionario con todos los datos a introducir, borrando los que son None
    data = {"state": state, "from_": from_, "to": to, "cost": cost}
    data = {k: v for k, v in data.items() if v is not None}

    #Comprobar si se han introducido 0 datos y lanzar una excepcion si se da el caso
    if len(data) == 0:
        raise HTTPException(
            status_code=400, detail="No hay nada que actualizar.")

    #Comprobar si el estado y el coste tienen un formato correcto y lanzar una excepcion en caso contrario
    if (state is not None and state not in states) or (cost is not None and cost <= 0):
        raise HTTPException(status_code=400, detail="Valores incorrectos.")

    try:
        booking = bookings.find_one({"_id": ObjectId(id)})
    except:
        booking = None

    if booking is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    #Usamos dos variables auxiliares para comprobar si "from_" es anterior a "to" independientemente de si se ha introducido en el PUT o no
    dfrom_ = from_ or booking["from_"]
    dto = to or booking["to"]

    if not dfrom_ < dto:
        raise HTTPException(
            status_code=400, detail="La fecha de inicio no es anterior a la de fin.")

    booking = bookings.update_one(
        {"_id": ObjectId(id)}, {"$set": data})

@router.get("/{id}")
async def get_by_id(id: str):
    try:
        booking = bookings.find_one({"_id": ObjectId(id)})
    except:
        booking = None

    if booking is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")
    else:
        return booking


@router.get("/userName/{userName}")
async def get_by_user_name(userName: str):
    userName = re.compile(".*" + userName + ".*",
                          re.IGNORECASE)  # type: ignore
    return [b for b in bookings.find({"userName": {"$regex": userName}}, {"_id": 0})]


@router.get("/house/{houseId}")
async def get_by_house_id(houseId: str):
    return [b for b in bookings.find({"houseId": houseId}, {"_id": 0})]


@router.get("/state/{state}")
async def get_by_state(state: str):
    if state not in states:
        raise HTTPException(
            status_code=400, detail="El estado introducido no existe.")

    return [b for b in bookings.find({"state": state}, {"_id": 0})]


@router.get("/range/")
async def get_range(size: int, offset: int = 0):
    if offset >= 0 and size > 0:
        return [b for b in bookings.find(projection={"_id": 0}, skip=offset, limit=size)]
    else:
        raise HTTPException(
            status_code=400, detail="El tamaño o el offset no tienen un formato correcto.")


@router.delete("/{id}")
async def delete(id: str):
    try:
        booking = bookings.find_one_and_delete({"_id": ObjectId(id)})
    except:
        booking = None

    if booking is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")
