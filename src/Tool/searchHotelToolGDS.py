from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from schema.hotel_search_request_schema import HotelSearchRequest
import httpx
from urllib.parse import urljoin
from config.config import settings
from Tool.redis_tool import save_hotel_search_options

class HotelSearchRequestWrapper(BaseModel):
    request: HotelSearchRequest
    convo_id: str
    
class SearchHotelsFromGDS(BaseTool):
    name: str = "Search Hotels from GDS"
    description: str = "Search for available hotels via external GDS."
    args_schema: BaseModel = HotelSearchRequestWrapper

    async def _run(self, request : HotelSearchRequest, convo_id:str) -> str:
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
                return response.dump(by_alias=True, exclude_none=True)     

        except httpx.HTTPStatusError:
            return "We ran into an issue finding hotels for you."