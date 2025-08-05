from urllib.parse import urljoin
import httpx
from typing import Optional
from schema.hotel_search_request_schema import HotelSearchRequest
import json
from config.config import settings
from langchain.tools.base import tool

from schema.hotel_details_request_schema import HotelDetailsRequest
from Tool.redis_tool import save_hotel_search_options



@tool      
async def Search_Hotels_From_GDS( request : HotelSearchRequest, convo_id:str) -> str:
        """Search for available hotels via external GDS."""
        
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
                return json.dumps(response, indent=2)   

        except httpx.HTTPStatusError:
            return "We ran into an issue finding hotels for you."
        

async def Search_Details_Specific_Hotel(request: HotelDetailsRequest) -> str:
        """Search for specific hotel details using GDS API."""
        try:
            
            # Convert to dict for HTTP request
            params = request.model_dump(by_alias=True, exclude_none=True)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    urljoin(settings.gds_base_url, "/api/hotel_details"),
                    data=params,
                    headers={"x-api-key": ""},
                )
            response.raise_for_status()
            response = response.json()
            #await save_hotelDetails_roomsOption(convo_id, response)
            return response.dump(by_alias=True, exclude_none=True)

        except (httpx.ReadTimeout, httpx.HTTPStatusError, Exception):
            return "We’re having trouble fetching room details for this hotel"
            

        

async def send_shortlink_request_hotelBooking(accountID:str, conversationID : str, option: int ) -> str:
        """ Sends a request to the GDS API to generate a short booking link for a selected hotel.
        Arguments: 
            accountID (str): The unique identifier of the user account.
            conversationID (str): The unique identifier of the current conversation or session.
            option (int): The index or number corresponding to the selected hotel option.
        Returns: A str representing the generated short booking link."""
        gds_checkout_url = (urljoin(settings.gds_base_url, "/shortLink"),)

        payload = {
            "conversationID": str(conversationID),
            "accountID": str(accountID),
            "option": int(option),
            "type": "hotel_booking",
        }

        headers = {"Content-Type": "application/json", "x-api-key": self.GDS_API_KEY}

        try:
            async with httpx.AsyncClient() as client:
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
                return link
        except httpx.HTTPStatusError:
            return "We’re having trouble creating a booking link."
