'use strict';

// This function serves the host feature. It uses
// 1. autocomplete to suggest addresses and upon chosen, it fills in the rest of the address,
// 2. also by autocomplete, it gets the coordinates of the location 
// 3. textSearch to get location's photo 
// 4. Sending AJAX call to server to update coordinates and photo of the location in the database

function otherMap() {
    // Create a basicMap, which will not be displayed on the page
    const basicMap = new google.maps.Map(document.querySelector('#map'), {
        center: {
            lat: 37.601773,
            lng: -122.20287,
        },
        zoom: 11,
    });

    // 1. Use Autocomplete Address Form to populate location's full address
    let addressField = document.getElementById("address");
    let postalField = document.getElementById("zipcode");
    let coords, fullAddress;
    
    // Create the autocomplete object, restricting the search predictions to addresses in the US 
    const autocomplete = new google.maps.places.Autocomplete(addressField, {
        componentRestrictions: { country: "us" },
        fields: ["address_components", "geometry", "formatted_address"],
        types: ["address"],
    });
    addressField.focus();
    // When the user selects an address from the drop-down: .
    autocomplete.addListener("place_changed", () => {
        // 1. Populate the address fields to fill in the rest of the address form
        // Get the place details from the autocomplete object
        const place = autocomplete.getPlace();
        console.log("geometry", place.geometry);
        if(!place.geometry) {
            // User did not select a prediction, reset the input field
            addressField.placeholder = "Enter an address";
        }
        let address = "";
        let postcode = "";
        // Get each component of the address from the place details, and fill-in the corresponding field on the form.
        for (const component of place.address_components) {
            const componentType = component.types[0];

            switch (componentType) {
                case "street_number": {
                    address = `${component.long_name} ${address}`;
                    break;
                }
                case "route": {
                    address += component.short_name;
                    break;
                }
                case "postal_code": {
                    postcode = `${component.long_name}${postcode}`;
                    break;
                }
                case "postal_code_suffix": {
                    postcode = `${postcode}-${component.long_name}`;
                    break;
                }
                case "locality": {
                    document.querySelector("#city").value = component.long_name;
                    break;
                }
                case "administrative_area_level_1": {
                    document.querySelector("#state").value = component.short_name;
                    break;
                }
            }
        }
        addressField.value = address;
        postalField.value = postcode;

        // 2. Save location coordinates 
        coords = {
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng()
        };
        
        // Save full address for looking up photos
        fullAddress = place.formatted_address;
        
    })
    

    // Select the form and upon submitting, send AJAX request to update coordinates and photo of the location in database
    document.getElementById("host_form").addEventListener("submit", () => {
        
        // Get photo of the location by TextSearch
        const request = {
            location: coords,
            radius: '500',
            query: document.getElementById("location").value + " " + fullAddress,
        };
        console.log(` textSearch query ${request.query}`);
        const photoRequest = new google.maps.places.PlacesService(basicMap);
        console.log(photoRequest);
        let photoUrl;
        photoRequest.textSearch(request, (results, status) => {
            console.log("trying to get photo");
            console.log(results);
            if (status === 'OK') {
                // Save place photo object in an array
                const photos = results[0].photos;
                console.log(photos);
                if (!photos) {
                    return;
                }                
                // Get url of the first photo
                photoUrl = photos[0].getUrl({maxWidth: 500, maxHeight: 500});
                console.log(`inside if, photo link: ${photoUrl}`);
            } else {
                alert(`TextSearch was unsuccessful for the following reason: ${status}`);
            }
            // Sending AJAX to update the coordinates and photo of location in the database 
            const locationDetails = {
                lat: coords.lat,
                lng: coords.lng,
                photo: photoUrl,
                name: document.getElementById("location").value,
                address: document.getElementById("address").value
            };
           
            fetch("/update_location_details", {
                method: 'POST',
                body: JSON.stringify(locationDetails),
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
        
    });
}