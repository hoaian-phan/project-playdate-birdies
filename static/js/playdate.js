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
                    Activities: ${responseJson.activity_list.join(", ")}<br>
                    Who's coming: Family of ${responseJson.attendants.join(", ")}<br>
                    Equipment: ${responseJson.equipments.join(", ")}
                    `
                    // if upcoming events, show Register form
                    if (button.value === "upcoming_event") {
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `<form action="/attend" 
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


// If host chooses to add activities in their hosting form
// Select the element with id "add_activities" and set display to none
const suggestedActivities = document.getElementById('suggested_activities');
suggestedActivities.style.display = 'none';
// Select the element with id "other" and add event handler
const addActivities = document.getElementById('add_activities');
addActivities.addEventListener('change', () => {
    if(addActivities.checked) {
        suggestedActivities.style.display = 'block';
        suggestedActivities.value = '';
    } else {
        suggestedActivities.style.display = 'none';
    }
});


// Adding other activities in text box in hosting form (hosting.html)
// Select the element with id "otherValue" and set display to none
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


// Adding list of items and quantity in hosting form (hosting.html) if host chooses to
// Select the element with id "add" and add event handler to insert element
const add_btn = document.getElementById('add');
let i = 0; // to set unique id for each item
add_btn.addEventListener("click", () => {
    i += 1; 
    document.getElementById('item_quantity').insertAdjacentHTML("beforeend",
        `
        <li id="item_quantity_${i}">
            <label for="item_${i}">Item</label>
            <input type="text" id="item_${i}" name="item">
            <label for="quantity_${i}">Quantity</label>
            <input type="text" id="quantity_${i}" name="quantity">
            <button type="button" id="delete_${i}" name="delete">Delete</button>
            <br>
        </li>
        `)
    // Select the element with id "delete" and add event handler to delete element
    const delete_btn = document.getElementById(`delete_${i}`);
    delete_btn.addEventListener("click", () => {
        delete_btn.parentElement.remove();
    });
});
// Count how many equipments ( how many child element of <ul>)
const numEquipment = document.querySelector("#item_quantity").childElementCount;
document.querySelector("#item_quantity").value = numEquipment;




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
                        address: eventLocation.address,
                        icon: "https://img.icons8.com/external-nawicon-flat-nawicon/40/000000/external-park-location-nawicon-flat-nawicon.png",
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
                            address: eventLocation.address,
                            icon: "https://img.icons8.com/external-nawicon-flat-nawicon/40/000000/external-park-location-nawicon-flat-nawicon.png",
                        });
                        console.log(marker.icon);
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

    // Get user's current location by using geolocation.getCurrentPosition()
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
