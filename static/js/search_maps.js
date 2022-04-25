'use strict';
// This file is used for displaying the map and location markers of all events resulted from a search


// Display a map and mark locations on the map
function initMap() {
    // Put a basic map on the search result page
    const basicMap = new google.maps.Map(document.querySelector('#map'), {
        center: {
            lat: 37.6688,
            lng: -122.0810,
        },
        zoom: 11,
    });
    
    // Info window for displaying info one at a time only
    const markerInfo = new google.maps.InfoWindow();

    // Display the locations on the map
    // Select all buttons and iterate through the list to get address and name of the event
    const buttons = document.querySelectorAll(".event-details");
    for (const button of buttons) { 
        let locationAddress, locationName, eventLocation;
        const url = `/events?event_id=${button.id}`; 
        
        // fetch with sending data by get request
        fetch(url)
            .then(response => response.json())
            .then(responseJson => {
                locationAddress = responseJson.address + ", " + responseJson.city + ", " + responseJson.state + " " 
                                       + responseJson.zipcode;
                locationName = responseJson.location;
                
                // Check if coordinates of the location are in the database
                let locationCoordinates;
                if (responseJson.lat && responseJson.lng) {
                    locationCoordinates = {"lat": responseJson.lat, "lng": responseJson.lng};
                    // Create event location 
                    eventLocation = {
                        name: locationName,
                        coords: locationCoordinates,
                        address: locationAddress
                    };
                    // Create a marker
                    const marker = new google.maps.Marker({
                        position: eventLocation.coords,
                        title: eventLocation.name,
                        animation: google.maps.Animation.DROP,
                        map: basicMap,
                        address: eventLocation.address,
                        icon: "https://img.icons8.com/external-nawicon-flat-nawicon/40/000000/external-park-location-nawicon-flat-nawicon.png",
                    });
                    // Zoom in on the geolocated location
                        // basicMap.setCenter(locationCoordinates);
                        // basicMap.setZoom(11);

                    // Create marker info
                    const locationInfo = `
                        <h1>${marker.title}</h1>
                        <p>
                            Located at: ${marker.address}
                        </p>
                        ${responseJson.title}</b><br>
                        On ${responseJson.date} from ${responseJson.start_time} to ${responseJson.end_time}<br>
                        `;
                    // callback function show location detail on map
                    const showInfo = () => {
                        if (button.innerText === "Show details") {
                            markerInfo.close();
                            markerInfo.setContent(locationInfo);
                            markerInfo.open(basicMap, marker);
                        } else {
                            markerInfo.close();
                        }
                    };
                    // add event click to marker
                    marker.addListener('click', showInfo);
                    // add event click to detail button
                    button.addEventListener("click", showInfo);
                } else { // if coordinates are not in database
                    // Geocode the address to coordinates
                    const geocoder = new google.maps.Geocoder();
                    geocoder.geocode({ address: locationAddress }, (results, status) => {
                        if (status === 'OK') {
                            // Get the coordinates of the event location
                            locationCoordinates = {
                                lat: results[0].geometry.location.lat(),
                                lng: results[0].geometry.location.lng()
                            }
                            // sending AJAX to update the coordinates in the database 
                            const coordinates = {
                                lat: results[0].geometry.location.lat(),
                                lng: results[0].geometry.location.lng(),
                                name: responseJson.location,
                                address: responseJson.address
                            };
                            fetch("/update_location_details", {
                                method: 'POST',
                                body: JSON.stringify(coordinates),
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                            })
                                .then(reply => reply.json())
                                .then(replyJson => {const status = replyJson.status;})
                        } else {
                            alert(`Geocode was unsuccessful for the following reason: ${status}`);
                        }
                        // Create event location with name and coordinates for markers
                        eventLocation = {
                            name: locationName,
                            coords: locationCoordinates,
                            address: locationAddress
                        };
                        // Create a marker
                        const marker = new google.maps.Marker({
                            position: eventLocation.coords,
                            title: eventLocation.name,
                            animation: google.maps.Animation.DROP,
                            map: basicMap,
                            address: eventLocation.address,
                            icon: "https://img.icons8.com/external-nawicon-flat-nawicon/40/000000/external-park-location-nawicon-flat-nawicon.png",
                        });
                        
                        // Zoom in on the geolocated location
                            // basicMap.setCenter(locationCoordinates);
                            // basicMap.setZoom(11);
                        // Create marker info
                        const locationInfo = `
                            <h1>${marker.title}</h1>
                            <p>
                                Located at: ${marker.address}
                            </p>
                            ${responseJson.title}</b><br>
                            On ${responseJson.date} from ${responseJson.start_time} to ${responseJson.end_time}<br>
                            `;
                        // callback function show location detail on map
                        const showInfo = () => {
                            if (button.innerText === "Show details") {
                                markerInfo.close();
                                markerInfo.setContent(locationInfo);
                                markerInfo.open(basicMap, marker);
                            } else {
                                markerInfo.close();
                            }
                        };
                        // add event click to marker
                        marker.addListener('click', showInfo);
                        // add event click to detail button
                        button.addEventListener('click', showInfo);
                    });
                }    
                
            })
    }

    // Get user's current location by using geolocation.getCurrentPosition()
    // Call back function
    const success = (position) => {
        const userCoordinates = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
        };
        // Create a marker for user's current location
        const userMarker = new google.maps.Marker({
            position: userCoordinates,
            title: "Your current location",
            map: basicMap,
            icon: "https://img.icons8.com/ultraviolet/40/000000/marker.png"
        });
        // Create user's marker info
        const userMarkerInfo = new google.maps.InfoWindow({
            content : `<h3>${userMarker.title}</h3>`,
        });
        // add event click to user location marker to open info window
        userMarker.addListener('click', () => {
            userMarkerInfo.open(basicMap, userMarker);
        });
    }
      
    const error = (err) => {
        console.warn(`ERROR(${err.code}): ${err.message}`);
    }
      
    if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(success, error); 
    }
}