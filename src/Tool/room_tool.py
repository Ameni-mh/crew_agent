from Tool.redis_tool import change_option_status_hotel_offer, get_room_search_payload_from_key, is_selected_option_from_key, save_hotelDetails_room_options
from Tool.gds_hotel_service import search_details_specific_hotel
from crewai.tools import tool
from schema.hotel_details_request_schema import HotelDetailsRequest


async def save_hotelDetails_roomsOption(self, convo_id, hotelDetails_request: dict):
        """        
        Save the hotel details and room options to Redis. 
        Args:
            convo_id (str): Conversation ID to save the hotel details and room options.
            hotelDetails_request (dict): Hotel details and room options to save.
        """
        hotel_details = { 
            "id": hotelDetails_request.get("id"),
            "name": hotelDetails_request.get("name"),
            "city": hotelDetails_request.get("city"),
            "country": hotelDetails_request.get("country"),
            "address": hotelDetails_request.get("address"),
            "stars": hotelDetails_request.get("stars"),
            "ratings": hotelDetails_request.get("ratings"),
            "longitude": hotelDetails_request.get("longitude"),
            "latitude": hotelDetails_request.get("latitude"),
            "desc": hotelDetails_request.get("desc"),
            "img": hotelDetails_request.get("img"),
            "amenities": hotelDetails_request.get("amenities"),
            "supplier_name": hotelDetails_request.get("supplier_name"),
            "supplier_id": hotelDetails_request.get("supplier_id"),
            "checkin": hotelDetails_request.get("checkin"),
            "checkout": hotelDetails_request.get("checkout"),
            "policy": hotelDetails_request.get("policy"),
            "booking_age_requirement": hotelDetails_request.get(
                "booking_age_requirement"
            ),
            "cancellation": hotelDetails_request.get("cancellation"),
            "tax_percentage": hotelDetails_request.get("tax_percentage"),
            "hotel_phone": hotelDetails_request.get("hotel_phone"),
            "hotel_email": hotelDetails_request.get("hotel_email"),
            "hotel_website": hotelDetails_request.get("hotel_website"),
            "discount": hotelDetails_request.get("discount"),
        }

        rooms_options = []
        rooms = hotelDetails_request.get("rooms") or []
        for idx, room in enumerate(rooms):
            rooms_options.append({**room, "option": idx + 1, "number_of_selected": 0})
        try:
            await save_hotelDetails_room_options(convo_id, hotel_details, rooms_options)
            return "Hotel details and room options saved successfully."
        except Exception as e:
            return "Error saving hotel details and room options"

