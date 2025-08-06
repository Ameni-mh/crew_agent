from urllib.parse import urljoin
import httpx
from typing import Optional
from schema.hotel_search_request_schema import HotelSearchRequest
import json
from config.config import settings
from langchain.tools.base import tool
from langchain_core.tools import InjectedToolCallId
from langchain_core.runnables import RunnableConfig
from schema.hotel_details_request_schema import HotelDetailsRequest
from Tool.redis_tool import save_hotel_search_options, save_hotelDetails_room_options
from Tool.room_tool import save_hotelDetails_roomsOption
from langgraph.types import Command
from typing import Annotated
from langgraph.prebuilt.chat_agent_executor import AgentState

@tool(name_or_callable="Lookup_hotels")     
async def Search_Hotels_From_GDS(convo_id:str, request : HotelSearchRequest,
                                 state: AgentState ) -> str:
        """Look up for available hotels via an external Global Distribution System (GDS).
            Args:
                conversationID (str): Unique identifier for the current conversation.
                request (HotelSearchRequest): Structured request containing hotel search parameters.
                state (AgentState) : state of agent
            Returns:
                str: A message containing the hotel search result or a notice indicating no availability.
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

            # Convert to dict for HTTP request
            params = request.model_dump(by_alias=True, exclude_none=True)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    urljoin(settings.gds_base_url, "/api/hotel_search"),
                    data=params,
                    headers={"x-api-key": settings.gds_api_key},
                )
                response.raise_for_status()
                response = response.json()
            
                await save_hotel_search_options(convo_id, response.get("response"), room_search_payload)
                #TODO: should verife if retrun list or no available
                #if not response.get("status") == "False":
                state["current_state"] = "\n".join(["Hotel option already saved",
                                                    "Focus on booking rooms,  and next steps."])
                print("current agent state :", state.get("current_state"))
                return json.dumps(response, indent=2)   

        except httpx.HTTPStatusError:
            return "We ran into an issue finding hotels for you."
        
        
@tool(name_or_callable="look_up_rooms_for_Hotel_Selected")
async def Search_Details_Specific_Hotel(convo_id : str, 
                                        request: HotelDetailsRequest,
                                        state: AgentState) -> str:
        """Look up rooms for specific hotel  via an external Global Distribution System (GDS).
            Args:
                conversationID (str): Unique identifier for the current conversation.
                request (HotelDetailsRequest): Structured request containing lookup rooms parameters.
                state (AgentState) : agent state
            Returns:
                str: A message containing the rooms result or a notice indicating no availability.
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

            hotel_details = { 
            "id": response.get("id"),
            "name": response.get("name"),
            "city": response.get("city"),
            "country": response.get("country"),
            "address": response.get("address"),
            "stars": response.get("stars"),
            "ratings": response.get("ratings"),
            "longitude": response.get("longitude"),
            "latitude": response.get("latitude"),
            "desc": response.get("desc"),
            "img": response.get("img"),
            "amenities": response.get("amenities"),
            "supplier_name": response.get("supplier_name"),
            "supplier_id": response.get("supplier_id"),
            "checkin": response.get("checkin"),
            "checkout": response.get("checkout"),
            "policy": response.get("policy"),
            "booking_age_requirement": response.get(
                "booking_age_requirement"
            ),
            "cancellation": response.get("cancellation"),
            "tax_percentage": response.get("tax_percentage"),
            "hotel_phone": response.get("hotel_phone"),
            "hotel_email": response.get("hotel_email"),
            "hotel_website": response.get("hotel_website"),
            "discount": response.get("discount"),
        }

            #rooms_options = []
            rooms = response.get("rooms") or []
            #for idx, room in enumerate(rooms):
               # rooms_options.append({**room, "option": idx + 1, "number_of_selected": 0})
            try:
                await save_hotelDetails_room_options(convo_id, hotel_details, rooms)
                state["current_state"] = "\n".join(["Room option of the hotel  already saved",
                                                    "Focus on booking confirmation, and next steps."])
                
            except Exception as e:
                return "Error saving hotel details and room options"
            
            return json.dumps(rooms, indent=2) 

        except Exception:
            return "We’re having trouble fetching room details for this hotel"
            

        
@tool(name_or_callable="Room_Booking_Confirmation")
async def send_shortlink_request_hotelBooking(accountID:str, conversationID : str, option: int, state: AgentState ) -> str:
        """ Generates a short booking link for a selected hotel via the GDS API, triggered when the user confirms their room selection.
        Arguments: 
            accountID (str): Unique identifier of the user account.
            conversationID (str): Unique identifier of the current conversation or session.
            option (int): Index corresponding to the selected hotel option.
            state(AgentState): Agent State 
        Returns: A str representing the generated short booking link."""
        gds_checkout_url = "http://localhost:4000/shortLink/"
        #"http://host.docker.internal:4000/shortLink/" 

        payload = {
            "conversationID": str(conversationID),
            "accountID": str(accountID),
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
                state["current_state"] = "\n".join([f"Room option for the hotel **{option}** has been confirmed.",
                                            "You may now proceed by asking the user about other needs, such as flight booking."])
                return link
        except httpx.HTTPStatusError:
            return "We’re having trouble creating a booking link."
