'use strict';

// Display a map and mark locations on the map
function otherMap() {
    const basicMap = new google.maps.Map(document.querySelector('#map'), {
        center: {
            lat: 37.601773,
            lng: -122.20287,
        },
        zoom: 11,
    });
    // Geocode the location when host submits the hosting form
    // Select the form and add event handler
    document.getElementById("host_form").addEventListener("submit", () => {
        // evt.preventDefault();
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
                // Get photo of the location by TextSearch
                const request = {
                    location: coords,
                    radius: '50',
                    query: 'locationAddress'
                  };
                const photoRequest = new google.maps.places.PlacesService(basicMap);
                console.log(photoRequest);
                let photoUrl;
                photoRequest.textSearch(request, (results, status) => {
                    console.log("trying to get photo");
                    if (status === 'OK') {
                        // Save place photo object in an array
                        const photos = results[0].photos;
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
            
        })
        
        
        
            
    })




    

    
}