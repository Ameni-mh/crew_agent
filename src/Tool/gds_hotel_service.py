from urllib.parse import urljoin
from fastapi import Request
import httpx
from schema.hotel_search_request_schema import HotelSearchRequest
import json
from config.config import settings
from langchain.tools.base import tool
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId
from schema.hotel_details_request_schema import HotelDetailsRequest
from Tool.redis_tool import save_hotel_search_options, save_hotelDetails_room_options
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from typing import Annotated
from schema.agent_context import AgentContext
from schema.hotel_details_request_output import HotelDetailsRequestOutput
from schema.hotel_search_request_output import HotelRequestOutput
from model.generalModel import GeneralPreferencesModel
from model.hotelPreferencesModel import HotelPreferencesModel

@tool(name_or_callable="Lookup_hotels")     
async def Search_Hotels_From_GDS(state: Annotated[AgentContext, InjectedState],
                                 request : HotelSearchRequest,
                                 tool_call_id: Annotated[str, InjectedToolCallId],
 ) :
        """Look up for available hotels via an external Global Distribution System (GDS).
            Args:
                state (AgentContext): Current state of the agent, injected by the framework.
                request (HotelSearchRequest): Structured request containing hotel search parameters.
                tool_call_id (str): Identifier for this tool call
            Returns:
                Command: Contains hotel search results and updated agent state
        """
        
        try:

            room_search_payload = {
                    "checkin": request.checkin,
                    "checkout": request.checkout,
                    "adults": getattr(request, "adults", 1),
                    "childs": getattr(request, "childs", 0),
                    "child_age": getattr(request, "childs_age", 0),
                    "rooms": request.rooms,
                    "language": getattr(request, "language", "en"),
                    "currency": getattr(request, "currency", ""),
                    "nationality":request.nationality,
                }

            
            params = request.model_dump(by_alias=True, exclude_none=True)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    urljoin(settings.gds_base_url, "/api/hotel_search"),
                    data=params,
                    headers={"x-api-key": settings.gds_api_key},
                )
                response.raise_for_status()
                response = response.json()

            
                if  response.get("status") :  
                    offers = []
                    list_hotels = response.get("response")

                    pydanctic_hotels = [HotelRequestOutput(**hotel) for hotel in list_hotels]

                    for idx, hotel in enumerate(list_hotels):
                        offers.append({**hotel, "option": idx + 1, "status": "unselected"})
                
                    await save_hotel_search_options(state["conversation_id"], offers, room_search_payload)

                    full_hotel_search = "\n".join(
                    "\n".join([
                        f"Hotel id : {hotel.hotel_id} - name : {hotel.name} - Starts :  {hotel.stars} - actual_price_per_night : {hotel.actual_price_per_night} - address:{hotel.address}",
                        f"image : {hotel.img}  - rating : {hotel.rating} - location : {hotel.location} - latitude : {hotel.latitude} - longitude : {hotel.longitude}",
                        f"currency : {hotel.currency} - booking_currency : {hotel.booking_currency} - service_fee : {hotel.service_fee} - supplier_name : {hotel.supplier_name} - supplier_id : {hotel.supplier_id} - redirect : {hotel.redirect}",
                        f"booking_data : {json.dumps(hotel.booking_data, indent=2)} - color : {hotel.color}"]
                         )
                    for idx, hotel in enumerate(pydanctic_hotels)
                    )

                    hotel_list_str = "\n".join(
                    f"Hotel id : {hotel['hotel_id']} - name : {hotel['name']} - Starts :  {hotel['stars']}⭐ - actual_price_per_night : {hotel['actual_price_per_night']} - address:{hotel['address']}"
                    for idx, hotel in enumerate(list_hotels)
                    )
                    

                    note = "Note: just present 5 hotels au Maximum and Doestn't forget to present price and starts to the user"
                    
                    return Command(update={
                        "room_search_payload": room_search_payload,
                        "hotels": full_hotel_search ,
                        "messages": [
                            ToolMessage(
                                hotel_list_str+"\n"+note,
                                tool_call_id=tool_call_id
                            )
                        ]
                    })
                else: 
                    return response.get("message")

        except httpx.HTTPStatusError:
            return "We ran into an issue finding hotels for you." 

@tool(name_or_callable="hotel_memory")
async def memory_gds_data(state: Annotated[AgentContext, InjectedState]
) -> str:
    """
    Retrieves previously stored Global Distribution System (GDS) search and payload data from memory.

    This tool is used to access information saved during earlier stages of the booking process,
    allowing other tools or prompts to reuse these details without re-querying the GDS.
    Returns:
        str: Contains:
            - room_search_payload (dict): The original payload used for the room search if available.
            - available_hotels (list): A list of hotels returned by the previous search if available.
    """
    
    memory = []
    if state["room_search_payload"]:
          memory.append("Room Search Payload : \n"+json.dumps(state["room_search_payload"], indent=2))

    if state["hotels"] :
         memory.append(f" Available hotels : \n {state['hotels']}")
  

    if not state["hotels"] and not state["room_search_payload"]:
         return "No memory of any list yet"
    
    return "\n".join(memory)
        
