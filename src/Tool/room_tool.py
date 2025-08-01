from Tool.redis_tool import save_hotelDetails_room_options
from crewai.tools import tool



async def save_hotelDetails_roomsOption(convo_id, hotelDetails_data: dict):
        """        
        Save the hotel details and room options to Redis. 
        Args:
            convo_id (str): Conversation ID to save the hotel details and room options.
            hotelDetails_request (dict): Hotel details and room options to save.
        """
        hotel_details = { 
            "id": hotelDetails_data.get("id"),
            "name": hotelDetails_data.get("name"),
            "city": hotelDetails_data.get("city"),
            "country": hotelDetails_data.get("country"),
            "address": hotelDetails_data.get("address"),
            "stars": hotelDetails_data.get("stars"),
            "ratings": hotelDetails_data.get("ratings"),
            "longitude": hotelDetails_data.get("longitude"),
            "latitude": hotelDetails_data.get("latitude"),
            "desc": hotelDetails_data.get("desc"),
            "img": hotelDetails_data.get("img"),
            "amenities": hotelDetails_data.get("amenities"),
            "supplier_name": hotelDetails_data.get("supplier_name"),
            "supplier_id": hotelDetails_data.get("supplier_id"),
            "checkin": hotelDetails_data.get("checkin"),
            "checkout": hotelDetails_data.get("checkout"),
            "policy": hotelDetails_data.get("policy"),
            "booking_age_requirement": hotelDetails_data.get(
                "booking_age_requirement"
            ),
            "cancellation": hotelDetails_data.get("cancellation"),
            "tax_percentage": hotelDetails_data.get("tax_percentage"),
            "hotel_phone": hotelDetails_data.get("hotel_phone"),
            "hotel_email": hotelDetails_data.get("hotel_email"),
            "hotel_website": hotelDetails_data.get("hotel_website"),
            "discount": hotelDetails_data.get("discount"),
        }

        rooms_options = []
        rooms = hotelDetails_data.get("rooms") or []
        for idx, room in enumerate(rooms):
            rooms_options.append({**room, "option": idx + 1, "number_of_selected": 0})
        try:
            await save_hotelDetails_room_options(convo_id, hotel_details, rooms_options)
            return "Hotel details and room options saved successfully."
        except Exception as e:
            return "Error saving hotel details and room options"

