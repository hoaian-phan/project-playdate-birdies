'use strict';

// Put a basic map on the search result page
function initMap() {
  console.log("Map loaded")
  const sfBayCoords = {
      lat: 37.601773,
      lng: -122.20287,
    };
  
  const basicMap = new google.maps.Map(document.querySelector('#map'), {
      center: sfBayCoords,
      zoom: 11,
  });

  const sfMarker = new google.maps.Marker({
      position: sfBayCoords,
      title: 'SF Bay',
      map: basicMap,
  });

  sfMarker.addListener('click', () => {
      alert('Hi!');
  });

  const sfInfo = new google.maps.InfoWindow({
      content: '<h1>San Francisco Bay!</h1>',
  });

  sfInfo.open(basicMap, sfMarker);
}