@tool(name_or_callable="look_up_rooms_for_Hotel_Selected")
async def Search_Details_Specific_Hotel(state: Annotated[AgentContext, InjectedState], 
                                        request: HotelDetailsRequest) -> str:
        """Look up rooms for specific hotel  via an external Global Distribution System (GDS).
            Args:
                state (AgentContext): Current state of the agent, injected by the framework.
                request (HotelDetailsRequest): Structured request containing lookup rooms parameters.
                tool_call_id (str): Identifier for this tool call
            Returns:
                Command: Contains the rooms search results and updated agent state.
        """
        try:
            
            # Convert to dict for HTTP request
            params = request.model_dump(by_alias=True, exclude_none=True)

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    urljoin(settings.gds_base_url, "/api/hotel_details"),
                    data=params,
                    headers={"x-api-key": ""},
                )
            response.raise_for_status()
            response = response.json()

            response_pydantic = HotelDetailsRequestOutput(**response)

            hotel_details = { 
            "id": response_pydantic.id,
            "name": response_pydantic.name,
            "city": response_pydantic.city,
            "country": response_pydantic.country,
            "address": response_pydantic.address,
            "stars": response_pydantic.stars,
            "ratings": response_pydantic.ratings,
            "longitude": response_pydantic.longitude,
            "latitude": response_pydantic.latitude,
            "desc": response_pydantic.desc,
            "img": response_pydantic.img,
            "amenities": response_pydantic.amenities,
            "supplier_name": response_pydantic.supplier_name,
            "supplier_id": response_pydantic.supplier_id,
            "checkin": response_pydantic.checkin,
            "checkout": response_pydantic.checkout,
            "policy": response_pydantic.policy,
            "booking_age_requirement": response_pydantic.booking_age_requirement,
            "cancellation": response_pydantic.cancellation,
            "tax_percentage": response_pydantic.tax_percentage,
            "hotel_phone": response_pydantic.hotel_phone,
            "hotel_email": response_pydantic.hotel_email,
            "hotel_website": response_pydantic.hotel_website,
            "discount": response_pydantic.discount,
        }

            #rooms_options = []
            rooms = response.get("rooms") or []
            #for idx, room in enumerate(rooms):
               # rooms_options.append({**room, "option": idx + 1, "number_of_selected": 0})
            try:
                await save_hotelDetails_room_options(state["conversation_id"], hotel_details, rooms)
                                
            except Exception as e:
                return "Error saving hotel details and room options"
            
            note = "NOTE: The following rooms are available, doestn't forget to present price and amenties to the user"
    
            return json.dumps(rooms, indent=2)+"\n"+note,

        except Exception as e:
            print("Error during hotel room search:", str(e))
            return "We’re having trouble fetching room details for this hotel"
            

        
@tool(name_or_callable="Room_Booking_Confirmation")
async def send_shortlink_request_hotelBooking(state: Annotated[AgentContext, InjectedState],
                                              option: int, tool_call_id: Annotated[str, InjectedToolCallId]) :
        """ Generates a short booking link for a selected hotel via the GDS API, triggered when the user confirms their room selection.
        Arguments: 
            state (AgentContext): Current state of the agent, injected by the framework.
            option (int): Index corresponding to the selected hotel option.
            tool_call_id (str): Identifier for this tool call
        Returns: A Command representing the generated short booking link and updated agent state."""
        gds_checkout_url = "http://localhost:4000/shortLink/"
        

        payload = {
            "conversationID": state["conversation_id"],
            "accountID": state["account_id"],
            "option": int(option),
            "type": "hotel_booking",
        }
        
        headers = {"Content-Type": "application/json", "x-api-key": settings.gds_api_key}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    gds_checkout_url, json=payload, headers=headers
                )
                response.raise_for_status()
                checkout_info = response.json()
                link = (
                        checkout_info.get(
                            "url"
                        )  # First try 'url', which is the actual field
                        or checkout_info.get("checkout_link")
                        or checkout_info.get("link")
                    )

                if not link:
                    return "We’re having trouble creating a booking link."
                
                context= "\n".join([f"Room option for the hotel **{option}** has been confirmed.",
                            "You may now present link and proceed by asking the user about other needs, such as flight booking or re-booking another hotel."])
                return Command(update={
                        "messages": [
                            ToolMessage(
                                context+"\n"+link,
                                tool_call_id=tool_call_id
                            )
                        ]
                    })
        except httpx.HTTPStatusError:
            return "We’re having trouble creating a booking link."
        
@tool(name_or_callable="get_hotel_preferences")
async def get_hotel_preferences(user_id: str):
    """Fetches hotel and general preferences from the database.
    Args:
        user_id (str): Unique identifier for the user."""
    general_pref_model = await GeneralPreferencesModel.create_instance(db_client=Request.app.db_client)
    general_preferences = await general_pref_model.get_generalPreferences_perUser(
        general_user_id= user_id 
    )

    hotel_pref_model = await HotelPreferencesModel.create_instance(db_client=Request.app.db_client)
    hotel_preferences = await hotel_pref_model.get_hotelPreferences_perUser(hotel_user_id=user_id)

    if not hotel_preferences and not general_preferences:
        return "No hotel or general preferences found for this user."
    
    hotel = hotel_preferences.model_dump(by_alias=True, exclude_none=True) if hotel_preferences else "No hotel preferences found for this user."
    general = general_preferences.model_dump(by_alias=True, exclude_none=True) if general_preferences else "No general preferences found for this user."
    return f"hotel_preferences: {hotel} \n general_preferences: {general}"
    
