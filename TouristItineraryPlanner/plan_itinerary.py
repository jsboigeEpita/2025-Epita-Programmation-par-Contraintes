#!/usr/bin/env python3
import sys
import os
import json
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv
from src.solver import TouristItinerarySolver
from flask import Flask, request, jsonify, render_template

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.CRITICAL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("=" * 50)
logger.info("Tourist Itinerary Planner starting up")
logger.info("=" * 50)

app = Flask(__name__, template_folder='templates', static_folder='static')

def _simple_poi_matching(mandatory_pois_text, poi_data):
    """Simple string matching for POIs"""
    mandatory_poi_ids = []
    requested_pois = [poi.strip().lower() for poi in mandatory_pois_text.split(",")]
    for requested_poi in requested_pois:
        for poi in poi_data:
            if requested_poi in poi["name"].lower():
                mandatory_poi_ids.append(poi["id"])
                break
    return mandatory_poi_ids

def identify_mandatory_pois(city, mandatory_pois_text, api_key=None):
    """Use LLM to match user-entered POI names to actual POI IDs in the database"""
    logger.info(f"Identifying mandatory POIs for {city}: {mandatory_pois_text}")
    
    if not api_key:
        logger.warning("No API key provided for LLM matching of mandatory POIs")
        return []
        
    try:
        # Load the city graph to get actual POIs
        from data.city_graph import load_graph
        city_graph = load_graph(city.lower())
        
        if not city_graph:
            logger.warning(f"No graph found for {city}, cannot match mandatory POIs")
            return []
            
        # Create a list of POIs with their IDs and names
        poi_data = []
        for node_id, node_data in city_graph.nodes(data=True):
            poi_data.append({
                "id": node_id,
                "name": node_data.get('Nom', ''),
                "type": node_data.get('Type', '')
            })
        
        logger.info(f"Found {len(poi_data)} POIs in database for {city}")
        logger.debug(f"Sample POIs: {json.dumps(poi_data[:3])}")
        
        # Fall back to simple string matching if no API key or very few POIs
        if not api_key or len(poi_data) < 5:
            logger.info("Using simple string matching for mandatory POIs")
            return _simple_poi_matching(mandatory_pois_text, poi_data)
        
        # Prepare the prompt for the LLM
        prompt = f"""Given the following list of points of interest (POIs) in {city}:
{json.dumps(poi_data)}

And this list of must-visit places specified by the user:
"{mandatory_pois_text}"

Identify which POI IDs from the database match the user's requests. Consider translations, misspellings, and alternative names.
Return ONLY a JSON array of numbers representing the POI IDs that match, like [1, 5, 10].
If no matches are found, return an empty array [].
Do not include any explanation or additional text in your response, only the JSON array.
"""

        logger.info(f"Sending request to LLM to identify POIs...")
        
        # Call OpenAI API to get matching
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",  # You may need to adjust this to the model you're using
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        # Parse the response
        content = response.choices[0].message.content.strip()
        logger.debug(f"LLM Raw Response: {content}")
        
        try:
            # Try to parse as JSON directly
            result = json.loads(content)
            if isinstance(result, list):
                mandatory_poi_ids = [int(id) for id in result]
            elif isinstance(result, dict) and "ids" in result:
                mandatory_poi_ids = [int(id) for id in result["ids"]]
            else:
                mandatory_poi_ids = []
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract the array portion
            import re
            array_match = re.search(r'\[.*?\]', content)
            if array_match:
                try:
                    array_str = array_match.group(0)
                    mandatory_poi_ids = [int(id) for id in json.loads(array_str)]
                except:
                    mandatory_poi_ids = []
            else:
                mandatory_poi_ids = []
        
        # Print the matched POIs with their names for verification
        logger.info(f"Matched mandatory POIs ({len(mandatory_poi_ids)}):")
        for poi_id in mandatory_poi_ids:
            for poi in poi_data:
                if poi["id"] == poi_id:
                    logger.info(f"  - ID {poi_id}: {poi['name']} ({poi['type']})")
                    break
                    
        logger.info(f"Final mandatory POI IDs: {mandatory_poi_ids}")
        logger.info("--- END MANDATORY POIs IDENTIFICATION ---")
        
        return mandatory_poi_ids
            
    except Exception as e:
        logger.error(f"Error identifying mandatory POIs: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def plan_itinerary(city, start_time="08:00", end_time="22:00", max_pois=6, restaurant_count=1, api_key=None, mandatory_poi_ids=None, use_api_for_distance=True):
    """Plan a tourist itinerary and return the results"""
    logger.info(f"Planning itinerary for {city}")
    logger.info(f"Time window: {start_time} - {end_time}")
    
    try:
        # Default to an empty list if mandatory_poi_ids is None
        if mandatory_poi_ids is None:
            mandatory_poi_ids = []
        
        # Try to load the graph with cached travel times
        from data.city_graph import load_graph
        graph = load_graph(city.lower())
        
        # Verify graph loaded correctly with travel times
        if graph is not None:
            edge_count = 0
            edges_with_travel_times = 0
            
            for u, v in graph.edges():
                edge_count += 1
                if 'travel_time' in graph[u][v]:
                    edges_with_travel_times += 1
            
            # Define has_travel_times variable based on coverage percentage
            has_travel_times = edge_count > 0 and edges_with_travel_times / edge_count >= 0.5
            logger.info(f"Loaded graph with {edges_with_travel_times}/{edge_count} edges having travel times")
            logger.info(f"Has sufficient travel times: {has_travel_times}")
        else:
            # If no graph was loaded, we definitely don't have travel times
            has_travel_times = False
        
        logger.debug("Initializing TouristItinerarySolver")
        solver = TouristItinerarySolver(
            city=city,
            graph=graph,  # Pass the loaded graph
            start_time=start_time, 
            end_time=end_time,
            mandatory_visits=mandatory_poi_ids,
            api_key=api_key,
            max_neighbors=3,
            mandatory_restaurant=True if restaurant_count > 0 else False,
            restaurant_count=restaurant_count,
            max_pois=max_pois,
            use_api_for_distance=use_api_for_distance and not has_travel_times  # Skip API if we have cached times
        )
        
        # Solve the problem
        itinerary = solver.solve(max_pois=max_pois)
        
        # Format the itinerary
        formatted_itinerary = solver.format_itinerary(itinerary)
        
        # Return results
        return {
            "success": True,
            "itinerary": formatted_itinerary,
            "raw_itinerary": itinerary,
            "stats": {
                "api_requests": solver.distance_calculator.request_count
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/plan', methods=['POST'])
def api_plan():
    """API endpoint for planning an itinerary"""
    logger.info("Received itinerary planning request")
    
    try:
        data = request.json
        logger.debug(f"Request data: {json.dumps(data)}")
        
        city = data.get('city')
        start_time = data.get('start_time', "08:00")
        end_time = data.get('end_time', "22:00")
        max_pois = int(data.get('max_pois', 6))
        restaurant_count = int(data.get('restaurant_count', 1))
        mandatory_pois_text = data.get('mandatory_pois', '').strip()
        use_api_for_distance = data.get('use_api_for_distance', True)
        
        logger.info(f"Planning itinerary for {city} from {start_time} to {end_time}")
        logger.info(f"Max POIs: {max_pois}, Restaurant count: {restaurant_count}")
        if mandatory_pois_text:
            logger.info(f"Mandatory POIs requested: {mandatory_pois_text}")
        
        # Get API key from environment
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("No OpenAI API key found in environment")
        
        # Check data/city_graph.py for graph existence
        from data.city_graph import check_city_graph_exists, load_graph
        graph_exists = check_city_graph_exists(city.lower())
        logger.info(f"Graph exists for {city}: {graph_exists}")

        import src.city_generator as city_generator
        if not graph_exists:
            city_generator.generate_city_data(city, api_key)
        
        # After graph is created, identify mandatory POIs if any were specified
        mandatory_poi_ids = []
        if mandatory_pois_text:
            logger.info(f"Identifying mandatory POIs: {mandatory_pois_text}")
            # Now that the graph should exist, identify mandatory POIs
            mandatory_poi_ids = identify_mandatory_pois(city, mandatory_pois_text, api_key)
            logger.info(f"Identified mandatory POI IDs: {mandatory_poi_ids}")
            print("ici")
            # If we found mandatory POIs, re-run the planner to include them
            if mandatory_poi_ids:
                logger.info(f"Re-planning itinerary with mandatory POIs: {mandatory_poi_ids}")
                result = plan_itinerary(
                    city, 
                    start_time, 
                    end_time, 
                    max_pois, 
                    restaurant_count, 
                    api_key, 
                    mandatory_poi_ids,
                    use_api_for_distance  # Add this parameter
                )
        else:
            # If no mandatory POIs, just plan the itinerary
            result = plan_itinerary(
                city, 
                start_time, 
                end_time, 
                max_pois, 
                restaurant_count, 
                api_key,
                use_api_for_distance  # Add this parameter
            )
        
        logger.info("Itinerary planning completed successfully")
        logger.debug(f"Result: {json.dumps(result)}")
        return jsonify(result)
    
    except Exception as e:
        error_msg = f"Error planning itinerary 2: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({"error": error_msg}), 500

@app.route('/api/fun-facts', methods=['POST'])
def api_fun_facts():
    """API endpoint for getting fun facts about a city"""
    data = request.json
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return jsonify({
            "success": False,
            "error": "No OpenAI API key found. Please set the OPENAI_API_KEY environment variable."
        })
    
    # Get city name from request
    city = data.get('city')
    if not city:
        return jsonify({
            "success": False,
            "error": "No city specified."
        })
    
    # Generate fun facts
    from src.city_generator import generate_city_fun_facts
    fun_facts = generate_city_fun_facts(city, api_key, count=8)
    logger.info(f"Generated fun facts for {city}: {fun_facts}")
    return jsonify({
        "success": True,
        "fun_facts": fun_facts
    })

# @app.route('/api/fun-facts/<poi_id>')
# def get_fun_facts(poi_id):
#     """API endpoint to get fun facts for a POI"""
#     try:
#         # Your existing code to get fun facts
#         facts = generate_city_fun_facts(poi_id)
#         return jsonify({"facts": facts})
#     except Exception as e:
#         logger.error(f"Error generating fun facts for POI {poi_id}: {str(e)}")
#         return jsonify({"error": "Failed to generate fun facts"}), 500

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Check if running as web server
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        # Start web server
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        print(f"Starting web server on port {port}...")
        app.run(debug=True, host='0.0.0.0', port=port)
        return
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python plan_itinerary.py <city_name> [start_time] [end_time] [max_pois] [restaurant_count]")
        print("       python plan_itinerary.py --server [port]")
        print("Example: python plan_itinerary.py 'Paris' '09:00' '18:00' 8 2")
        sys.exit(1)
    
    # Get city name
    city = sys.argv[1]
    
    # Get optional parameters
    start_time = sys.argv[2] if len(sys.argv) > 2 else "08:00"
    end_time = sys.argv[3] if len(sys.argv) > 3 else "22:00"
    max_pois = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    restaurant_count = int(sys.argv[5]) if len(sys.argv) > 5 else 2
    
    print(f"Planning itinerary for {city}...")
    print(f"Time window: {start_time} to {end_time}")
    print(f"Maximum POIs: {max_pois}")
    print(f"Restaurant count: {restaurant_count}")
    
    # Plan the itinerary
    result = plan_itinerary(city, start_time, end_time, max_pois, restaurant_count, api_key)
    
    if result["success"]:
        print(result["itinerary"])
        print(f"\nAPI Request Statistics:")
        print(f"Total API requests made: {result['stats']['api_requests']}")
    else:
        print(f"Error planning itinerary 3: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()