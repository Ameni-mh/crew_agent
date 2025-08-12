from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from urllib.parse import urljoin
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

#load_dotenv(".env")

# Create an MCP server
mcp = FastMCP(
    name="Hotels",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8055,  # only used for SSE transport (set this to any port)
    stateless_http=True,
)

@mcp.tool(name="Lookup_hotels")     
async def Search_Hotels_From_GDS(convo_id:str, request : HotelSearchRequest,
                                 tool_call_id: Annotated[str, InjectedToolCallId],
 ) :
        """Look up for available hotels via an external Global Distribution System (GDS).
            Args:
                conversationID (str): Unique identifier for the current conversation.
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

                
                print("status: ", type(response.get("status")), response.get("message"))
                if  response.get("status") :  
                    offers = []
                    list_hotels = response.get("response")
                    for idx, hotel in enumerate(list_hotels):
                        offers.append({**hotel, "option": idx + 1, "status": "unselected"})
                
                    await save_hotel_search_options(convo_id, offers, room_search_payload)  
                    
                    return Command(update={
                        "room_search_payload": room_search_payload,
                        "hotels": response.get("response"),
                        "messages": [
                            ToolMessage(
                                json.dumps(response, indent=2),
                                tool_call_id=tool_call_id
                            )
                        ]
                    })
                else: 
                    return response.get("message")

        except httpx.HTTPStatusError:
            return "We ran into an issue finding hotels for you." 

@mcp.tool(name="hotel_memory")
async def memory_gds_data(state: Annotated[AgentContext, InjectedState]
) ->str:
    """
    Retrieves previously stored Global Distribution System (GDS) search and payload data of hotels from memory.

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
         memory.append("Hotels:\n" + json.dumps(state["hotels"], indent=2))
  

    if not state["hotels"] and not state["room_search_payload"]:
         return "No memory of any list yet"
    
    return "\n".join(memory)
        
@mcp.tool(name="look_up_rooms_for_Hotel_Selected")
async def Search_Details_Specific_Hotel(convo_id : str, 
                                        request: HotelDetailsRequest) -> str:
        """Look up rooms for specific hotel  via an external Global Distribution System (GDS).
            Args:
                conversationID (str): Unique identifier for the current conversation.
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
                                
            except Exception as e:
                return "Error saving hotel details and room options"
    
            return json.dumps(rooms, indent=2)

        except Exception:
            return "We’re having trouble fetching room details for this hotel"
            

        
@mcp.tool(name="Room_Booking_Confirmation")
async def send_shortlink_request_hotelBooking(accountID:str, conversationID : str,
                                               option: int, tool_call_id: Annotated[str, InjectedToolCallId]) :
        """ Generates a short booking link for a selected hotel via the GDS API, triggered when the user confirms their room selection.
        Arguments: 
            accountID (str): Unique identifier of the user account.
            conversationID (str): Unique identifier of the current conversation or session.
            option (int): Index corresponding to the selected hotel option.
            tool_call_id (str): Identifier for this tool call
        Returns: A Command representing the generated short booking link and updated agent state."""
        gds_checkout_url = "http://localhost:4000/shortLink/"
        

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



# Run the server
if __name__ == "__main__":
    transport = "stdio"
    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse")
    elif transport == "streamable-http":
        print("Running server with Streamable HTTP transport")
        mcp.run(transport="streamable-http")
    else:
        raise ValueError(f"Unknown transport: {transport}")
