const EVENTS_API_URL = "/events";
const singleDayCheckbox = document.getElementById("singleDay");
const newEventForm = document.getElementById("newEventForm");
let dashboardEvents = [];

if (singleDayCheckbox) {
    singleDayCheckbox.addEventListener("change", singleDaySwitched);
}

if (newEventForm) {
    newEventForm.addEventListener("submit", handleEventFormSubmit);
}

document.addEventListener("DOMContentLoaded", () => {
    initDashboard();
});

function singleDaySwitched() {
    const finishDate = document.getElementById("finishDate");
    if (!finishDate) {
        return;
    }

    if (singleDayCheckbox.checked) {
        finishDate.style.display = "none";
    } else {
        finishDate.style.display = "block";
    }
}

function handleEventFormSubmit(event) {
    if (!validateTimes()) {
        event.preventDefault();
        return;
    }

    event.preventDefault();
    const submitButton = getSubmitButton();
    setSubmitState(true, submitButton);

    const eventData = getEventFormData();
    postEvent(eventData)
        .then(() => {
            window.location.href = "dashboard.html";
        })
        .catch((error) => {
            setSubmitState(false, submitButton);
            console.error("Event save failed:", error);
            alert("Unable to save event right now. Please try again later.");
        });
}

function getEventFormData() {
    const title = document.getElementById("eventName").value.trim();
    const location = document.getElementById("location").value.trim();
    const description = document.getElementById("description").value.trim();
    const startDate = document.getElementById("startDate").value;
    const startTime = document.getElementById("startTime").value;
    let finishDate = document.getElementById("finishDate").value;
    const finishTime = document.getElementById("finishTime").value;
    const singleDay = singleDayCheckbox ? singleDayCheckbox.checked : false;
    const tabs = Array.from(document.querySelectorAll("#tabCheckboxes input[type=checkbox]:checked")).map((checkbox) => checkbox.value);

    if (singleDay) {
        finishDate = startDate;
    }

    return {
        title: title || "Untitled Event",
        location,
        description,
        startDate,
        startTime,
        finishDate,
        finishTime,
        singleDay,
        tabs,
        tag: inferEventTag(title, tabs),
        createdAt: new Date().toISOString(),
        rsvpCount: 0
    };
}

function inferEventTag(title, tabs) {
    const normalized = title.toLowerCase();
    if (normalized.includes("wedding") || normalized.includes("ceremony")) {
        return "Wedding";
    }
    if (normalized.includes("conference") || normalized.includes("summit") || normalized.includes("tech")) {
        return "Conference";
    }
    if (normalized.includes("party") || normalized.includes("gathering") || normalized.includes("celebration")) {
        return "Party";
    }
    if (tabs.includes("polls")) {
        return "Polls";
    }
    return "Event";
}

function validateTimes() {
    const startDate = document.getElementById("startDate").value;
    const startTime = document.getElementById("startTime").value;
    let finishDate = document.getElementById("finishDate").value;
    const finishTime = document.getElementById("finishTime").value;

    if (singleDayCheckbox && singleDayCheckbox.checked) {
        finishDate = startDate;
    }
    if (startDate === "" || finishDate === "") {
        return true; // Allow undecided dates
    } else if (startDate > finishDate) {
        alert("The finish date and time must be after the start date and time.");
        return false;
    } else if (startTime === "" || finishTime === "") {
        return true; // Allow undecided times
    } else if (startDate === finishDate && startTime >= finishTime) {
        alert("The finish time must be after the start time.");
        return false;
    }
    return true;
}

function getSubmitButton() {
    return newEventForm?.querySelector('input[type="submit"], button[type="submit"]');
}

function setSubmitState(isLoading, button) {
    if (!button) {
        return;
    }
    button.disabled = isLoading;
    if (button.tagName.toLowerCase() === "input") {
        button.value = isLoading ? "Saving…" : "Create";
    } else {
        button.textContent = isLoading ? "Saving…" : "Create";
    }
}

function postEvent(eventObj) {
    return fetch(EVENTS_API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(eventObj)
    }).then(checkResponse);
}

function fetchEvents() {
    return fetch(EVENTS_API_URL).then(checkResponse);
}

function checkResponse(response) {
    if (!response.ok) {
        return response.text().then((text) => {
            const message = text || response.statusText || "Server error";
            throw new Error(message);
        });
    }
    return response.json();
}

function initDashboard() {
    const eventsGrid = document.querySelector(".events-grid");
    if (!eventsGrid) {
        return;
    }

    const loader = document.getElementById("dashboardLoader");
    const errorMessage = document.getElementById("load-error-message");

    if (loader) {
        loader.style.display = "block";
    }
    if (errorMessage) {
        errorMessage.style.display = "none";
    }

    const filterButtons = document.querySelectorAll(".filter-btn");
    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            document.querySelectorAll(".filter-btn").forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
            renderEvents(dashboardEvents, button.dataset.filter || "all");
        });
    });

    fetchEvents()
        .then((events) => {
            dashboardEvents = Array.isArray(events) ? events : [];
            renderEvents(dashboardEvents);
        })
        .catch((error) => {
            if (loader) {
                loader.style.display = "none";
            }
            if (errorMessage) {
                errorMessage.textContent = "Unable to load events. Please try again later.";
                errorMessage.style.display = "block";
            }
            console.error("Failed to load events:", error);
        });
}

