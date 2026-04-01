const singleDayCheckbox = document.getElementById("singleDay");
singleDayCheckbox.addEventListener("change", singleDaySwitched);

function singleDaySwitched() {
    const finishDate = document.getElementById("finishDate")
    if (singleDayCheckbox.checked) {
        finishDate.style.display = "none";
    } else {
        finishDate.style.display = "block";
    }
}

const newEventForm = document.getElementById("newEventForm");
newEventForm.addEventListener("submit", timesValidation);

function timesValidation(event) {
    if (!validateTimes()) {
        event.preventDefault();
    }
}

function validateTimes() {
    const startDate = document.getElementById("startDate").value;
    const startTime = document.getElementById("startTime").value;
    let finishDate = document.getElementById("finishDate").value;
    const finishTime = document.getElementById("finishTime").value;

    if (singleDayCheckbox.checked) {
        finishDate = startDate;
    }
    if (startDate == "" || finishDate == "") {
        return true; // Allow undecided dates)
    } else if (startDate > finishDate) {
        alert("The finish date and time must be after the start date and time.");
        return false;
    } else if (startTime == "" || finishTime == "") {
        return true; // Allow undecided times
    } else if (startDate == finishDate && startTime >= finishTime) {
        alert("The finish time must be after the start time.");
        return false;
    }
    return true;
}

