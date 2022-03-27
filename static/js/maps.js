'use strict';

// Display a map and mark locations on the map
function otherMap() {
    // Geocode the location when host submits the hosting form
    // Select the form and add event handler
    document.getElementById("host_form").addEventListener("submit", () => {
        // Get the full address of the event
        const locationAddress = document.getElementById("address").value + ", " +
                                document.getElementById("city").value + ", " +
                                document.getElementById("state").value + " " +
                                document.getElementById("zipcode").value;
        console.log(locationAddress);
        // Geocode the address to coordinates
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ address: locationAddress }, (results, status) => {
            if (status === 'OK') {
                // sending AJAX to update the coordinates in the database 
                const coordinates = {
                    lat: results[0].geometry.location.lat(),
                    lng: results[0].geometry.location.lng(),
                    name: document.getElementById("location").value,
                    address: document.getElementById("address").value
                };
                alert(`coordinates ${coordinates}`);
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
        })
    });




    

    
}