function renderEvents(events = [], filter = "all") {
    const eventsGrid = document.querySelector(".events-grid");
    const noEventsMessage = document.getElementById("no-events-message");
    const loader = document.getElementById("dashboardLoader");
    const errorMessage = document.getElementById("load-error-message");

    if (loader) {
        loader.style.display = "none";
    }
    if (errorMessage) {
        errorMessage.style.display = "none";
    }

    const now = new Date();
    const shownEvents = events.filter((eventObj) => {
        if (filter === "all") {
            return true;
        }
        const endDate = eventObj.finishDate || eventObj.startDate;
        const endTime = eventObj.finishTime || "23:59";
        const eventEnd = new Date(`${endDate}T${endTime}`);
        return filter === "upcoming" ? eventEnd >= now : eventEnd < now;
    });

    eventsGrid.innerHTML = "";

    if (shownEvents.length === 0) {
        if (noEventsMessage) {
            noEventsMessage.style.display = "block";
        }
    } else {
        if (noEventsMessage) {
            noEventsMessage.style.display = "none";
        }
        shownEvents.forEach((eventObj) => {
            eventsGrid.appendChild(createEventCard(eventObj));
        });
    }

    updateStats(events);
}

function updateStats(events) {
    const upcomingCount = document.getElementById("upcoming-count");
    const pastCount = document.getElementById("past-count");
    const rsvpCount = document.getElementById("rsvp-count");
    const totalCount = document.getElementById("total-count");

    const now = new Date();
    const upcomingEvents = events.filter((eventObj) => {
        const endDate = eventObj.finishDate || eventObj.startDate;
        const endTime = eventObj.finishTime || "23:59";
        return new Date(`${endDate}T${endTime}`) >= now;
    }).length;
    const pastEvents = events.length - upcomingEvents;
    const totalRsvps = events.reduce((sum, eventObj) => sum + (eventObj.rsvpCount || 0), 0);

    if (upcomingCount) {
        upcomingCount.textContent = upcomingEvents;
    }
    if (pastCount) {
        pastCount.textContent = pastEvents;
    }
    if (rsvpCount) {
        rsvpCount.textContent = totalRsvps;
    }
    if (totalCount) {
        totalCount.textContent = events.length;
    }
}

function createEventCard(eventObj) {
    const card = document.createElement("div");
    card.className = "event-card";

    const cardImage = document.createElement("div");
    cardImage.className = "card-image";

    const image = document.createElement("img");
    image.src = "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=600&q=80";
    image.alt = eventObj.title;

    const overlay = document.createElement("div");
    overlay.className = "card-image-overlay";

    const tag = document.createElement("span");
    tag.className = "event-tag";
    tag.textContent = eventObj.tag || "Event";

    const badge = document.createElement("div");
    badge.className = "event-date-badge";
    const startDate = eventObj.startDate || "";
    const { month, day } = formatMonthDay(startDate);
    badge.innerHTML = `<div class="date-month">${month}</div><div class="date-day">${day}</div>`;

    cardImage.appendChild(image);
    cardImage.appendChild(overlay);
    cardImage.appendChild(tag);
    cardImage.appendChild(badge);

    const cardBody = document.createElement("div");
    cardBody.className = "card-body";

    const title = document.createElement("h3");
    title.className = "event-title";
    title.textContent = eventObj.title;

    const desc = document.createElement("p");
    desc.className = "event-desc";
    desc.textContent = eventObj.description || "No description provided.";

    const footer = document.createElement("div");
    footer.className = "card-footer";

    const rsvp = document.createElement("div");
    rsvp.className = "rsvp-count";
    rsvp.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>${eventObj.rsvpCount || 0} RSVPs`;

    const actions = document.createElement("div");
    actions.className = "card-actions";
    ["Edit", "Share", "Delete"].forEach((titleText) => {
        const button = document.createElement("button");
        button.className = "action-btn";
        button.title = titleText;
        const icon = document.createElement("svg");
        icon.setAttribute("width", "13");
        icon.setAttribute("height", "13");
        icon.setAttribute("viewBox", "0 0 24 24");
        icon.setAttribute("fill", "none");
        icon.setAttribute("stroke", "currentColor");
        icon.setAttribute("stroke-width", "2");
        icon.setAttribute("stroke-linecap", "round");
        if (titleText === "Edit") {
            icon.innerHTML = '<path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>';
        } else if (titleText === "Share") {
            icon.innerHTML = '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>';
        } else {
            icon.innerHTML = '<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>';
        }
        button.appendChild(icon);
        actions.appendChild(button);
    });

    footer.appendChild(rsvp);
    footer.appendChild(actions);
    cardBody.appendChild(title);
    cardBody.appendChild(desc);
    cardBody.appendChild(footer);
    card.appendChild(cardImage);
    card.appendChild(cardBody);

    return card;
}

function formatMonthDay(dateString) {
    if (!dateString) {
        return { month: "--", day: "--" };
    }
    const date = new Date(dateString);
    if (Number.isNaN(date.getTime())) {
        return { month: "--", day: "--" };
    }
    const month = date.toLocaleString("en-US", { month: "short" }).toUpperCase();
    const day = String(date.getDate()).padStart(2, "0");
    return { month, day };
}

