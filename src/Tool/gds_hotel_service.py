from urllib.parse import urljoin
from crewai.tools import tool
import httpx

from schema.hotel_search_request_schema import HotelSearchRequest

from config.config import settings

          

        
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
