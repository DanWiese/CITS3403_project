const singleDayCheckbox = document.getElementById("singleDay");
const startDate = document.getElementById("startDate");
const startTime = document.getElementById("startTime");
const finishDate = document.getElementById("finishDate");
const finishTime = document.getElementById("finishTime");
const pollsCheckbox = document.getElementById("pollsCheckbox");
const expensesCheckbox = document.getElementById("expensesCheckbox");
const discussionCheckbox = document.getElementById("discussionCheckbox");

singleDayCheckbox.addEventListener("change", singleDaySwitched);
startDate.addEventListener("input", syncSingleDayDates);

function singleDaySwitched() {
    if (singleDayCheckbox.checked) {
        // Keep finish date locked to the start date, but allow editing the finish time.
        finishDate.disabled = true;
        syncSingleDayDates();
    } else {
        finishDate.disabled = false;
    }
}

function syncSingleDayDates() {
    if (!singleDayCheckbox.checked) {
        return;
    }

    finishDate.value = startDate.value;
}

const newEventForm = document.getElementById("newEventForm");
newEventForm.addEventListener("submit", submission);

async function submission(event) {
    event.preventDefault();

    if (!validateTimes()) {
        return;
    }

    const selectedTabs = [];
    if (pollsCheckbox.checked) selectedTabs.push("polls");
    if (expensesCheckbox.checked) selectedTabs.push("expenses");
    if (discussionCheckbox.checked) selectedTabs.push("discussion");

    const privacyChoice = document.querySelector('input[name="privacy"]:checked');

    const payload = {
        title: document.getElementById("eventName").value.trim(),
        location: document.getElementById("location").value.trim(),
        description: document.getElementById("description").value.trim(),
        start_date: startDate.value,
        start_time: startTime.value,
        end_date: finishDate.value,
        end_time: finishTime.value,
        is_private: !privacyChoice || privacyChoice.value === "private",
        selected_tabs: selectedTabs
    };

    const response = await fetch("/events", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    let result = {};
    try {
        result = await response.json();
    } catch (error) {
        result = { message: "Unable to create event." };
    }

    if (!response.ok) {
        alert(result.message || "Unable to create event.");
        return;
    }

    window.location.href = result.redirect_url || "/dashboard";
}

function validateTimes() {
    syncSingleDayDates();
    const startDateValue = startDate.value;
    const startTimeValue = startTime.value;
    let finishDateValue = finishDate.value;
    const finishTimeValue = finishTime.value;

    if (startDateValue == "" || startTimeValue == "") {
        alert("The start date and time are required.");
        return false;
    } else if (finishDateValue == "") {
        if (finishTimeValue != "") {
            alert("The finish date is required if a finish time is entered.");
            return false;
        } else {
            return true; // Allow undecided finish date and time
        }
    } else if (startDateValue > finishDateValue) {
        alert("The finish date and time must be after the start date and time.");
        return false;
    } else if (startDateValue == finishDateValue && startTimeValue >= finishTimeValue) {
        alert("The finish time must be after the start time.");
        return false;
    }
    return true;
}

singleDaySwitched();

