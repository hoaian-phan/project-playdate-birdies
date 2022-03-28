'use strict';

// This function uses: 1. autocomplete searchbox to suggest the full address of the location,
// 2. geocoding to get location's coordinates 
// 3. textSearch to get location's photo
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
    })
        // // 2. Get the coordinates of the location
        // coordinates = {
        //     lat: place.geometry.location.lat(),
        //     lng: place.geometry.location.lng()
        // };
        // console.log(`lat: ${coordinates.lat}, lng: ${coordinates.lng}`);
        // // 3. Get photo of the location by TextSearch
        // const request = {
        //     location: coordinates,
        //     radius: '50',
        //     query: place.formatted_address,
        // };
        // const photoRequest = new google.maps.places.PlacesService(basicMap);
        // console.log(photoRequest);
        // let photoUrl;
        // photoRequest.textSearch(request, (results, status) => {
        //     console.log("trying to get photo");
        //     if (status === 'OK') {
        //         // Save place photo object in an array
        //         const photos = results[0].photos;
        //         if (!photos) {
        //             return;
        //         }                
        //         // Get url of the first photo
        //         photoUrl = photos[0].getUrl({maxWidth: 500, maxHeight: 500});
        //         console.log(`inside if, photo link: ${photoUrl}`);
        //     } else {
        //         alert(`TextSearch was unsuccessful for the following reason: ${status}`);
        //     }
        //     console.log(`outside if, photo link: ${photoUrl}`);
        // });
        

        // // When the host submits the form, send AJAX request to update coordinates and photo of the event location
        // document.getElementById("host_form").addEventListener("submit", () => {
        //     // evt.preventDefault();
        //     console.log("Form submitted")
        //     const locationDetails = {
        //         lat: coordinates.lat,
        //         lng: coordinates.lng,
        //         photo: photoUrl,
        //         name: document.getElementById("location").value,
        //         address: address,
        //     };
        //     alert(`locationDetails ${locationDetails}`);
        //     fetch("/update_location_details", {
        //         method: 'POST',
        //         body: JSON.stringify(locationDetails),
        //         headers: {
        //             'Content-Type': 'application/json',
        //         },
        //     })
        //         .then(reply => reply.json())
        //         .then(replyJson => {
        //             const status = replyJson.status;
        //             console.log(status);
        //         })
        //     });
        // });
    

    


    // Geocode the location when host submits the hosting form
    // Select the form and add event handler
    document.getElementById("host_form").addEventListener("submit", () => {
        
        // Get the full address of the event
        const locationAddress = document.getElementById("address").value + ", " +
                                document.getElementById("city").value + ", " +
                                document.getElementById("state").value + " " +
                                document.getElementById("zipcode").value;
        console.log(`locationAddress : ${locationAddress}`);
        // Geocode the address to coordinates
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ address: locationAddress }, (results, status) => {
            if (status === 'OK') {
                // Save coordinates 
                const coords = {
                    lat: results[0].geometry.location.lat(),
                    lng: results[0].geometry.location.lng()
                };
                console.log(`coordinates ${coords.lat}, ${coords.lng}`);
                // const park = new google.maps.LatLng(37.4464501, -121.8964089);
                // Get photo of the location by TextSearch
                const request = {
                    location: coords,
                    radius: '500',
                    query: locationAddress
                };
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
                    console.log(`outside if, photo link: ${photoUrl}`);
                    // Sending AJAX to update the coordinates and photo of location in the database 
                    const locationDetails = {
                        lat: coords.lat,
                        lng: coords.lng,
                        photo: photoUrl,
                        name: document.getElementById("location").value,
                        address: document.getElementById("address").value
                    };
                    alert(`locationDetails ${locationDetails}`);
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
                })    
            } else {
                alert(`Geocode was unsuccessful for the following reason: ${status}`);
            }
            
        });
        
    });  
}