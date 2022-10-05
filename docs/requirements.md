# Requirements

## Glossary

### Acronyms

- **App**: Application (RentNite). 
- **DB**: Data Base.
- **REST**: Representational State Transfer (Architecture style).

### Users 
- **Houseowners**: People who have houses.
- **Guests**: People who use RentNite to rent a house. 

### Attributes

- **Capacity**: Maximum number of people that can sleep in the house.
- **Price**: Price per night.

### States 

- **Available**: Can be booked.
- **Occupied**: Already booked.

### Requirements 

- **Base**: Explicitly stated by the [client](https://informatica.cv.uma.es/pluginfile.php/515058/mod_resource/content/6/0.%20Caso%20de%20estudio.pdf). If nothing is stated in the title of the requirement it is assumed to be basic.
- **Supposed**: Not explicitly stated by the [client](https://informatica.cv.uma.es/pluginfile.php/515058/mod_resource/content/6/0.%20Caso%20de%20estudio.pdf), but probably needed. 
- **Extra**: Functionality that would be useful, even not explicitly stated by the [client](https://informatica.cv.uma.es/pluginfile.php/515058/mod_resource/content/6/0.%20Caso%20de%20estudio.pdf). It will not be considered a priority, but will only be implemented if time is left over.

## Functional

### System

- **Load images**: The _app_ must be able to upload images.
- **Map usage**: The _app_ must be able to use map services as OpenStreetMap or Google Maps.
- **Emails**: The _app_ will send automatic emails (e.g. confirmation of a booking or payment), and advertise the accommodation on social networks, such as Twitter.
- **Open data service**: The _app_ will make use of open data such as [Gobierno de España](https://datos.gob.es) or other platforms to provide information on public transport, weather forecasts at destinations, pollution levels, etc.
- **Messaging**: The _app_ will allow users to interact with each other, through messages between them.
- **Payment**: The _app_ will be integrated with a payment service, such as PayPal, for the payment of bookings.

### Users 

- **_Supposed_. Roles**: An user can be a _houseowner_ and a _guest_.

### _Houseowners_

- **Publish houses**: _Houseowners_ can publish their houses, one advertisement per house. 
- **Edit houses**: _Houseowners_ can edit their houses. Except the state of the dates already past.
- **Delete houses**: _Houseowners_ can delete their houses. 
- **Accept booking requests**: Accept booking requests from _guests_.  
- **Decline booking requests**: Decline booking requests from _guests_.
- **Rate _guest_**: The _houseowner_ of a house can rate a _guest_ that had been there once the final date ends. 
- **Answer a comment**: The _houseowner_ can answer the comments made on his advertised houses.
- **Advertise houses**: The _houseowner_ advertise the house on social networks, such as Twitter.

### _Guests_ 

- **Booking request**: Send a request for booking a house a period of time.
- **_Supposed_. Cancel booking**: Cancel a booking he had already booked.
- **Search houses with filters**: When a _guest_ is searching for a house, he can set filters:
    - Geographic (Proximity to a certain place)
    - The _houseowner_
    - Date disponibility (if it is avalible)
    - _Price_ range.
    - _Supposed_. _Capacity_.
- **Rate house**: The _guest_ who did the booking can rate the house once the final date ends. 
- **Write a comment**: The _guest_ can share complains, questions or suggestions through comments on the advertised house or as an answer on another comment.

### Bookings

- **Relate _guest_ with booking**: When a _guest_ does a booking, this booking relates this _guest_ with the house booked.
- **Initial and final date**: Doing a booking implies having an initial and final end date. All this period must be _available_ before the booking is done, then when the _houseowner_ accepts the request all must be set as _occupied_.  
- **Meeting point / key pick-up padlock**: A booking must have a meeting point or a key pick-up padlock for the initial day of the booking.  

### Houses

- **Identify house**: Houses must be identified by their address.
- **Unique house**: A house can't be published more than once in the _app_.
- **House owner**: Each house must have an _houseowner_.
- **House description**: A published house must have a description where all its attributes are shown (e.g. Kitchen furniture, has wifi, has pool or parking...).
- **Date state**: Each date can be _available_ or _occupied_.
- **Location**: Houses have a location, that allows to locate them in the map. 

## Non-functional 

- **Persistence**: The _app_ must persist data on a _DB_.
- **OAuth**: The _app_ must manage the identified access of users through OAuth 2.0 and an external account system, e.g. Google or Facebook.
- **Supposed. Architecture style**: The _app_ architecture style will be _REST_.
