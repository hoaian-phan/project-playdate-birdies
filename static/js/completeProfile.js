'use strict';
// This file is used for :
// 1. autocomplete user's physical address
// 2. get coordinates of user's address
// 3. search by radius for near by locations


// Display a map and mark locations on the map
function userMap() {
    // Put a basic map on the search result page
    const basicMap = new google.maps.Map(document.querySelector('#map'), {
        center: {
            lat: 37.601773,
            lng: -122.20287,
        },
        zoom: 11,
    });

// 1. Use autocomplete for user's home address
// Create the search box and link it to the UI element.
    let address = document.getElementById("address");
    let coordinates;
    
    const autocomplete = new google.maps.places.Autocomplete(address, {
        componentRestrictions: { country: "us" },
        fields: ["geometry", "formatted_address"],
        types: ["address"],
    });
    // When user chooses an address, get full address and coordinates information
    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();

        if (!place.geometry || !place.geometry.location) {
            console.log("Returned place contains no geometry");
            return;
        }
        // Save full address and coordinates
        address = place.formatted_address;
        console.log("full address", address);
        

        coordinates = {
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng()
        }
        console.log("coordinates", coordinates.lat, coordinates.lng);
    });
    
    // Select the form and upon submitting, send AJAX request to update coordinates and full address of the user in database
    document.getElementById("profile").addEventListener("submit", () => {
        const userAddress = {
            lat: coordinates.lat,
            lng: coordinates.lng,
            address: address,
        };
    
        fetch("/update_profile", {
            method: 'POST',
            body: JSON.stringify(userAddress),
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(reply => reply.json())
            .then(replyJson => {
                const status = replyJson.status;
                console.log(status);
            })
        });
}
