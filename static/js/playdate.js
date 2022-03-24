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
                    ${responseJson.description}<br>
                    For ${responseJson.age_group}.
                    Hosted by ${responseJson.host}<br>
                    At ${responseJson.location}<br>
                    Address: ${responseJson.address}, ${responseJson.city}, ${responseJson.state} ${responseJson.zipcode}<br>
                    On ${responseJson.date} from ${responseJson.start_time} to ${responseJson.end_time}<br>
                    Activities: ${responseJson.activity_list}<br>
                    Who's coming: Family of ${responseJson.attendants}
                    ` // how to add comma to the activity and attendants list (above)
                    // if upcoming events, show Register form
                    if (button.value === "upcoming_event") {
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `<form action="/register" method="POST" onsubmit="return confirm('Do you want to register for this playdate?');">
                            <input type="hidden" name="event_id" value="${button.id}">
                            <input type=submit value="Register">
                        </form>
                        `)
                    }
                    // if host event, show Cancel form
                    if (button.value === "host_event") {
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `
                        <div id="cancel_host">
                            <form action="/cancel_event" method="POST" onsubmit="return confirm('Do you really want to cancel this playdate?');">
                                <input type="hidden" name="event_id" value="${button.id}">
                                <input type=submit value="Cancel playdate">
                            </form>
                        </div>
                        `)
                    }
                    // if attending event, show Cancel registration form
                    if (button.value === "attending_event") {
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `
                        <div id="cancel_registration">
                            <form action="/cancel_registration" method="POST" onsubmit="return confirm('Do you really want to cancel this registration?');">
                                <input type="hidden" name="event_id" value="${button.id}">
                                <input type=submit value="Cancel registration">
                            </form>
                        </div>
                        `)
                    }
                    
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
                        map: basicMap,
                        address: eventLocation.address
                    });
                    // Zoom in on the geolocated location
                        basicMap.setCenter(locationCoordinates);
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
                } else { // if coordinates are not in database
                    // Geocode the address to coordinates
                    console.log("Geocoding");
                    const geocoder = new google.maps.Geocoder();
                    geocoder.geocode({ address: locationAddress }, (results, status) => {
                        if (status === 'OK') {
                            // Get the coordinates of the user's location
                            locationCoordinates = {
                                lat: results[0].geometry.location.lat(),
                                lng: results[0].geometry.location.lng()
                            }
                            // sending AJAX to update the coordinates in the database 
                            const coordinates = {
                                lat: results[0].geometry.location.lat(),
                                lng: results[0].geometry.location.lng(),
                                location_id: responseJson.location_id,
                            };
                            fetch("/update_coordinates", {
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
                            map: basicMap,
                            address: eventLocation.address
                        });
                        // Zoom in on the geolocated location
                            basicMap.setCenter(locationCoordinates);
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
                        button.addEventListener('click', showInfo);
                    });
                }    
                
            })
    }
}

// If host chooses to add activities in their hosting form
// Select the element with id "add_activities" and set to hidden
const suggestedActivities = document.getElementById('suggested_activities');
suggestedActivities.style.visibility = 'hidden';
// Select the element with id "other" and add event handler
const addActivities = document.getElementById('add_activities');
addActivities.addEventListener('change', () => {
    if(addActivities.checked) {
        suggestedActivities.style.visibility = 'visible';
        suggestedActivities.value = '';
    } else {
        suggestedActivities.style.visibility = 'hidden';
    }
});


// Adding other activities in text box in hosting form (hosting.html)
// Select the element with id "otherValue" and set to hidden
const otherText = document.getElementById('otherActivity');
otherText.style.visibility = 'hidden';
// Select the element with id "other" and add event handler
const otherCheckbox = document.getElementById('other');
otherCheckbox.addEventListener('change', () => {
    if(otherCheckbox.checked) {
        otherText.style.visibility = 'visible';
        otherText.value = '';
    } else {
        otherText.style.visibility = 'hidden';
    }
});


// Adding list of equipment in hosting form (hosting.html) if host chooses to
// Select the element with id "equipment" and set to hidden
const equipment = document.getElementById('equipment');
equipment.style.visibility = 'hidden';
// Select the element with id "other" and add event handler
const addEquipment = document.getElementById('add_equipment');
addEquipment.addEventListener('change', () => {
    if(addEquipment.checked) {
        equipment.style.visibility = 'visible';
        equipment.value = '';
    } else {
        equipment.style.visibility = 'hidden';
    }
});