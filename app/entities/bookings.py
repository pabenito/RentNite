# Import libraries
import re
from datetime import date, datetime, time
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, HTTPException, status
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from app.database import db
from .models import *
from ..entities import houses as houses_api
from ..opendata.osm import geocode

# Create router
router = APIRouter()

# Initialize DB
bookings: Collection = db["bookings"]
houses: Collection = db["houses"]
users: Collection = db["users"]

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
def create(booking : BookingPost):
    new_booking = dict()

    # Casa
    try:
        house : House = House.parse_obj(houses.find_one({"_id": ObjectId(booking.house_id)}))
        new_booking["house_id"] = str(house.id)
        house_address = {"city": house.address.city, "street": house.address.street, "number": house.address.number, 
                                        "latitude": house.address.latitude, "longitude": house.address.longitude}
        house_address = {k: v for k, v in house_address.items() if v is not None}
        new_booking["house_address"] = house_address
    except:
        raise HTTPException(
            status_code=400, detail="No se ha encontrado ninguna casa con el ID proporcionado.")

    # Cliente
    try:
        guest : User = User.parse_obj(users.find_one({"_id": ObjectId(booking.guest_id)}))
        new_booking["guest_id"] = str(guest.id)
        new_booking["guest_name"] = guest.username
    except Exception:
        raise HTTPException(
            status_code=400, detail="No se ha encontrado ningun usuario con el ID proporcionado.")

    # Comprobar si las fechas son validas
    if not (date.today() <= booking.from_ < booking.to):
        raise HTTPException(
            status_code=400, detail="Fecha incorrecta.")

    # Comprobar si la casa ya esta reservada para esa fecha
    bookings_list = search(house_id=new_booking["house_id"])

    from_ = datetime.combine(booking.from_, time.min)
    to = datetime.combine(booking.to, time.min)

    for b in bookings_list:
        if b["from_"] <= to <= b["to"] or b["from_"] <= from_ <= b["to"]:
            raise HTTPException(400, "La fecha no puede solaparse con otra reserva.")

    new_booking["from_"] = from_
    new_booking["to"] = to

    # Lugar de reunion
    if booking.meeting_location is not None:
        location = booking.meeting_location
        geocode_result = geocode(location.street, location.city, location.number)

        meeting_location = {"city": location.city, "street": location.street, "number": location.number}

        if geocode_result is not None:
            meeting_location["latitude"] = float(geocode_result["lat"])
            meeting_location["longitude"] = float(geocode_result["lon"])

        new_booking["meeting_location"] = meeting_location

    new_booking["cost"] = booking.cost
    new_booking["state"] = State.REQUESTED.value

    inserted_booking: InsertOneResult = bookings.insert_one(new_booking)
    return Booking.parse_obj(bookings.find_one({"_id": ObjectId(inserted_booking.inserted_id)})).to_response()

@router.put("/{id}")
def update(id: str, state: State | None = None, from_: date | None = None, to: date | None = None, cost: float | None = None, meeting_location: AddressPost | None = None):

    # Formatear las fechas correctamente si se han proporcionado
    if from_ is not None:
        from_ = datetime.combine(from_, time.min)
    if to is not None:
        to = datetime.combine(to, time.min)

    if state is not None:
        state = state.value

    # Inicializar diccionario con todos los datos a introducir, borrando los que son None
    data = {"state": state, "from_": from_, "to": to, "cost": cost}
    data = {k: v for k, v in data.items() if v is not None}

    # Formatear la direccion correctamente si se ha proporcionado
    if meeting_location is not None:
        final_address: dict = {"city": meeting_location.city, "street": meeting_location.street, "number": meeting_location.number}
        
        geocode_result = geocode(meeting_location.city, meeting_location.street, meeting_location.number)

        if geocode_result is not None:
            final_address["latitude"] = float(geocode_result["lat"]) # type: ignore
            final_address["longitude"] = float(geocode_result["lon"]) # type: ignore
        
        data["meeting_location"] = final_address

    # Comprobar si se han introducido 0 datos y lanzar una excepcion si se da el caso
    if len(data) == 0:
        raise HTTPException(
            status_code=400, detail="No hay nada que actualizar.")

    # Comprobar si el coste tiene un formato correcto y lanzar una excepcion en caso contrario
    if cost is not None and cost <= 0:
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

    if not (datetime.combine(date.today(), time.min) <= dfrom_ < dto):
        raise HTTPException(
            status_code=400, detail="Fecha incorrecta.")

    # Comprobar si la casa ya esta reservada para esa fecha
    bookings_list = search(house_id=booking["house_id"])
    
    for b in bookings_list:
        if b["id"] != id and ((b["from_"] <= dto <= b["to"]) or (b["from_"] <= dfrom_ <= b["to"])):
            raise HTTPException(400, "La fecha no puede solaparse con otra reserva.")

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
        params['guest_name'] = {"$regex": guest_name}

    if guest_id is not None:
        params['guest_id'] = guest_id

    if house_id is not None:
        params['house_id'] = house_id

    if state is not None:
        params['state'] = state.value

    bookings_list = list(bookings.find(filter=params))
    result = []

    for b in bookings_list:
        result.append(Booking.parse_obj(b).to_response())

    return result

# Get bookings by house owner name
@router.get("/getByHouseOwner")
def get_by_house_owner_id(owner_id: str):
    bookings_list = list(bookings.find())
    result = []

    for b in bookings_list:
        house = houses_api.get_by_id(b["house_id"])
        if house["owner_id"] == owner_id:
            result.append(Booking.parse_obj(b).to_response())

    return result

@ router.get("/range/")
def get_range(size: int, offset: int = 0):
    if offset < 0 or size <= 0:
        raise HTTPException(
            status_code=400, detail="El tamaño o el offset no tienen un formato correcto.")

    bookings_list = list(bookings.find(skip=offset, limit=size))
    result = []

    for b in bookings_list:
        result.append(Booking.parse_obj(b).to_response())
    
    return result


@ router.delete("/{id}")
def delete(id: str):
    try:
        booking = bookings.find_one_and_delete({"_id": ObjectId(id)})
    except:
        booking = None

    if booking is None:
        raise HTTPException(status_code=404, detail=RNE)
