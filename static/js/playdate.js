'use strict';

// 1. AJAX requests to see event details
// Select all buttons of the class "event-details"
const buttons = document.querySelectorAll(".event-details");

// Add event handler to each button
for (const button of buttons) {
    button.addEventListener("click", () => {
        // make the url with key and value as event_id via button id
        const url = `/events?event_id=${button.id}`;
        // fetch with sending data by get request
        fetch(url)
            .then(response => response.json())
            .then(responseJson => { // display details
                if (button.innerText === "Show details") {
                    button.innerText = "Hide details";
                    document.getElementById(`display-detail${button.id}`).innerHTML = 
                    `
                    <b>Playdate details<br>
                    Title: ${responseJson.title}</b><br>
                    ${responseJson.description}<br>
                    For ${responseJson.age_group}<br>
                    Hosted by ${responseJson.host}<br>
                    At ${responseJson.location}<br>
                    Address: ${responseJson.address}, ${responseJson.city}, ${responseJson.state} ${responseJson.zipcode}<br>
                    On ${responseJson.date} from ${responseJson.start_time} to ${responseJson.end_time}<br>
                    <form action="/register" method="POST">
                        <input type="hidden" name="event_id" value="${button.id}">
                        <input type=submit value="Register">
                    </form>
                    `
                } else { // Hide event details
                    button.innerText = "Show details";
                    document.getElementById(`display-detail${button.id}`).innerHTML = "";
                }
            })
    });
}


// Display a map and mark locations on the map
function initMap() {
    // Put a basic map on the search result page
    const basicMap = new google.maps.Map(document.querySelector('#map'), {
        center: {
            lat: 37.601773,
            lng: -122.20287,
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
                
                // Geocode the address to coordinates
                const geocoder = new google.maps.Geocoder();
                let userLocation;
                geocoder.geocode({ address: locationAddress }, (results, status) => {
                    if (status === 'OK') {
                        // Get the coordinates of the user's location
                        userLocation = results[0].geometry.location;
                    } else {
                        alert(`Geocode was unsuccessful for the following reason: ${status}`);
                    }
                    // Create event location with name and coordinates for markers
                    eventLocation = {
                        name: locationName,
                        coords: userLocation,
                        address: locationAddress
                    };

                    // Create a marker
                    const marker = new google.maps.Marker({
                        position: eventLocation.coords,
                        title: eventLocation.name,
                        map: basicMap,
                        address: eventLocation.address
                    });

                    // Zoom in on the geolocated location
                        basicMap.setCenter(userLocation);
                        basicMap.setZoom(11);

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
                    
                });
            })
    }
}



