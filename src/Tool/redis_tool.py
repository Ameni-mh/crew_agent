from typing import Optional
from redis.asyncio import Redis
from config.config import settings
from langchain.tools.base import tool

redis_url = settings.redis_url
redis = Redis.from_url(redis_url, decode_responses=True)
    

async def save_hotel_search_options(convo_id:str, offers: list,room_search_payload :dict ) -> str:
    """
    Save hotel offer options and guest information to Redis.
    Call this tool before searching for hotels with this tool ``search_hotels_from_GDSAgregator_async``.
    
    Args: 
        input (dict): Contains the following keys:
        - convo_id (str): Unique conversation identifier
        - offers (list): List of hotel offers returned from the GDS aggregator.
        - Room Search Payload (dict): Serialized Pydantic model RoomSearchPayload 
    
    Returns:
        str: Success or error message
    """
    try:

        if not convo_id or not isinstance(offers, list) or not isinstance(room_search_payload, dict):
            return "Invalid input: Missing or improperly formatted fields."

        # Add indexing to offers for selection tracking
        options = [
            {**offer, "option": idx + 1, "status": "unselected"}
            for idx, offer in enumerate(offers)
        ]

        offers_key = f"hotel_booking:offers:{convo_id}"
        payload_key = f"hotel_booking:room_search_payload:{convo_id}"

        await redis.json().set(offers_key, "$", options)
        await redis.json().set(payload_key, "$", room_search_payload)

        return "Hotel search options saved successfully."
    except Exception as e:
        return f"Error saving hotel search options: {str(e)}"


async def save_hotelDetails_room_options(convo_id, hotelDetails, roomsOption):
    """
    Save hotel details and available room options to Redis.
    
    Args:
        convo_id (str): Unique conversation identifier
        hotelDetails (dict): Hotel information including description, policies, and cancellation rules
        roomsOption (list): List of available room options with their details
    
    Returns:
        str: Success or error message
    """
    try:
        rooms_key = f"hotel_booking:rooms:{convo_id}"
        hotelDetails_key = f"hotel_booking:hotelDetails:{convo_id}"

        await redis.json().set(rooms_key, "$", roomsOption)
        await redis.json().set(hotelDetails_key, "$", hotelDetails)
        return "Hotel details and room options saved successfully."
    except Exception as e:
        return "Error saving hotel details and room options."

@tool(name_or_callable="hotel_option_from_redis")
async def get_hotel_search_options(convo_id: str) -> list:
    """
    Retrieve saved hotel options options from Redis.
    Args:
        convo_id (str): Unique conversation identifier
    Returns:
        list: List of hotel offers, or error message if not found
    """
    offers_key = f"hotel_booking:offers:{convo_id}"
    offers = await redis.json().get(offers_key, "$")

    if not offers or not isinstance(offers, list):
        return "No offers found for this conversation."
    
    return "/n".join(offers)


async def change_option_status_hotel_offer(
    convo_id: str,
    selected_option: int,
    status: str = "selected"
) -> str:
    """
    Change the status of a selected hotel offer in Redis.
    
    Args:
        convo_id (str): Conversation ID to identify the hotel offers
        selected_option (int): The option number/ID to change status for (Required)
        status (str, optional): Either "selected" or "unselected". Defaults to "selected"
    
    Returns:
        str: Status of the operation ("selected", "unselected", or error message)
    
    Example:
        >>> await change_option_status_hotel_offer(convo_id="conv123", selected_option="option1")
        'selected'
    """
    if not convo_id or not selected_option:
        return "Error: convo_id and selected_option are required"

    offers_key = f"hotel_booking:offers:{convo_id}"

    # Get the nested offers list from Redis
    try:
        offers_nested = await redis.json().get(offers_key, "$")
        if not offers_nested or not isinstance(offers_nested, list):
            return "No offers found for this conversation."

        offers = offers_nested[0] if isinstance(offers_nested[0], list) else offers_nested

        # Find index of the selected option
        idx = next(
            (i for i, o in enumerate(offers) if str(o.get("option")) == str(selected_option)), 
            None
        )
        if idx is None:
            return f"Option '{selected_option}' not found."

        if status == "selected":
            # Mark only the selected offer as "selected", all others "unselected"
            for i, offer in enumerate(offers):
                offer["status"] = "selected" if i == idx else "unselected"
            await redis.json().set(offers_key, "$", offers)
            return "selected"

        if status == "unselected":
            offers[idx]["status"] = "unselected"
            await redis.json().set(offers_key, "$", offers)
            return "unselected"

        return "Invalid status value."

    except Exception as e:
        print(f"Error changing option status: {e}")
        return f"Error: {str(e)}"


async def selected_option_from_key(convo_id: str) -> dict:
    """
    Retrieve the currently selected hotel option from Redis.
    
    Args:
        convo_id (str): Unique conversation identifier
    
    Returns:
        dict: {
            'selected': bool,
            'option': str,
            'hotel_id': str,
            'hotel_name': str
        } or {'selected': False} if none selected
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
                answer = "\n".join([
                    f"The offer with option ID '{offer ['option']}' for hotel '{offer['hotel_name']}' "
                    f"(Hotel ID: {offer ['hotel_id']}) has been selected."
                ]
)
                return answer

        return "has not been selected"

    except Exception as e:
        return "Error reading from Redis"


async def get_room_search_payload_from_key(convo_id: str):
    """
    Retrieve the room search criteria and guest preferences from Redis.
    
    Args:
        convo_id (str): Unique conversation identifier
    
    Returns:
        dict: Room search parameters or None if not found
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


async def get_selected_rooms_from_key(convo_id: str) -> dict:
    """
    Retrieve all selected rooms and their quantities from Redis.
    
    Args:
        convo_id (str): Unique conversation identifier
    
    Returns:
        str: Formatted string of selected rooms and quantities, or error message
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


async def get_rooms_name(convo_id: str) -> list[str]:
    """
    Retrieve list of available room names for a hotel.
    
    Args:
        convo_id (str): Unique conversation identifier
    
    Returns:
        str: Newline-separated list of room names or error message
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


async def mark_rooms_selected(convo_id: str, selected_option:str, additional_selected_count: int):
    """
    Update the quantity of selected rooms for a specific room type.
    
    Args:
        convo_id (str): Unique conversation identifier
        selected_option (str): Room type/name to update
        additional_selected_count (int): Number of additional rooms to select
    
    Returns:
        str: Confirmation message with updated count or error message
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

@tool(name_or_callable="rooms_option_from_redis")
async def get_all_rooms_from_key(convo_id: str):
    """
    Retrieve complete information for all available rooms of last selected hotel.
    Args:
        convo_id (str): Unique conversation identifier
    Returns:
        str: Formatted string containing all room details or error message
    """
    try:
        if not convo_id:
            return "Invalid input 'convo_id', must be provided."

        rooms_key = f"hotel_booking:rooms:{convo_id}"
        rooms = await redis.json().get(rooms_key, "$")

        # Check if data exists and is in expected format
        if not rooms or not isinstance(rooms, list) or len(rooms) == 0:
            return "No rooms found for this conversation."

        room_list = rooms[0]

        if not isinstance(room_list, list) or len(room_list) == 0:
            return "No rooms found."

        return "\n".join(room_list)

    except Exception:
        return "Error retrieving all rooms."
