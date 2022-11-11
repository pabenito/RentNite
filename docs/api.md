# API 

Hemos distributido la API en los siguientes microservicios:

- Entidad casa (/houses): "http://127.0.0.1:8000/houses"
- Entidad reserva (/bookings): "http://127.0.0.1:8000/bookings"
- Entidad mensajes (/messages): "http://127.0.0.1:8000/messages"
- OpenStreetMap (/osm): "http://127.0.0.1:8000/osm"
- AEMET OpenData (/aemet): "http://127.0.0.1:8000/aemet"

De cada llamada a la API se especificará su funcionalidad y argumentos, si los tiene.

Los argumentos seguirán la siguiente notación:

- {argumento del path}
- ?argumento query
- argumento opcional~valor por defecto (argumento~ = argumento~None)

## Houses

**Punto**: /houses
**URL**: "http://127.0.0.1:8000/houses"

Se describe a continuación la funcionalidad ofrecida por la API houses:

- **GET /houses/**: Da la bienvenida.
- **POST /houses/**: Añade una nueva casa.
    - ?_address_: Dirección
    - ?_capacity_: Máximo número de visitantes
    - ?_price_: Precio por noche
    - ?_rooms_: Habitaciones
    - ?_bathrooms_: Cuartos de baño
    - ?_ownerName_: Nombre del propietario
- **GET /houses/{id}**: Devuelve la casa con el id especificado.
    - {_id_}: Identificador de la casa
- **PUT /houses/{id}**: Actualiza los datos de la casa con el id especificado.
    - {_id_}: Identificador de la casa
    - ?_address_: Dirección
    - ?_capacity_: Máximo número de vistantes
    - ?_price_: Precio por noche
    - ?_rooms_: Habitaciones
    - ?_bathrooms_: Cuartos de baño
    - ?_ownerName_: Nombre del propietario
- **DELETE /houses/{id}**: Elimina la casa con el id especificado.
    - {_id_}: Identificador de la casa
- **GET /houses/range/**: Lista tantas casas como ?_size_ indique, saltándose las ?_skip_ primeras. Se suponen ordenadas por inserción en la base de datos. 
    - ?_size_: Número de casas a devolver
    - ?_skip_: Número de casas a saltarse (su valor por defecto es 0)
- **GET /houses/address/{address}**: Devuelve la casa con la dirección especificada.
    - {_address_}: Dirección
- **GET /houses/owner/{ownerName}/guests**: Devuelve los nombres de los visitantes de todas las viviendas de un propietario.
    - {_ownerName_}: Nombre del propietario

## Bookings

**Punto**: /bookings
**URL**: "http://127.0.0.1:8000/bookings"

Se describe a continuación la funcionalidad ofrecida por la API bookings:

- **GET /bookings/**: Lista todas las reservas.
- **POST /bookings/**: Añade una solicitud de reserva.
    - ?_from__: Fecha de llegada
    - ?_to_: Fecha de salida
    - ?_cost_: Precio total de la estancia
    - ?_guestId_: Identificador del usuario que solicita la reserva
    - ?_houseId_: Identificador de la casa donde se realiza la reserva
    - ?_meetingLocation_~: Dirección donde se realizará la reunión en la que se informará al cliente sobre cualquier detalle que deba conocer sobre la vivienda y en la que le serán entregadas las llaves de esta (solo si se especifica)
- **GET /bookings/{id}**: Devuelve la reserva con el _id_ especificado.
    - {_id_}: Identificador de la reserva
- **PUT /bookings/{id}**: Actualiza los datos de la reserva con el _id_ especificado.
    - {_id_}: Identificador de la reserva
    - ?_state_~: Estado de la reserva
    - ?_from__~: Fecha de llegada
    - ?_to_~: Fecha de salida
    - ?_cost_~: Precio total de la estancia
    - ?_meetingLocation_~: Dirección donde se realizará la reunión en la que se informará al cliente sobre cualquier detalle que deba conocer sobre la vivienda y en la que le serán entregadas las llaves de esta (solo si se especifica)
- **DELETE /bookings/{id}**: Elimina la reserva con el id especificado.
    - {_id_}: Identificador de la reserva
- **GET /bookings/search/**: Muestra una lista de reservas dada una serie de filtros de búsqueda que se pueden usar simultáneamente.
    - ?_guestName_~: Nombre del usuario que ha realizado la reserva (invitado)
    - ?_houseId_~: Identificador de la casa donde se realiza la reserva
    - ?_state_~: Estado de la reserva
- **GET /bookings/range/**: Lista tantas reservas como _size_ indique, saltándose las _offset_ primeras. Se suponen ordenadas por inserción en la base de datos. 
    - ?_size_: Número de reservas a mostrar
    - ?_offset_~0: Número de reservas que saltar

## Messages

**Punto**: /messages
**URL**: "http://127.0.0.1:8000/messages"

Se describe a continuación la funcionalidad ofrecida por la API messages:

- **GET /messages/**: Devuelve una lista con todos mensajes que cumplan con el filtro especificado, si no se especifican filtros devuelve todos los mensajes.
    - ?sender\_id~: Identificador del usuario que lo envió
    - ?house\_id~: Identificador de la casa a la que pertenece el mensaje (como comentario).
    - ?chat\_id~: Identificador del chat al que pertenece el mensaje
    - ?from~: Fecha para buscar mensajes de esta en adelante
    - ?to~: Fecha para buscar mensajes de esta hacia atrás
- **POST /messages/**: Crea un nuevo mensaje.
    - ?message: Mensaje a enviar  
    - ?sender\_id~user.id: Identificador del usuario que lo envia
    - ?sender\_username~user.username: Nombre de usuario del usuario que lo envia
    - ?house\_id~: Identificador de la casa a la que pertenece el mensaje (como comentario).
    - ?chat\_id~: Identificador del chat al que pertenece el mensaje
    - ?date~now(): Fecha en la que es envía el mensaje
- **GET /messages/{id}**: Devuelve el mensaje con el id especificado.
    - {_id_}: Identificador del mensaje 
- **DELETE /messages/{id}**: Elimina mensaje con el id especificado.
    - {_id_}: Identificador del mensaje 

## Chat 

**Punto**: /chats
**URL**: "http://127.0.0.1:8000/chats"

Representa los chats entre usuarios.

Se describe a continuación la funcionalidad ofrecida por la API chats:

- **GET /chats/**: Devuelve una lista con todos chats que cumplan con el filtro especificado, si no se especifican filtros devuelve todos los chats.
    - ?house\_address~: Dirección de la casa asociada al booking al que pertenece el chat  
    - ?booking\_id~: Identificador de la reserva asociada al chat
    - ?owner\_id~: Identificador del propietario de la casa
    - ?owner\_username~: Nombre de usuario del propietario de la casa
    - ?guest\_id~: Identificador del usuario que ha solitado la reserva
    - ?guest\_id~: Nombre de usuario del usuario que ha solitado la reserva
    - ?from~: Fecha para buscar chats de de reservas cuya fecha de inicio esté de esta en adelante
    - ?to~: Fecha para buscar chats de de reservas cuya fecha de inicio esté de esta hacia atrás
- **POST /chats/**: Crea un nuevo chat.
    - ?booking\_id: Identificador de la reserva asociada al chat
- **GET /chats/{id}**: Devuelve el chat con el id especificado.
    - {_id_}: Identificador del chat  

## OpenStreetMap

**Punto**: /osm
**URL**: "http://127.0.0.1:8000/osm"

Se describen a continuación la funcionalidad ofrecida por la API houses:

- **GET /osm/**: Da la bienvenida.
- **GET /osm/nodes/{id}**: Devuelve los datos del nodo con el id especificado.
    - {_id_}: Identificador del nodo
- **GET /osm/maps/poi**: Devuelve los puntos de interés (solo nodos con al menos dos etiquetas) a la distancia indicada en ?_range_ (en kilómetros) (por defecto 1km) alrededor de las coordenadas especificadas. Ejemplo: <http://127.0.0.1:8000/osm/maps/poi?latitude=36.72&longitude=-4.48&range=0.1>
    - ?latitude: Latitud
    - ?longitude: Longitud
    - ?range~1: Rango en kilómetros
    - ?search~: Elementos que buscar (bus_stop, restaurant, subway)
- **GET /osm/maps/all**: Devuelve los elementos a la distancia indicada en ?_range_ (en kilómetros) (por defecto 1km) alrededor de las coordenadas especificadas. Ejemplo: Paradas de autobuses a 500 metros <http://127.0.0.1:8000/osm/maps/all?latitude=36.72&longitude=-4.48&range=0.5&search=bus_stop>
    - ?latitude: Latitud
    - ?longitude: Longitud
    - ?range~1: Rango en kilómetros.

## AEMET OpenData

**Punto**: /aemet
**URL**: "http://127.0.0.1:8000/aemet"

Se describen a continuación la funcionalidad ofrecida por la API houses:

- **GET /aemet/**: Da la bienvenida.
- **GET /aemet/town**: Devuelve la ciudad en la que se encuentran las coordenadas especificadas y sus datos.
    - ?latitude: Latitud
    - ?longitude: Longitud
- **GET /aemet/forecast/temperature/daily**: evuelve el máximo y mínimo de temperatura prevista para los próximos 7 días en las coordenadas especificadas.
    - ?latitude: Latitud
    - ?longitude: Longitud
- **GET /aemet/forecast/temperature/hourly**: Devuelve la temperatura prevista para los próximos 7 días en intervalos de 6 horas en las coordenadas especificadas.
    - ?latitude: Latitud
    - ?longitude: Longitud
- **GET /aemet/forecast/precipitation/daily**: Devuelve la probabilidad de lluvia prevista para los próximos 7 días en las coordenadas especificadas.
    - ?latitude: Latitud
    - ?longitude: Longitud
- **GET /aemet/forecast/precipitation/hourly**: Devuelve la probabilidad de lluvia prevista para los próximos 7 días en intervalos de 6 horas en las coordenadas especificadas.
    - ?latitude: Latitud
    - ?longitude: Longitud
