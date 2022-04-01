'use strict';
// This file is for DOM manipulation in the hosting form

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