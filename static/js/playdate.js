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
                document.querySelector("#display-details").innerHTML = "Playdate details";
                document.querySelector("#title").innerHTML = "Title: " + responseJson.title;
                document.querySelector("#description").innerHTML = responseJson.description;
                document.querySelector("#age").innerHTML = "For " + responseJson.age_group;
                document.querySelector("#host").innerHTML = "Hosted by " + responseJson.host;
                document.querySelector("#location").innerHTML = "At " + responseJson.location;
                document.querySelector("#address").innerHTML = "Address: " + responseJson.address 
                                                                + ", " + responseJson.city + ", " 
                                                                + responseJson.state + " " 
                                                                + responseJson.zipcode;
                document.querySelector("#date-time").innerHTML = "On " + responseJson.date
                                                                + " from " + responseJson.start_time
                                                                + " to " + responseJson.end_time;
            })
    })
};


