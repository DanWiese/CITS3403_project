const singleDayCheckbox = document.getElementById("singleDay");
const finishDate = document.getElementById("finishDate");
const finishTime = document.getElementById("finishTime");
const pollsCheckbox = document.getElementById("pollsCheckbox");
const expensesCheckbox = document.getElementById("expensesCheckbox");
const discussionCheckbox = document.getElementById("discussionCheckbox");

singleDayCheckbox.addEventListener("change", singleDaySwitched);
pollsCheckbox.addEventListener("change", toggleOptionalTabs);
document.getElementById("startDate").addEventListener("input", syncSingleDayDates);
document.getElementById("startTime").addEventListener("input", syncSingleDayDates);

function singleDaySwitched() {
    if (singleDayCheckbox.checked) {
        finishDate.style.display = "none";
        finishTime.style.display = "none";
        syncSingleDayDates();
    } else {
        finishDate.style.display = "block";
        finishTime.style.display = "block";
    }
}

function syncSingleDayDates() {
    if (!singleDayCheckbox.checked) {
        return;
    }

    const startDateValue = document.getElementById("startDate").value;
    const startTimeValue = document.getElementById("startTime").value;

    finishDate.value = startDateValue;

    if (startTimeValue) {
        const [hours, minutes] = startTimeValue.split(":").map(Number);
        const endTimeDate = new Date();
        endTimeDate.setHours(hours, minutes, 0, 0);
        endTimeDate.setMinutes(endTimeDate.getMinutes() + 60);

        const endHours = String(endTimeDate.getHours()).padStart(2, "0");
        const endMinutes = String(endTimeDate.getMinutes()).padStart(2, "0");
        finishTime.value = `${endHours}:${endMinutes}`;
    }
}

function toggleOptionalTabs() {
    expensesCheckbox.disabled = !pollsCheckbox.checked;
    discussionCheckbox.disabled = !pollsCheckbox.checked;

    if (!pollsCheckbox.checked) {
        expensesCheckbox.checked = false;
        discussionCheckbox.checked = false;
    }
}

const newEventForm = document.getElementById("newEventForm");
newEventForm.addEventListener("submit", timesValidation);

async function timesValidation(event) {
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
        start_date: document.getElementById("startDate").value,
        start_time: document.getElementById("startTime").value,
        end_date: finishDate.value,
        end_time: finishTime.value,
        single_day: singleDayCheckbox.checked,
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
    const startDate = document.getElementById("startDate").value;
    const startTime = document.getElementById("startTime").value;
    let finishDateValue = finishDate.value;
    const finishTimeValue = finishTime.value;

    if (singleDayCheckbox.checked) {
        finishDateValue = startDate;
        finishDate.value = startDate;

        if (startTime && (!finishTimeValue || startTime >= finishTimeValue)) {
            syncSingleDayDates();
        }
    }
    if (startDate == "" || finishDateValue == "") {
        return true; // Allow undecided dates)
    } else if (startDate > finishDateValue) {
        alert("The finish date and time must be after the start date and time.");
        return false;
    } else if (startTime == "" || finishTimeValue == "") {
        return true; // Allow undecided times
    } else if (startDate == finishDateValue && startTime >= finishTimeValue) {
        alert("The finish time must be after the start time.");
        return false;
    }
    return true;
}

toggleOptionalTabs();
singleDaySwitched();

