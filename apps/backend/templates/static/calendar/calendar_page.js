const addEventButton = document.querySelector(".add-event-btn-top");
const addEventButtonBottom = document.querySelector(".add-event-btn-bottom");
const dayButtons = document.querySelectorAll(".day-calendar");

const addEventPopup = document.querySelector(".add-event-container"); //popup represents the add-event container
const showEventsPopup = document.querySelector(".events-list-container"); //popup represents the add-event container


addEventButton.addEventListener("click", () => {
    addEventButton.classList.add("hidden"); //Hides the add-event-button once clicked
    showEventsPopup.classList.add("hidden"); //Hides the show event popup if it was already present

    addEventPopup.classList.remove("hidden"); //Makes the add-event popup appear if you press the add event button

    requestAnimationFrame(() => {
        addEventPopup.classList.add("show");
    });
});

addEventButtonBottom.addEventListener("click", () => {
    addEventButton.classList.add("hidden"); //Hides the add-event-button once clicked
    showEventsPopup.classList.add("hidden"); //Hides the show event popup if it was already present

    addEventPopup.classList.remove("hidden"); //Makes the add-event popup appear if you press the add event button

    requestAnimationFrame(() => {
        addEventPopup.classList.add("show");
    });
});

const cancelButton = document.querySelector(".cancel-btn");

cancelButton.addEventListener("click", () => {
    addEventPopup.classList.add("hidden"); //Makes the add-event popup hidden if you press the cancel button
    addEventPopup.classList.remove("show");

    addEventButton.classList.remove("hidden"); //Add event button reappears once you exit the popup
})

const addEventCancelButton = document.querySelector("#add-event-cancel-btn");

addEventCancelButton.addEventListener("click", () => {
    addEventPopup.classList.add("hidden"); //Makes the add event popup hidden if you press the x button
    addEventPopup.classList.remove("show"); //Removes the show class

    addEventButton.classList.remove("hidden"); //Add event button reappears once you exit the popup
})


const showEventsCancelButton = document.querySelector("#show-events-cancel-btn");

showEventsCancelButton.addEventListener("click", () => { //Makes the show-events popup hidden if you press the x button
    showEventsPopup.classList.add("hidden");

    addEventPopup.classList.remove("show"); //Removes the show class
})