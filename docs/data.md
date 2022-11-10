# Data model JSON

This document intend to represent the data model for each entity in the non-SQL database.

## Syntaxis

entity{
  required attribute, (means attribute is required)
  optional attribute*, (means attribute is optional)
  attribute with default value = default value, (means has a default value)
  auto-initialized attribute = function, (means it is initialized to function value)
  attribute1 | attribute2 (means only one of them),
  [list attribute] (measn the value is a list of values)
}

**Note**: Every entity has _id attribute, so is not represeted in the model. 

## Entities 

### Messages

Messages{
    sender_id = user.id,
    sender_username = user.username,
    date = now(), 
    message,
    respose_to*,
    house_id | booking_id | chat_id
  }

Messagges can be sent:

  - As a comment to a house (house_id)
  - As a message into a booking chat (booking_id)
  - As a message into a users chat (chat_id)

### Chats

Chats{
    [users]
  }


