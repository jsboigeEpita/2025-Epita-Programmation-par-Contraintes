import openai
import time
import json
import os

class DistanceCalculator:
    """Calculates travel times between POIs using OpenAI API."""
    
    def __init__(self, api_key=None, use_api=True, batch_size=10):
        """Initialize the distance calculator with API key."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.use_api = use_api
        self.batch_size = batch_size
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        openai.api_key = self.api_key
        self.cache = {}  # Cache to store previous requests
        self.request_count = 0  # Counter for API requests
        self.request_queue = []  # Queue for batch requests
        
    def get_travel_time(self, origin, destination, mode):
        """Get travel time between two POIs."""
        # Create a cache key
        cache_key = f"{origin['ID']}-{destination['ID']}-{mode}"
        
        # Check if already in cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # If not using API, use haversine formula
        if not self.use_api:
            travel_time = self._fallback_travel_time(origin, destination, mode)
            self.cache[cache_key] = travel_time
            return travel_time
            
        # Add to request queue
        self.request_queue.append((origin, destination, mode, cache_key))
        
        # Process batch if queue reaches batch size
        if len(self.request_queue) >= self.batch_size:
            self._process_batch()
            
        # If the result is now in cache, return it
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # If not in cache yet, process this single request
        return self._process_single_request(origin, destination, mode)
    
    def _process_batch(self):
        """Process a batch of travel time requests."""
        if not self.request_queue:
            return
            
        # Define mode of transportation strings
        mode_strings = ["walking", "public transport", "car"]
        
        # Create a batch prompt
        batch_prompt = "Calculate travel times in minutes between multiple location pairs:\n\n"
        for i, (origin, destination, mode, _) in enumerate(self.request_queue):
            batch_prompt += f"Request {i+1}:\n"
            batch_prompt += f"  Origin: {origin['Nom']} at coordinates {origin['latitude']}, {origin['longitude']}\n"
            batch_prompt += f"  Destination: {destination['Nom']} at coordinates {destination['latitude']}, {destination['longitude']}\n"
            batch_prompt += f"  Mode: {mode_strings[mode]}\n\n"
            
        batch_prompt += "Respond with a JSON array of travel times in minutes. For example: [15, 25, 10, ...]"
            
        try:
            self.request_count += 1  # Count as one API request
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides precise travel time estimates."},
                    {"role": "user", "content": batch_prompt}
                ],
                temperature=0
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            try:
                # Try to parse the JSON response
                times = json.loads(content)
                
                # Add results to cache
                for i, (origin, destination, mode, cache_key) in enumerate(self.request_queue):
                    if i < len(times) and isinstance(times[i], (int, float)):
                        self.cache[cache_key] = int(times[i])
                    else:
                        # Fallback for missing or invalid results
                        self.cache[cache_key] = self._fallback_travel_time(origin, destination, mode)
                        
            except json.JSONDecodeError:
                # If JSON parsing fails, use fallback for all
                for origin, destination, mode, cache_key in self.request_queue:
                    self.cache[cache_key] = self._fallback_travel_time(origin, destination, mode)
                    
        except Exception as e:
            # On error, use fallback for all
            for origin, destination, mode, cache_key in self.request_queue:
                self.cache[cache_key] = self._fallback_travel_time(origin, destination, mode)
                
        # Clear the queue
        self.request_queue = []
        
    def _process_single_request(self, origin, destination, mode):
        """Process a single travel time request (original implementation)."""
        # Define mode of transportation
        mode_str = ["walking", "public transport", "car"][mode]
        
        # Create the API request
        prompt = (
            f"Calculate the travel time in minutes between two locations:\n"
            f"Origin: {origin['Nom']} at coordinates {origin['latitude']}, {origin['longitude']}\n"
            f"Destination: {destination['Nom']} at coordinates {destination['latitude']}, {destination['longitude']}\n"
            f"Mode of transportation: {mode_str}\n"
            f"Only respond with a single number representing the estimated travel time in minutes."
        )
        
        try:
            self.request_count += 1
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides precise travel time estimates."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            
            # Extract the travel time from the response
            travel_time = self._parse_time_from_response(response.choices[0].message.content)
            
            # Cache the result
            cache_key = f"{origin['ID']}-{destination['ID']}-{mode}"
            self.cache[cache_key] = travel_time
            
            return travel_time
            
        except Exception as e:
            # Return a fallback value
            fallback = self._fallback_travel_time(origin, destination, mode)
            cache_key = f"{origin['ID']}-{destination['ID']}-{mode}"
            self.cache[cache_key] = fallback
            return fallback
    
    def _parse_time_from_response(self, response_text):
        """Extract the travel time from API response."""
        try:
            # Try to extract just the number from the response
            time_str = ''.join(c for c in response_text if c.isdigit() or c == '.')
            return int(float(time_str))
        except:
            # If parsing fails, use a default value
            return 20
            
    def _fallback_travel_time(self, origin, destination, mode):
        """Calculate a fallback travel time if API fails."""
        # Simple calculation based on haversine distance
        import math
        
        # Convert latitude and longitude from degrees to radians
        lat1 = math.radians(origin['latitude'])
        lon1 = math.radians(origin['longitude'])
        lat2 = math.radians(destination['latitude'])
        lon2 = math.radians(destination['longitude'])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of Earth in kilometers
        distance = c * r
        
        # Estimate travel time based on mode
        speeds = [5, 15, 25]  # km/h for walking, public transport, car
        time_hours = distance / speeds[mode]
        return int(time_hours * 60)  # Convert to minutes
        
    def get_request_count(self):
        """Return the number of API requests made."""
        return self.request_count
        
    def flush_queue(self):
        """Force processing of any remaining items in the request queue."""
        if self.request_queue:
            self._process_batch()