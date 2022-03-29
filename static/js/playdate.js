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
                    For ${responseJson.age_group}.
                    Hosted by ${responseJson.host}<br>
                    At ${responseJson.location}<br>
                    Address: ${responseJson.address}, ${responseJson.city}, ${responseJson.state} ${responseJson.zipcode}<br>
                    On ${responseJson.date} from ${responseJson.start_time} to ${responseJson.end_time}<br>
                    Activities: ${responseJson.activity_list.join(", ")}<br>
                    Who's coming: Family of ${responseJson.attendants.join(", ")}<br>
                    `
                    // if upcoming events, show Register form
                    if (button.value === "upcoming_event") {
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
                                <input type=submit value="Cancel registration">
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
suggestedActivities.style.display = 'none';
// Select the element with id "other" and add event handler
const addActivities = document.getElementById('add_activities');
addActivities.addEventListener('change', () => {
    if(addActivities.checked) {
        suggestedActivities.style.display = 'block';
        suggestedActivities.value = '';
    } else {
        suggestedActivities.style.display = 'none';
    }
});


// Adding other activities in text box in hosting form (hosting.html)
// Select the element with id "otherValue" and set display to none
const otherText = document.getElementById('otherActivity');
otherText.style.visibility = 'hidden';
// Select the element with id "other" and add event handler
const otherCheckbox = document.getElementById('other');
otherCheckbox.addEventListener('change', () => {
    if(otherCheckbox.checked) {
        otherText.style.visibility = 'visible';
        otherText.value = '';
    } else {
        otherText.style.visibility = 'hidden';
    }
});


// Adding list of items and quantity in hosting form (hosting.html) if host chooses to
// Select the element with id "add" and add event handler to insert element
const add_btn = document.getElementById('add');
let i = 0; // to set unique id for each item
add_btn.addEventListener("click", () => {
    i += 1; 
    document.getElementById('item_quantity').insertAdjacentHTML("beforeend",
        `
        <li id="item_quantity_${i}">
            <label for="item_${i}">Item</label>
            <input type="text" id="item_${i}" name="item">
            <label for="quantity_${i}">Quantity</label>
            <input type="text" id="quantity_${i}" name="quantity">
            <button type="button" id="delete_${i}" name="delete">Delete</button>
            <br>
        </li>
        `)
    // Select the element with id "delete" and add event handler to delete element
    const delete_btn = document.getElementById(`delete_${i}`);
    delete_btn.addEventListener("click", () => {
        delete_btn.parentElement.remove();
    });
});
// Count how many equipments ( how many child element of <ul>)
const numEquipment = document.querySelector("#item_quantity").childElementCount;
document.querySelector("#item_quantity").value = numEquipment;





