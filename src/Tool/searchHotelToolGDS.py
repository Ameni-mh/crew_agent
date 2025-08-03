import json
from typing import Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from schema.hotel_search_request_schema import HotelSearchRequest
import httpx
from urllib.parse import urljoin
from config.config import settings


class HotelSearchRequestWrapper(BaseModel):
    request: HotelSearchRequest = Field(..., description="any date before put it in this schema be (DD-MM-YYYY)  ")
    
    
class SearchHotelsFromGDS(BaseTool):
    name: str = "Search Hotels from GDS"
    description: str = "Search for available hotels via external GDS."
    args_schema: BaseModel = HotelSearchRequest 

    async def _run(self, 
                    city: str,
                    checkin: str,
                    checkout: str,
                    nationality: str,
                    adults: Optional[int] = 1, 
                    childs: Optional[int] = 0,   
                    rooms: Optional[int] = 1,   
                    language: Optional[str] = "en",
                    currency: Optional[str] = "USD",
                    child_age: Optional[int] = 0,
                    pagination: Optional[int] = 1,
                    price_from: Optional[int] = None,
                    price_to: Optional[int] = None,
                    ip: Optional[str] = None,
                    module_name: Optional[str] = "hotels",
                    rating: Optional[int] = None,
                    user_type: Optional[str] = None
                   ) -> str:
        
        request = HotelSearchRequest(
            city=city,
            checkin=checkin,
            checkout=checkout,
            nationality=nationality,
            adults=adults,
            childs=childs,
            rooms=rooms,
            language=language,
            currency=currency,
            child_age=child_age,
            pagination=pagination,
            price_from=price_from,
            price_to=price_to,
            ip=ip,
            module_name=module_name,
            rating=rating,
            user_type=user_type
        )
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
            
                #await save_hotel_search_options(convo_id, response.get("response"), room_search_payload)
                return json.dumps(response, indent=2)   

        except httpx.HTTPStatusError:
            return "We ran into an issue finding hotels for you."