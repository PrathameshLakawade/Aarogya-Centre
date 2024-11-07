// Book Appointment Card
function showCity() {
    document.getElementById("appointment-city").style.display = 'block';
}

function hideCity() {
    document.getElementById("appointment-city").style.display = 'none';
}

// Healthcare Chatbot
function openChat() {
    document.getElementById("chat-form").style.display = "block";
    document.getElementById("open-button").style.display = "none";
    document.getElementById("close-button").style.display = "block";
    document.getElementById('navigation-bar').style.opacity = 0.5;
    document.getElementById('greeting-card').style.opacity = 0.5;
    document.getElementById('book-appointment-card').style.opacity = 0.5;
    document.getElementById('communicate-link-card').style.opacity = 0.5;
    document.getElementById('appointment-statistics-card').style.opacity = 0.5;
    document.getElementById('upcoming-appointment-card').style.opacity = 0.5;
    document.getElementById('upcoming-virtual-card').style.opacity = 0.5;
    document.getElementById('members-card').style.opacity = 0.5;
    document.getElementById('account-age-card').style.opacity = 0.5;
}

function closeChat() {
    document.getElementById("chat-form").style.display = "none";
    document.getElementById("open-button").style.display = "block";
    document.getElementById("close-button").style.display = "none";
    document.getElementById('navigation-bar').style.opacity = 1;
    document.getElementById('greeting-card').style.opacity = 1;
    document.getElementById('book-appointment-card').style.opacity = 1;
    document.getElementById('communicate-link-card').style.opacity = 1;
    document.getElementById('appointment-statistics-card').style.opacity = 1;
    document.getElementById('upcoming-appointment-card').style.opacity = 1;
    document.getElementById('upcoming-virtual-card').style.opacity = 1;
    document.getElementById('members-card').style.opacity = 1;
    document.getElementById('account-age-card').style.opacity = 1;
}