from dbm import _error
from urllib.parse import urljoin
from crewai.tools import tool
import httpx

from src.schema.hotel_search_request_schema import HotelSearchRequest

from config.config import settings


@tool
async def search_hotels_from_GDSAgregator(
         request: HotelSearchRequest | dict
    ) -> dict:
        """
        Search for available hotels via external GDS.
        Formats the request, handles timeouts and HTTP errors gracefully.
        """
        try:
            # Convert dict to Pydantic model if necessary
            if isinstance(request, dict):
                gds_query = HotelSearchRequest(**request)
            else:
                gds_query = request

            gds_query.module_name = "hotels"

            # Convert to dict for HTTP request
            params = gds_query.model_dump(by_alias=True, exclude_none=True)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    urljoin(settings.gds_base_url, "/api/hotel_search"),
                    data=params,
                    headers={"x-api-key": settings.gds_api_key},
                )
                response.raise_for_status()
                response = response.json()
                return response.dump(by_alias=True, exclude_none=True)

        except httpx.ReadTimeout:
            return " Looks like our hotel search is taking a break. Please try again soon!"
            

        except httpx.HTTPStatusError:
            return "Sorry! We ran into an issue finding hotels for you. Could you try again a little later?"
            

        except Exception:
            return "Oops! Something went wrong while searching for hotels. Please try again in a moment."
            
@tool
async def search_details_specific_hotel(self, request: HotelSearchRequest):
        """"Search for specific hotel details using GDS API.
        Args:
            request (HotelSearchRequest): Search criteria following HotelSearchRequest schema"""
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
                return response.dump(by_alias=True, exclude_none=True)

        except (httpx.ReadTimeout, httpx.HTTPStatusError, Exception):
            return "We’re having trouble fetching room details for this hotel"
            

        
@tool
async def send_shortlink_request_hotelBooking(self, conversationID, option, accountID):
        """ Sends a request to the GDS API to create a short link for hotel booking."""
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
