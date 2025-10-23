// Replace with your actual OpenUV API key
const OPENUV_API_KEY = 'openuv-pioosrmh2g7696-io';

// Initialize variables
let map;
let currentMarker;
let userLocation = null;

// Initialize the application
async function initApp() {
    await initializeMap();
    await getUserLocation();
}

// Initialize map
function initializeMap() {
    map = L.map('map').setView([0, 0], 2); // Temporary center
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

// Get user's current location
function getUserLocation() {
    updateLocationStatus('📍 Detecting your location...');
    
    if (!navigator.geolocation) {
        updateLocationStatus('❌ Geolocation is not supported by your browser');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            userLocation = { lat, lng };
            
            // Update map view
            map.setView([lat, lng], 13);
            
            // Get address and UV data
            await Promise.all([
                getAddressFromCoords(lat, lng),
                getUVData(lat, lng)
            ]);
            
            // Add marker to map
            if (currentMarker) {
                map.removeLayer(currentMarker);
            }
            currentMarker = L.marker([lat, lng])
                .addTo(map)
                .bindPopup('Your Location')
                .openPopup();
                
        },
        (error) => {
            console.error('Error getting location:', error);
            handleLocationError(error);
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
        }
    );
}

// Handle location errors
function handleLocationError(error) {
    let message = '❌ Unable to get your location';
    
    switch(error.code) {
        case error.PERMISSION_DENIED:
            message = '❌ Location access denied. Please enable location permissions.';
            break;
        case error.POSITION_UNAVAILABLE:
            message = '❌ Location information unavailable.';
            break;
        case error.TIMEOUT:
            message = '❌ Location request timed out.';
            break;
    }
    
    updateLocationStatus(message);
    // Fallback to a default location (e.g., New York)
    fallbackToDefaultLocation();
}

// Fallback to default location
function fallbackToDefaultLocation() {
    userLocation = { lat: 40.7128, lng: -74.0060 }; // New York
    map.setView([userLocation.lat, userLocation.lng], 10);
    getUVData(userLocation.lat, userLocation.lng);
    updateLocationStatus('📍 Using default location (New York)');
    updateAddressDisplay('New York, USA');
}

// Get address from coordinates
async function getAddressFromCoords(lat, lng) {
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
        const data = await response.json();
        
        if (data.display_name) {
            const address = data.display_name.split(',').slice(0, 3).join(',');
            updateAddressDisplay(address);
            updateLocationStatus(`📍 Location: ${address}`);
        }
    } catch (error) {
        console.error('Error getting address:', error);
        updateAddressDisplay('Location detected');
    }
}

// ClinicalBERT status check
async function checkClinicalBERTStatus() {
    try {
        const response = await fetch('http://localhost:5003/health', {
            method: 'GET',
            mode: 'no-cors' // Simple check
        });
        return true;
    } catch (error) {
        return false;
    }
}

// Update status indicator
function updateClinicalBERTStatus() {
    const statusElement = document.getElementById('clinicalbert-status');
    if (statusElement) {
        checkClinicalBERTStatus().then(isRunning => {
            if (isRunning) {
                statusElement.innerHTML = `
                    <div class="status-indicator status-online">
                        <span class="status-dot"></span>
                        Local ClinicalBERT: Online
                    </div>
                `;
            } else {
                statusElement.innerHTML = `
                    <div class="status-indicator status-offline">
                        <span class="status-dot"></span>
                        Local ClinicalBERT: Offline - Run the server first
                    </div>
                `;
            }
        });
    }
}

// Check status when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check status after a delay to let server start
    setTimeout(updateClinicalBERTStatus, 2000);
    
    // Optional: Auto-refresh status every 10 seconds
    setInterval(updateClinicalBERTStatus, 10000);
});

// Update address display
function updateAddressDisplay(address) {
    document.getElementById('current-address').textContent = address;
}

// Update location status
function updateLocationStatus(status) {
    document.getElementById('location-status').textContent = status;
}

// Get UV data from OpenUV API
async function getUVData(lat, lng) {
    const alertBanner = document.getElementById('alert-banner');
    
    try {
        // Show loading state
        alertBanner.innerHTML = `
            <div class="alert-content">
                <div class="spinner"></div>
                <span>Getting UV data for your location...</span>
            </div>
        `;
        
        const response = await fetch(`https://api.openuv.io/api/v1/uv?lat=${lat}&lng=${lng}`, {
            headers: {
                'x-access-token': OPENUV_API_KEY
            }
        });
        
        if (!response.ok) {
            throw new Error('UV API request failed');
        }
        
        const data = await response.json();
        const uvData = data.result;
        
        // Update display
        updateUVAlert(uvData.uv);
        updateLastUpdated();
        
        // Update marker popup
        if (currentMarker) {
            currentMarker.setPopupContent(`
                <strong>Your Location</strong><br>
                UV Index: ${uvData.uv}<br>
                ${new Date(uvData.uv_time).toLocaleTimeString()}
            `);
        }
        
        return uvData;
        
    } catch (error) {
        console.error('Error fetching UV data:', error);
        // Fallback to mock data for demo
        const mockUV = Math.floor(Math.random() * 12) + 1; // Random UV 1-12
        updateUVAlert(mockUV);
        updateLastUpdated();
        alertBanner.innerHTML = `
            <div class="alert-content">
                <span>⚠️ Using demo data - API limit may be reached</span>
            </div>
        `;
    }
}

// Update UV alert display
function updateUVAlert(uvIndex) {
    const alertBanner = document.getElementById('alert-banner');
    
    let level, message, className;
    
    if (uvIndex <= 2) {
        level = 'Low'; className = 'low';
        message = 'Perfect day to be outside! Minimal protection required.';
    } else if (uvIndex <= 5) {
        level = 'Moderate'; className = 'moderate';
        message = 'Stay in shade near midday. Wear sunscreen and a hat.';
    } else if (uvIndex <= 7) {
        level = 'High'; className = 'high';
        message = 'Protection needed! Use sunscreen SPF 30+, wear a hat and sunglasses.';
    } else if (uvIndex <= 10) {
        level = 'Very High'; className = 'very-high';
        message = 'Extra protection required! Use sunscreen SPF 50+, seek shade during midday.';
    } else {
        level = 'Extreme'; className = 'extreme';
        message = 'DANGER! Avoid sun exposure! Unprotected skin can burn in minutes.';
    }
    
    alertBanner.innerHTML = `
        <div class="alert-content">
            <h3>${level} Risk Alert - UV Index: ${uvIndex.toFixed(1)}</h3>
            <p>${message}</p>
        </div>
    `;
    alertBanner.className = `alert ${className}`;
}

// Update last updated time
function updateLastUpdated() {
    const now = new Date();
    document.getElementById('last-updated').textContent = now.toLocaleTimeString();
}

// Refresh location button
document.getElementById('refresh-location').addEventListener('click', function() {
    getUserLocation();
});

// Initialize the app when page loads
document.addEventListener('DOMContentLoaded', initApp);