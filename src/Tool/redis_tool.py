from redis.asyncio import Redis
from config.config import settings
from crewai.tools import tool

redis_url = settings.redis_url
redis = Redis.from_url(redis_url, decode_responses=True)

@tool
async def save_hotel_search_options(convo_id, offers, guest):
    """
    Save the hotel offers and room search payload info as separate keys in Redis.
    """
    try:
        offers_key = f"hotel_booking:offers:{convo_id}"
        gest_key = f"hotel_booking:room_search_payload:{convo_id}"

        await redis.json().set(offers_key, "$", offers)
        await redis.json().set(gest_key, "$", guest)
        return "Hotel search options saved successfully."
    except Exception as e:
        return "Error saving hotel search options."

@tool
async def save_hotelDetails_room_options(convo_id, hotelDetails, roomsOption):
    """
    Save the room option and hotel details as description, policy and cancellation.
    """
    try:
        rooms_key = f"hotel_booking:rooms:{convo_id}"
        hotelDetails_key = f"hotel_booking:hotelDetails:{convo_id}"

        await redis.json().set(rooms_key, "$", roomsOption)
        await redis.json().set(hotelDetails_key, "$", hotelDetails)
        return "Hotel details and room options saved successfully."
    except Exception as e:
        return "Error saving hotel details and room options."

@tool
async def get_hotel_search_options(convo_id: str) -> list:
    """
    Retrieve the list of all hotel search options stored in Redis.
    """
    offers_key = f"hotel_booking:offers:{convo_id}"
    offers = await redis.json().get(offers_key, "$")

    if not offers or not isinstance(offers, list):
        return "No offers found for this conversation."
    
    return "/n".join(offers)

@tool
async def change_option_status_hotel_offer(
    convo_id: str, selected_option, status: str = "selected"
):
    """
    Change the status of a selected hotel offer in Redis.
    If status is "selected": set only that hotel to selected and all others to unselected.
    If status is "unselected": set only that hotel to unselected, others stay unchanged.
    """
    offers_key = f"hotel_booking:offers:{convo_id}"

    # Get the nested offers list from Redis
    offers_nested = await redis.json().get(offers_key, "$")
    if (
        not offers_nested
        or not isinstance(offers_nested, list)
        or not isinstance(offers_nested[0], list)
    ):
        return "No offers found for this conversation."

    offers = offers_nested[0]  # Unpack one level

    # Find index of the selected option
    idx = next(
        (i for i, o in enumerate(offers) if o.get("option") == selected_option), None
    )
    if idx is None:
        return f"Option '{selected_option}' not found."

    if status == "selected":
        # Mark only the selected offer as "selected", all others "unselected"
        for i, offer in enumerate(offers):
            offer["status"] = "selected" if i == idx else "unselected"

        await redis.json().set(offers_key, "$", offers)  # Keep original structure
        return "selected"

    if status == "unselected":
        offers[idx]["status"] = "unselected"
        await redis.json().set(offers_key, "$", offers)  # Also keep structure

        return "unselected"

    return "Invalid status value."

@tool
async def is_selected_option_from_key(convo_id: str) -> dict:
    """
    Check the hotel offers in Redis and return the selected option if any.
    """
    try:
        offers_key = f"hotel_booking:offers:{convo_id}"
        offers_nested = await redis.json().get(offers_key, "$")

        # Extract the list of offers from the outer nested list
        offers = (
            offers_nested[0]
            if offers_nested and isinstance(offers_nested, list)
            else []
        )

        for offer in offers:
            if offer.get("status") == "selected":
                return {
                    "selected": True,
                    "option": offer.get("option"),
                    "hotel_id": offer.get("hotel_id"),
                    "hotel_name": offer.get("name"),
                }

        return {"selected": False}

    except Exception as e:
        print(f"[get_selected_option_from_key] Error reading from Redis: {e}")
        return {"selected": False}

