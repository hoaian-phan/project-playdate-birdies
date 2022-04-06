'use strict';
// This file is used for :
// 1. search by radius for near by locations
// 2. Compute the distance between places



// Display a map and mark locations on the map
function nearbyMap() {
    // Put a basic map on the search result page
    const basicMap = new google.maps.Map(document.querySelector('#map'), {
        center: {
            lat: 37.601773,
            lng: -122.20287,
        },
        zoom: 11,
    });
    // Send fetch request to get user's home coordinates
    document.addEventListener('DOMContentLoaded', () => {
        let user_location;
        fetch("/nearby")
            .then(reply => reply.json())
            .then(dataJson => {
                if (dataJson.lat && dataJson.lng){
                    console.log(typeof(dataJson.lat), typeof(dataJson.lng));
                    user_location = {
                        "lat" : dataJson.lat,
                        "lng" : dataJson.lng,
                    };
                }
                //Request to be sent to nearbySearch
                const request = {
                    location: user_location,
                    radius: '8000',
                    type: ['park']
                };
                console.log(`request: ${request.location.lat}, ${request.location.lng} `)

                // Search for parks around user's home address using nearbySearch
                let listResults = [];
                const service = new google.maps.places.PlacesService(basicMap);
                console.log(service);
                // Use nearbySearch and get the first 10 closest parks
                service.nearbySearch(request, (results, status)  => {
                    
                    if (status == google.maps.places.PlacesServiceStatus.OK) {
                        console.log(results.length);
                        for (let i = 0; i < results.length; i++) {
                            console.log(results[i]);
                            listResults.push(results[i]);
                        }
                    }
                })
                

            })
    

         
    });
}