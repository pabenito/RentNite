# Requirements

## Glossary

### Acronyms

- **App**: Application. (AirBnB) 
- **DB**: Data Base.

### Users 
- **Houseowners**: People who have houses.
- **Guest**: People who use AirBnB to rent a house. 

### Attributes

- **Capatity**: Maximum number of people that can sleep in the house.
- **Price**: Price per night. 
- **Size**: Surface area in square metres.
- **Essentials**: Towels, bed sheets, soap, and toilet paper.
- **Beach essentials**: Beach towels, umbrella, beach blanket, snorkeling gear.

### States 

- **Avalible**: Can be booked.
- **Blocked**: Cannot be booked.
- **Occupied**: Already booked.

### Requirements 

- **Base**: Explicitly stated by the [client](https://informatica.cv.uma.es/pluginfile.php/515058/mod_resource/content/6/0.%20Caso%20de%20estudio.pdf). If nothing is stated in the title of the requirement it is assumed to be basic.
- **Supposed**: Not explicitly stated by the [client](https://informatica.cv.uma.es/pluginfile.php/515058/mod_resource/content/6/0.%20Caso%20de%20estudio.pdf), but probably needed. 
- **Extra**: Functionality that would be useful, even not explicitly stated by the [client](https://informatica.cv.uma.es/pluginfile.php/515058/mod_resource/content/6/0.%20Caso%20de%20estudio.pdf). It will not be considered a priority, but will only be implemented if time is left over.

## Functional

### System

- **Load images**: The system must be able to upload images.
- **Map usage**: The system must be able to use map services as OpenStreetMap or Google Maps.
- **Emails**: Send automatic emails (e.g. confirmation of a booking or payment), and advertise the accommodation on social networks, such as Twitter.
- **Open data service**: The _app_ will make use of open data such as [Gobierno de España](https://datos.gob.es) or other platforms to provide information on public transport, weather forecasts in
platforms to provide information on public transport, weather forecasts at destinations, pollution levels, etc.
- **Messaging**: The _app_ will allow users to interact with each other, through messages between them.

### Users 

- **_Supposed_. Roles**: An user can be a _houseowner_ and a _guests_.

### _Houseowners_

- **Publish houses**: _Houseowners_ can publish their houses, one advertisement per house. 
- **Edit houses**: _Houseowners_ can edit their houses. Except the state of the dates already past.
- **Delete houses**: _Houseowners_ can delete their houses. 
- **Accept booking requests**: Accept booking requests from _guests_.  
- **Decline booking requests**: Decline booking requests from _guests_.
- **Rate _guest_**: The _houseowner_ of a house can rate a _guest_ that had been there once the final date ends. 
- **Answer a comment**: The _houseowner_ can answer the comments made on his advertised houses.

### _Guests_ 

- **Booking request**: Send a request for booking a house a period of time.
- **_Supposed_. Cancel booking**: Cancel a booking he had already booked.
- **Search houses with filters**: When a _guest_ is searching for a house, he can set filters:
    - Geographic (Proximity to a certain place)
    - The _houseowner_
    - Date disponibility (if it is avalible)
    - _Price_ range.
    - _Supposed_. _Capatity_.
- **Rate house**: The _guest_ who did the booking can rate the house once the final date ends. 
- **Let a comment**: The _guest_ can share complains, questions or suggest through comments on the advertised house or as an answer on another comment.

### Bookings

- **Relate _guest_ with booking**: When a _guest_ does a booking, this booking relates this _geust_ with the house booked.
- **Initial and final date**: Doing a booking implies have an inital and final end date. All this period must be _avalible_ before the booking is done, then when the _houseowner_ accept the request all mut be set as _occupied_.  
- **Meeting point / key pick-up padlock**: A booking must have a meeting point or a key pick-up padlock for the initial day of the booking.  

### Houses

- **Identify house**: Houses must be identified by their address.
- **Unique house**: A house can't be published more than once in the _app_.
- **House owner**: Each house must have an _houseowner_.
- **House _base_ attributes**: Address, _capacity_ and _price_.
- **House _supposed_ attributes**: Rooms, bathrooms. (From [Airbnb](https://www.airbnb.com/))
- **House _extra_ attributes** (Services): From [AirBnB](https://www.airbnb.com/rooms/584469386220279136/amenities?adults=1&category_tag=Tag%3A8225&children=0&infants=0&search_mode=flex_destinations_search&check_in=2023-01-03&check_out=2023-01-09&federated_search_id=32d82aa5-d216-445e-87bf-7719bbb4db5c&source_impression_id=p3_1664352813_nq%2Bsh4T5DMqlBdQk). 
    - Bathroom 
      - [ ] Bathtub 
      - [ ] Hair dryer
    - Bedroom and laundry
      - [ ] Washer
      - [ ] _Eessentials_
      - [ ] Bed liens
      - [ ] Iron 
    - Entertainment 
      - [ ] TV
    - Heating and cooling
      - [ ] Air conditioning
      - [ ] Heating 
    - Internet and office 
      - [ ] Wifi 
    - Kitchen and dining
      - [ ] _Kitchen_ 
      - [ ] Refrigerator
      - [ ] Microwave
      - [ ] Dishes and silverware
      - [ ] Freezer
      - [ ] Dishwasher
      - [ ] Stove
      - [ ] Oven
      - [ ] Hot watter kettle
      - [ ] Coffe maker
      - [ ] Toaster
      - [ ] Blender
    - Outdoor
      - [ ] Patio or balcony
      - [ ] Backyard
      - [ ] BBQ grill
      - [ ] _Beach essentials_
    - Parking and facilities
      - [ ] Parking 
      - [ ] Pool
    - Security
      - [ ] Smoke alarm
      - [ ] Carbon monoxide alarm
      - [ ] Private entrance
- **Date state**: Each date can be _avalible_, _bloked_, or _occupied_. 

## Non-functional 

- **Persistence**: The _app_ must persist data on a _DB_.
- **OAuth**: The _app_ must manage the identified access of users through OAuth 2.0 and an external account system, e.g. Google or Facebook.
- **Payment**: The application will be integrated with a payment service, such as PayPal, for the payment of bookings.
