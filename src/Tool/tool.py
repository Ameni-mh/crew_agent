
from crewai.tools import tool
from datetime import datetime
from langdetect import detect
import httpx

from schema.hotel_search_request_schema import HotelSearchRequest

@tool
def validate_field_tool(llm_data_extracted: dict):
    """
    Validates hotel search parameters and requirements.
    
    Args:
        llm_data_extracted (dict): Dictionary containing hotel search parameters        

    Returns:
        str: "valid" if all validations pass, otherwise returns missing/invalid fields
    """

    city = llm_data_extracted.get("city")
    nationality = llm_data_extracted.get("nationality")
    childs = llm_data_extracted.get("childs")
    child_age = llm_data_extracted.get("child_age")
    price_from = llm_data_extracted.get("price_from")
    price_to = llm_data_extracted.get("price_to")
    adults = llm_data_extracted.get("adults")
    rooms = llm_data_extracted.get("rooms")

    today_str = datetime.now().strftime("%d-%m-%Y")
    checkin_str = llm_data_extracted.get("checkin")
    checkout_str = llm_data_extracted.get("checkout")

    today = datetime.strptime(today_str, "%d-%m-%Y").date()
    checkin= datetime.strptime(checkin_str, "%d-%m-%Y").date()
    checkout= datetime.strptime(checkout_str, "%d-%m-%Y").date()

    missing = []

    if not city:
        missing.append("the city where you want to stay")
    if city == "unknown":
        missing.append("a valid city name")
    if not checkin:
        missing.append("your check-in date")
    if not checkout:
        missing.append("your check-out date")
    if not nationality:
        missing.append("your nationality")
    if (adults and adults > 1 or childs and childs > 0) and rooms == 1:
        missing.append("how many rooms you need for your group")
    if checkin and checkout and checkin > checkout:
        missing.append("a check-in date earlier than the check-out date")
    if checkin and checkin < today:
        missing.append("a check-in date that is not in the past")
    if checkout and checkout < today:
        missing.append("a check-out date that is not in the past")
    if (childs == 0 and child_age != 0) or (childs != 0 and child_age == 0):
        missing.append("valid child age (should be 0 if there are no children)")
    if childs and childs > 0 and (child_age < 0 or child_age > 17):
        missing.append("a child age between 0 and 17")
    if price_from is not None and price_to is not None and price_from > price_to:
        missing.append("a maximum price that is higher than the minimum price")

    if not missing:
        return "valid"

    return '\n'.join(missing)

@tool
def detect_language_tool(message: str):
      """
        Detects the language of user input for multilingual support.
        
        Args:
            message (str): User's input text message
            
        Returns:
            str: ISO 639-1 language code (e.g., 'en' for English, 'es' for Spanish)
        
        """
      return detect(message)

@tool
async def search_hotels_from_GDSAgregator(request: dict ):
        """
    Searches for available hotels using GDS (Global Distribution System) API.
    
    Args:
        request (dict): Search criteria following HotelSearchRequest schema
            
    
    Returns:
        dict: JSON response containing:
            - Available hotels matching criteria
            
    Raises:
        httpx.ReadTimeout: If the API request times out
        httpx.HTTPStatusError: If the API returns an error status
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
                    "https://phptravels.net/api/hotel_search",
                    data=params,
                    headers={"x-api-key": ""}
                )
                response.raise_for_status()
                response = response.json()
                return response

        except httpx.ReadTimeout:
            raise


        except httpx.HTTPStatusError as e:
            raise

        except Exception as e:
          raise
