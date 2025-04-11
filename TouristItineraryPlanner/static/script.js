let funFacts = [];
let currentFactIndex = 0;
let factInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('itinerary-form');
    const resultsSection = document.getElementById('results-section');
    const itineraryResult = document.getElementById('itinerary-result');
    const errorMessage = document.getElementById('error-message');
    const loadingIndicator = document.getElementById('loading');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate the city name
        const cityInput = document.getElementById('city').value.trim();
        if (!cityInput) {
            errorMessage.textContent = "Please enter a city name";
            errorMessage.style.display = 'block';
            resultsSection.style.display = 'block';
            itineraryResult.style.display = 'none';
            loadingIndicator.style.display = 'none';
            return;
        }
        
        // Format the city name properly - capitalize first letter of each word
        const formattedCity = cityInput.split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
        
        // Show loading state
        resultsSection.style.display = 'block';
        itineraryResult.style.display = 'none';
        errorMessage.style.display = 'none';
        loadingIndicator.style.display = 'block';
        
        // Reset fun facts
        clearInterval(factInterval);
        funFacts = [];
        currentFactIndex = 0;
        const funFactElement = document.getElementById('fun-fact');
        if (funFactElement) {
            funFactElement.textContent = "Loading interesting facts about " + formattedCity + "...";
        }
        
        // STEP 1: First fetch fun facts
        try {
            await fetchFunFacts(formattedCity);
            
            // STEP 2: Then plan the itinerary
            planItinerary(formattedCity);
        } catch (error) {
            handleError("Error loading fun facts: " + error.message);
        }
    });
    
    function planItinerary(city) {
        // Get form data
        const formData = {
            city: city,
            start_time: document.getElementById('start-time').value,
            end_time: document.getElementById('end-time').value,
            max_pois: document.getElementById('max-pois').value,
            restaurant_count: document.getElementById('restaurant-count').value,
            mandatory_pois: document.getElementById('mandatory-pois').value
        };
        
        // Find where the form data is collected and the API request is made
        // Add the new parameter:
        const distanceMethod = document.getElementById('distance-calculation').value;
        const useApiForDistance = distanceMethod === 'api';

        // Add to the data object being sent
        const requestData = {
            city: city,
            start_time: formData.start_time,
            end_time: formData.end_time,
            max_pois: formData.max_pois,
            restaurant_count: formData.restaurant_count,
            mandatory_pois: formData.mandatory_pois,
            use_api_for_distance: useApiForDistance
        };
        
        // Set itinerary result to not display while loading
        const itineraryResult = document.getElementById('itinerary-result');
        if (itineraryResult) {
            itineraryResult.style.display = 'none';
        }
        
        // Send API request
        fetch('/api/plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            
            // Clear fun facts interval
            clearInterval(factInterval);
            
            if (data.success) {
                // Show results
                displayItinerary(data.itinerary);
            } else {
                // Show error
                handleError(data.error);
            }
        })
        .catch(error => {
            handleError("Network error: " + error.message);
        });
    }
    
    function handleError(message) {
        // Hide loading indicator
        loadingIndicator.style.display = 'none';
        
        // Clear fun facts interval
        clearInterval(factInterval);
        
        // Show error
        errorMessage.textContent = `Error: ${message}`;
        errorMessage.style.display = 'block';
    }

    console.log('DOM fully loaded, initializing event listeners');
    initializePOIDetailsModal();
});

// Fetch fun facts and return a promise
function fetchFunFacts(city) {
    return new Promise((resolve, reject) => {
        fetch('/api/fun-facts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ city: city }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.fun_facts && data.fun_facts.length > 0) {
                funFacts = data.fun_facts;
                
                // Display the first fact immediately
                displayNextFact();
                
                // Set up interval to change facts every 20 seconds
                clearInterval(factInterval);
                factInterval = setInterval(displayNextFact, 20000);
                
                resolve();
            } else {
                // If no fun facts were returned, still proceed but with a default message
                funFacts = ["Did you know? Facts about this city are being generated just for you!"];
                displayNextFact();
                resolve();
            }
        })
        .catch(error => {
            console.error('Error fetching fun facts:', error);
            // Don't reject, just proceed with planning
            resolve();
        });
    });
}

