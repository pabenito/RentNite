# Data model JSON

This document intend to represent the data model for each entity in the non-SQL database.

## Syntaxis

```
entity{
  required attribute, (means attribute is required)
  optional attribute*, (means attribute is optional)
  attribute with default value = default value, (means has a default value)
  auto-initialized attribute = function, (means it is initialized to function value)
  attribute1 | attribute2 (means only one of them),
  [list attribute] (means the value is a list of values)
}
```

**Note**: Every entity has _id attribute, so is not represented in the model. 

## Entities 

### Messages

```
Messages{
    sender_id = user.id,
    sender_username = user.username,
    date = now(), 
    message,
    response_to*,
    house_id | chat_id
  }

```

Messagges can be sent:

  - As a comment to a house (house_id)
  - As a message into chat (chat_id)

### Chats

```
Chats{
    house_address,
    booking_from,
    booking_to,
    booking_id, 
    owner_id,
    owner_username,
    guest_id,
    guest_username
  }
```

### Ratings

```
Ratings{
    rater_id,
    rate,
    rated_user_id | rated_house_id
  }
```

### Bookings

```
Bookings{
    state,
    from_,
    to,
    cost,
    guestId,
    userName,
    houseId,
    houseAddress,
    meetingLocation
}

```