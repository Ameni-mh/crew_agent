from crewai.tools import BaseTool
import httpx
from pydantic import BaseModel, Field
from urllib.parse import urljoin
from config.config import settings
from schema.hotel_details_request_schema import HotelDetailsRequest

class SearchDetailsSpecificHotel(BaseTool):
    name: str = "Search Details Specific Hotel"
    description: str = "Search for specific hotel details using GDS API."
    args_schema: BaseModel = HotelDetailsRequest

    async def _run(self, request: str) -> str:
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
            

        
