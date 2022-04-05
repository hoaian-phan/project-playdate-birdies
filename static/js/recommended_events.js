'use strict';
// This file is used for :
// 1. autocomplete user's physical address
// 2. get coordinates of user's address
// 3. search by radius for near by locations



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
}

