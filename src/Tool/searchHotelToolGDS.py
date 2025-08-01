from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.schema.hotel_search_request_schema import HotelSearchRequest
import httpx
from urllib.parse import urljoin
from config.config import settings


class SearchHotelsFromGDS(BaseTool):
    name: str = "Search Hotels from GDS"
    description: str = "Search for available hotels via external GDS."
    args_schema: BaseModel = HotelSearchRequest

    async def _run(self, request) -> str:
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

        except httpx.HTTPStatusError:
            return "We ran into an issue finding hotels for you."