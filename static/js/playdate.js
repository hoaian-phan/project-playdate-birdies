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
                document.querySelector("#display-details").innerHTML = 
                `
                <b>Playdate details<br>
                Title: ${responseJson.title}</b><br>
                ${responseJson.description}<br>
                For ${responseJson.age_group}<br>
                Hosted by ${responseJson.host}<br>
                At ${responseJson.location}<br>
                Address: ${responseJson.address}, ${responseJson.city}, ${responseJson.state} ${responseJson.zipcode}<br>
                On ${responseJson.date} from ${responseJson.start_time} to ${responseJson.end_time}<br>
                `  
            })
    })
};











