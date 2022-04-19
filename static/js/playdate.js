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
                    Recommended age group: ${responseJson.age_group}<br>
                    At ${responseJson.location}<br>
                    On ${responseJson.date} from ${responseJson.start_time} to ${responseJson.end_time}<br>
                    Activities: ${responseJson.activity_list.join(", ")}<br>
                    Hosted by ${responseJson.host}<br>
                    
                    <span class="inline">
                        <form class="follow" id="follow-${responseJson.event_id}">
                            <input type="hidden" name="user2_id" id="follow${responseJson.event_id}" value="${responseJson.host_id}">
                            <input class="btn btn-outline-info btn-sm" type="submit" value="Follow host">
                        </form>
                    </span>

                    <span class="inline">
                        <form class="like_park" id="like_park-${responseJson.event_id}">
                            <input type="hidden" name="location_id" id="like_park${responseJson.event_id}" value="${responseJson.location_id}">
                            <input class="btn btn-outline-success btn-sm" type="submit" value="Add park to favorites">
                        </form>
                    </span>
                    `
                    // Follow host feature
                    const follow_form = document.querySelector(`#follow-${responseJson.event_id}`);
                    follow_form.addEventListener("submit", (evt) => {
                        evt.preventDefault();
                        const followUrl = `/follow?user2_id=${responseJson.host_id}`;
                        console.log(followUrl);
                        // fetch and sending data
                        fetch(followUrl)
                            .then(reply => reply.json())
                            .then(dataJson => {
                                if (dataJson.success === true) {
                                    alert(`You successfully followed ${dataJson.friend}.`);
                                } else if (dataJson.success === "self") {
                                    alert(`${dataJson.reason}`);
                                } else if (dataJson.success === "no") {
                                    alert(`${dataJson.reason}`);
                                } else {
                                    alert(`${dataJson.reason}`);
                                }
                            })
                    })

                    // Add park to favorite feature
                    const likePark = document.querySelector(`#like_park-${responseJson.event_id}`);
                    likePark.addEventListener("submit", (evt) => {
                        evt.preventDefault();
                        const likeParkUrl = `/like_park?location_id=${responseJson.location_id}`;
                        console.log(likeParkUrl);
                        // fetch and sending data
                        fetch(likeParkUrl)
                            .then(reply => reply.json())
                            .then(dataJson => {
                                if (dataJson.success === true) {
                                    alert(`You successfully added this park to your favorites.`);
                                }
                                else if (dataJson.success === false) {
                                    alert(`You already liked this park.`);
                                } else {
                                    alert('You need to log in to add parks to favorites.')
                                }
                            })
                    })
                    
                    
                    // if upcoming events and this user hasn't registered, show Attend 
                    if (button.value === "upcoming_event") {
                        console.log(button.id);
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `<span class="inline">
                            <form action="/attend"> 
                                <input type="hidden" name="event_id" value="${button.id}">
                                <input class="btn btn-outline-warning btn-sm" type="submit" value="Attend">
                            </form>
                        </span>
                        `)
                    }
                    // if host event, show Cancel form
                    if (button.value === "host_event") {
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `
                        <span class="inline" id="cancel_host">
                            <form action="/cancel_event" method="POST" onsubmit="return confirm('Do you really want to cancel this playdate?');">
                                <input type="hidden" name="event_id" value="${button.id}">
                                <input class="btn btn-outline-danger btn-sm" type="submit" value="Cancel playdate">
                            </form>
                        </span>
                        `)
                    }
                    // if attending event, show Cancel registration form
                    if (button.value === "attending_event") {
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `
                        <span class="inline" id="cancel_registration">
                            <form action="/cancel_registration" method="POST" onsubmit="return confirm('Do you really want to cancel this registration?');">
                                <input type="hidden" name="event_id" value="${button.id}">
                                <input class="btn btn-outline-danger btn-sm" type="submit" value="Cancel registration">
                            </form>
                        </span>
                        `)
                    }
                    // if hosting or attending future events, show Invite friends form
                    if (button.classList.contains("invite_friends")) {
                        // document.getElementById(`invite${button.id}`).innerHTML =
                        document.getElementById(`display-detail${button.id}`).insertAdjacentHTML("beforeend", 
                        `
                        <span class="inline" id="invitation">
                            <form action="/invite">
                                <input type="hidden" name="event_id" value="${button.id}">
                                <input class="btn btn-outline-warning btn-sm" type="submit" value="Invite friends">
                            </form>
                        </span>
                        `)
                    }
                    
                } else { // Hide event details
                    button.innerText = "Show details";
                    document.getElementById(`display-detail${button.id}`).innerHTML = "";
                }
            })
    });
}