@tool
async def get_room_search_payload_from_key(convo_id: str):
    """
    This function retrieves the room search payload from Redis for the specified conversation ID.
    If the payload is not found or is empty, it returns None.
    """
    room_search_payload_key = f"hotel_booking:room_search_payload:{convo_id}"
    room_search_payload_details = await redis.json().get(room_search_payload_key, "$")

    if (
        not room_search_payload_details
        or not isinstance(room_search_payload_details, list)
        or not room_search_payload_details[0]
    ):
        return None

    return room_search_payload_details[0]

@tool
async def get_selected_rooms_from_key(convo_id: str) -> dict:
    """
    Check the hotel rooms in Redis and return all selected option if any.
    If no rooms are selected, return None.
    If rooms are selected, return a list of dictionaries with room names and their selected counts.
    """
    try:
        rooms_key = f"hotel_booking:rooms:{convo_id}"
        rooms_nested = await redis.json().get(rooms_key, "$")

        # Extract the list of offers from the outer nested list
        rooms = (
            rooms_nested[0] if rooms_nested and isinstance(rooms_nested, list) else []
        )

        rooms_selected = []
        for room in rooms:
            number_of_selected = room.get("number_of_selected")
            if number_of_selected != 0:
                rooms_selected.append(
                    {"name": room.get("name"), "number_of_selected": number_of_selected}
                )

        if not rooms_selected:
            return "No rooms selected."

        return '\n'.join(rooms_selected)

    except Exception as e:
        return "No rooms selected."

@tool
async def get_rooms_name(convo_id: str) -> list[str]:
    """
    Retrieve the list of room names for a given conversation ID from Redis.
    Args:
        convo_id: Unique identifier for the conversation.
    """
    try:
        rooms_key = f"hotel_booking:rooms:{convo_id}"
        rooms_nested = await redis.json().get(rooms_key, "$")

        # Check structure: should be a nested list
        if (
            not rooms_nested
            or not isinstance(rooms_nested, list)
            or not isinstance(rooms_nested[0], list)
        ):
    
            return "No room names found."

        rooms = rooms_nested[0]  # Extract the list of room dictionaries
        rooms_name = [room.get("name") for room in rooms if "name" in room]

        return "\n".join(rooms_name) if rooms_name else "No room names found."

    except Exception as e:
        return "Error retrieving room names."

@tool
async def mark_rooms_selected(
    convo_id: str, selected_option, additional_selected_count: int
):
    """
    Updates the number of rooms selected for a given option in Redis by adding to the current count.

    Args:
        convo_id: Unique identifier for the conversation.
        selected_option: The selected room option.
        additional_selected_count: The additional number of rooms to select.
    """
    try:
        if not convo_id or selected_option is None or additional_selected_count is None:
            raise ValueError(
                "Invalid input: 'convo_id', 'selected_option', and 'additional_selected_count' must be provided."
            )

        rooms_key = f"hotel_booking:rooms:{convo_id}"
        rooms = await redis.json().get(rooms_key, "$")

        if isinstance(rooms, list) and len(rooms) == 1 and isinstance(rooms[0], list):
            rooms = rooms[0]
            if not rooms or not isinstance(rooms, list):
                raise ValueError(f"No offers found for conversation ID {convo_id}.")

        idx = next(
            (i for i, o in enumerate(rooms) if o.get("name") == selected_option), None
        )
        if idx is None:
            raise ValueError(
                f"Option {selected_option} not found for conversation ID {convo_id}."
            )

        current_count = rooms[idx].get("number_of_selected", 0)

        new_count = current_count + additional_selected_count

        await redis.json().set(rooms_key, f"$[{idx}].number_of_selected", new_count)
        return f"Updated {selected_option} to {new_count} selected rooms."

    except Exception:
        return "Error updating selected rooms."

@tool
async def get_all_rooms_from_key(convo_id: str):
    try:
        if not convo_id:
            return "Invalid input 'convo_id', must be provided."

        rooms_key = f"hotel_booking:rooms:{convo_id}"
        rooms = await redis.json().get(rooms_key, "$")

        # Check if data exists and is in expected format
        if not rooms or not isinstance(rooms, list) or len(rooms) == 0:
            return None

        room_list = rooms[0]

        if not isinstance(room_list, list) or len(room_list) == 0:
            return None

        return "\n".join(room_list)

    except Exception:
        return "Error retrieving all rooms."