function displayNextFact() {
    if (funFacts.length > 0) {
        const funFactElement = document.getElementById('fun-fact');
        
        // Check if element exists before manipulating it
        if (funFactElement) {
            // Add fade-out effect
            funFactElement.classList.remove('fade-in');
            funFactElement.classList.add('fade-out');
            
            // Wait for fade-out to complete
            setTimeout(() => {
                // Update text
                funFactElement.textContent = funFacts[currentFactIndex];
                
                // Switch to fade-in
                funFactElement.classList.remove('fade-out');
                funFactElement.classList.add('fade-in');
                
                // Update index for next time
                currentFactIndex = (currentFactIndex + 1) % funFacts.length;
            }, 500);
        }
    }
}

function displayItinerary(result) {
    const planningIndicator = document.getElementById('planning-indicator');
    if (planningIndicator) {
        planningIndicator.style.display = 'none';
    }
    
    const itineraryResult = document.getElementById('itinerary-result');
    if (itineraryResult) {
        itineraryResult.style.display = 'block';
        itineraryResult.textContent = result;
    }
}

function loadFunFacts(poiId) {
    console.log('Loading fun facts for POI ID:', poiId);
    
    // Safely get elements with null checks
    const funFactsLoading = document.getElementById('fun-facts-loading');
    const funFactsContent = document.getElementById('fun-facts-content');
    const funFactsError = document.getElementById('fun-facts-error');
    
    // Show loading state if element exists
    if (funFactsLoading) {
        funFactsLoading.style.display = 'block';
        console.log('Showing loading indicator');
    }
    
    // Hide other elements if they exist
    if (funFactsContent) funFactsContent.style.display = 'none';
    if (funFactsError) funFactsError.style.display = 'none';
    
    // Make the API call
    fetch(`/api/fun-facts/${poiId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Fun facts API response:', data);
            
            // Hide loading indicator
            if (funFactsLoading) funFactsLoading.style.display = 'none';
            
            if (data.facts) {
                // Show content if element exists
                if (funFactsContent) {
                    funFactsContent.style.display = 'block';
                    funFactsContent.innerHTML = data.facts;
                    console.log('Fun facts displayed successfully');
                } else {
                    console.error('Fun facts content element not found');
                }
            } else {
                throw new Error(data.error || 'No facts returned');
            }
        })
        .catch(error => {
            console.error('Error loading fun facts alex:', error);
            
            // Hide loading indicator
            if (funFactsLoading) funFactsLoading.style.display = 'none';
            
            // Show error if element exists
            if (funFactsError) {
                funFactsError.style.display = 'block';
                funFactsError.textContent = 'Failed to load fun facts. Please try again.';
            }
        });
}

function showFunFacts(poiId, facts) {
    const funFactsLoading = document.getElementById('fun-facts-loading');
    const funFactsContent = document.getElementById('fun-facts-content');
    
    if (funFactsLoading) funFactsLoading.style.display = 'none';
    if (funFactsContent) {
        funFactsContent.style.display = 'block';
        funFactsContent.innerHTML = facts;
    }
}

function showFunFactsError(error) {
    const funFactsLoading = document.getElementById('fun-facts-loading');
    const funFactsError = document.getElementById('fun-facts-error');
    
    if (funFactsLoading) funFactsLoading.style.display = 'none';
    if (funFactsError) {
        funFactsError.style.display = 'block';
        funFactsError.textContent = error;
    }
}

// Initialize the modal and its event handlers
function initializePOIDetailsModal() {
    // Get modal elements
    const modal = document.getElementById('poi-details-modal');
    const closeBtn = modal?.querySelector('.close');
    
    // Set up event handlers if elements exist
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            if (modal) modal.style.display = 'none';
        });
    }
    
    // Close when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    console.log('POI details modal initialized');
}

// Show POI details and load fun facts
function showPOIDetails(poi) {
    console.log('Showing POI details for:', poi);
    
    // Safely get elements
    const modal = document.getElementById('poi-details-modal');
    const poiName = document.getElementById('poi-name');
    
    // Only proceed if modal exists
    if (!modal) {
        console.error('POI details modal not found in the DOM');
        return;
    }
    
    // Update modal content
    if (poiName) poiName.textContent = poi.name;
    
    // Show the modal
    modal.style.display = 'block';
    
    // Load fun facts
    if (poi.id) {
        loadFunFacts(poi.id);
    }
}