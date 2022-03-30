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
                if (button.innerText === "Show details") {
                    button.innerText = "Hide details";
                    document.getElementById(`display-detail${button.id}`).innerHTML = 
                    `
                    
                    ${responseJson.description}<br>
                    Recommended age group: ${responseJson.age_group}<br>
                    At ${responseJson.location}<br>
                    Address: ${responseJson.address}, ${responseJson.city}, ${responseJson.state} ${responseJson.zipcode}<br>
                    On ${responseJson.date} from ${responseJson.start_time} to ${responseJson.end_time}<br>
                    Activities: ${responseJson.activity_list.join(", ")}<br>
                    Hosted by ${responseJson.host}<br>
                    
                    <form id="follow">
                        <input type="hidden" name="user2_id" value="${responseJson.host_id}">
                        <input type="submit" value="Follow host">
                    </form>
                    `
                    // Follow the host: add event handler
                    const follow_btns = document.querySelectorAll("#follow");
                    if (follow_btns) {
                        for (const btn of follow_btns) {
                            btn.addEventListener("submit", (evt) => {
                                evt.preventDefault();
                                const followUrl = `/follow?user2_id=${responseJson.host_id}`;
                                // fetch and sending data
                                fetch(followUrl)
                                    .then(reply => reply.json())
                                    .then(dataJson => {
                                        if (dataJson.success === true) {
                                            alert(`You successfully followed ${responseJson.host}.`)
                                        }
                                        else {
                                            alert(`You already followed ${responseJson.host}.`)
                                        }
                                    })
                            })
                        }
                    }
                    
                    // if upcoming events and this user hasn't registered, show Attend 
                    if ((button.value === "upcoming_event") & (!responseJson.is_registered )) {
                        console.log(button.id);
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `<form action="/attend"> 
                            <input type="hidden" name="event_id" value="${button.id}">
                            <input type="submit" value="Attend">
                        </form>
                        `)
                    }
                    // if host event, show Cancel form
                    if (button.value === "host_event") {
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `
                        <div id="cancel_host">
                            <form action="/cancel_event" method="POST" onsubmit="return confirm('Do you really want to cancel this playdate?');">
                                <input type="hidden" name="event_id" value="${button.id}">
                                <input type="submit" value="Cancel playdate">
                            </form>
                        </div>
                        `)
                    }
                    // if attending event, show Cancel registration form
                    if (button.value === "attending_event") {
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `
                        <div id="cancel_registration">
                            <form action="/cancel_registration" method="POST" onsubmit="return confirm('Do you really want to cancel this registration?');">
                                <input type="hidden" name="event_id" value="${button.id}">
                                <input type="submit" value="Cancel registration">
                            </form>
                        </div>
                        `)
                    }
                    
                } else { // Hide event details
                    button.innerText = "Show details";
                    document.getElementById(`display-detail${button.id}`).innerHTML = "";
                }
            })
    });
}




// If host chooses to add activities in their hosting form
// Select the element with id "add_activities" and set display to none
const suggestedActivities = document.getElementById('suggested_activities');
if (suggestedActivities) {
    suggestedActivities.style.display = 'none';
}
// Select the element with id "other" and add event handler
const addActivities = document.getElementById('add_activities');
if (addActivities) {
    addActivities.addEventListener('change', () => {
        if(addActivities.checked) {
            suggestedActivities.style.display = 'block';
            suggestedActivities.value = '';
        } else {
            suggestedActivities.style.display = 'none';
        }
    });
}


// Adding other activities in text box in hosting form (hosting.html)
// Select the element with id "otherValue" and set display to none
const otherText = document.getElementById('otherActivity');
if (otherText) {
    otherText.style.visibility = 'hidden';
}
// Select the element with id "other" and add event handler
const otherCheckbox = document.getElementById('other');
if (otherCheckbox) {
    otherCheckbox.addEventListener('change', () => {
        if(otherCheckbox.checked) {
            otherText.style.visibility = 'visible';
            otherText.value = '';
        } else {
            otherText.style.visibility = 'hidden';
        }
    });
}








