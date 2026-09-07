/* =========================================================
   IP-SAKTI JAVASCRIPT
========================================================= */


/* =========================================================
   PAGE NAVIGATION
========================================================= */

const navItems = document.querySelectorAll(".nav-item");
const pages = document.querySelectorAll(".page");


navItems.forEach(item => {

    item.addEventListener("click", () => {

        const pageName = item.dataset.page;

        openPage(pageName);

    });

});


function openPage(pageName) {

    pages.forEach(page => {
        page.classList.remove("active-page");
    });

    navItems.forEach(item => {
        item.classList.remove("active");
    });


    const selectedPage = document.getElementById(pageName);

    if (selectedPage) {
        selectedPage.classList.add("active-page");
    }


    const selectedNav = document.querySelector(
        `.nav-item[data-page="${pageName}"]`
    );

    if (selectedNav) {
        selectedNav.classList.add("active");
    }


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


/* =========================================================
   TOAST MESSAGE
========================================================= */

function showToast(message) {

    const toast = document.getElementById("toast");

    toast.textContent = message;

    toast.classList.add("show");

    setTimeout(() => {

        toast.classList.remove("show");

    }, 2500);
}


/* =========================================================
   PRIOR ART SEARCH
========================================================= */

function searchPriorArt() {

    const input = document.getElementById("priorArtInput");

    const results = document.getElementById("searchResults");

    const value = input.value.trim();


    if (value === "") {

        showToast("Please enter an innovation or keyword.");

        input.focus();

        return;
    }


    results.classList.remove("hidden");

    showToast("AI prior-art analysis completed.");

}


/* =========================================================
   AI ASSISTANT
========================================================= */

function addUserMessage(message) {

    const chatArea = document.getElementById("chatArea");


    const messageElement = document.createElement("div");

    messageElement.className = "chat-message user-message";


    messageElement.innerHTML = `

        <div class="message-avatar">
            SR
        </div>

        <div class="message-content">

            <strong>You</strong>

            <p>${escapeHTML(message)}</p>

        </div>

    `;


    chatArea.appendChild(messageElement);


    chatArea.scrollTop = chatArea.scrollHeight;
}


function addAIMessage(message) {

    const chatArea = document.getElementById("chatArea");


    const messageElement = document.createElement("div");

    messageElement.className = "chat-message ai-message";


    messageElement.innerHTML = `

        <div class="message-avatar">
            🤖
        </div>

        <div class="message-content">

            <strong>IP-SAKTI AI</strong>

            <p>${message}</p>

        </div>

    `;


    chatArea.appendChild(messageElement);


    chatArea.scrollTop = chatArea.scrollHeight;
}


function sendAIMessage() {

    const input = document.getElementById("aiInput");

    const message = input.value.trim();


    if (!message) {

        return;

    }


    addUserMessage(message);

    input.value = "";


    setTimeout(() => {

        generateAIResponse(message);

    }, 600);

}


function askAI(question) {

    const input = document.getElementById("aiInput");

    input.value = question;

    sendAIMessage();

}


function generateAIResponse(question) {

    const lower = question.toLowerCase();


    if (
        lower.includes("prior art") ||
        lower.includes("patent")
    ) {

        addAIMessage(
            "I can help identify potential prior-art areas. " +
            "For a real assessment, provide your innovation's " +
            "technical features, intended use and distinguishing characteristics."
        );

        return;
    }


    if (
        lower.includes("biodiversity") ||
        lower.includes("traditional knowledge") ||
        lower.includes("tk")
    ) {

        addAIMessage(
            "For TK and biodiversity-related innovation, first establish " +
            "the source and provenance of the knowledge or biological resource, " +
            "then review applicable access, benefit-sharing and IP requirements."
        );

        return;
    }


    if (
        lower.includes("risk") ||
        lower.includes("risk assessment")
    ) {

        addAIMessage(
            "The preliminary risk framework considers prior-art similarity, " +
            "TK provenance, regulatory compliance and evidence strength. " +
            "A high-risk item should be reviewed by an appropriate expert."
        );

        return;
    }


    if (
        lower.includes("innovation") ||
        lower.includes("idea")
    ) {

        addAIMessage(
            "To evaluate an innovation, document its problem statement, " +
            "technical solution, novelty, supporting evidence and potential " +
            "IP protection strategy."
        );

        return;
    }


    addAIMessage(
        "I can help with innovation analysis, IP and prior art, " +
        "TK & biodiversity, regulatory considerations, risk assessment " +
        "and evidence management. What would you like to analyze?"
    );

}


/* =========================================================
   ENTER KEY FOR AI CHAT
========================================================= */

document
    .getElementById("aiInput")
    .addEventListener("keydown", function(event) {

        if (event.key === "Enter") {

            sendAIMessage();

        }

    });


/* =========================================================
   REPORT GENERATION
========================================================= */

function generateReport() {

    showToast("Report generation started...");

    setTimeout(() => {

        showToast("Report generated successfully!");

    }, 1500);

}


/* =========================================================
   DARK MODE
========================================================= */

const darkModeToggle = document.getElementById("darkMode");


darkModeToggle.addEventListener("change", () => {

    if (darkModeToggle.checked) {

        document.body.classList.add("dark");

        localStorage.setItem("ipSaktiDarkMode", "true");

    } else {

        document.body.classList.remove("dark");

        localStorage.setItem("ipSaktiDarkMode", "false");

    }

});


if (localStorage.getItem("ipSaktiDarkMode") === "true") {

    document.body.classList.add("dark");

    darkModeToggle.checked = true;

}


/* =========================================================
   GLOBAL SEARCH
========================================================= */

const globalSearch = document.getElementById("globalSearch");


globalSearch.addEventListener("keydown", function(event) {

    if (event.key !== "Enter") {

        return;

    }


    const searchValue = globalSearch.value.trim().toLowerCase();


    if (!searchValue) {

        return;

    }


    if (
        searchValue.includes("innovation") ||
        searchValue.includes("idea")
    ) {

        openPage("innovation");

    }

    else if (
        searchValue.includes("prior") ||
        searchValue.includes("patent") ||
        searchValue.includes("ip")
    ) {

        openPage("prior-art");

    }

    else if (
        searchValue.includes("biodiversity") ||
        searchValue.includes("traditional") ||
        searchValue.includes("tk")
    ) {

        openPage("tk-biodiversity");

    }

    else if (
        searchValue.includes("regulation") ||
        searchValue.includes("compliance")
    ) {

        openPage("regulatory");

    }

    else if (
        searchValue.includes("risk") ||
        searchValue.includes("evidence")
    ) {

        openPage("risk");

    }

    else if (
        searchValue.includes("report")
    ) {

        openPage("reports");

    }

    else if (
        searchValue.includes("setting")
    ) {

        openPage("settings");

    }

    else {

        showToast("No matching module found.");

    }

});


/* =========================================================
   SECURITY
========================================================= */

function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


/* =========================================================
   INITIALIZATION & BACKEND API
========================================================= */

// Local backend for development. For deployment, change this to the deployed FastAPI backend URL.
const API_BASE_URL = "http://127.0.0.1:8000";

console.log("IP-SAKTI Dashboard loaded successfully.");

async function callBackend(question) {
    const response = await fetch(`${API_BASE_URL}/api/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, jurisdiction: "India", language: "English" })
    });
    if (!response.ok) throw new Error(`Backend request failed: ${response.status}`);
    return await response.json();
}

function formatAIResponse(data) {
    let html = escapeHTML(data.answer || "No answer received from the AI engine.");
    if (data.disclaimer) html += `<br><br><small><strong>Disclaimer:</strong> ${escapeHTML(data.disclaimer)}</small>`;
    if (Array.isArray(data.citations) && data.citations.length) {
        html += "<br><br><strong>Sources:</strong><ul>";
        data.citations.forEach(c => {
            const title = escapeHTML(c.title || c.reference || "Source");
            const url = c.url ? escapeHTML(c.url) : "";
            html += url ? `<li><a href="${url}" target="_blank" rel="noopener noreferrer">${title}</a></li>` : `<li>${title}</li>`;
        });
        html += "</ul>";
    }
    return html;
}

function setChatLoading(isLoading) {
    const input = document.getElementById("aiInput");
    const button = document.querySelector('.chat-input button');
    if (input) input.disabled = isLoading;
    if (button) button.disabled = isLoading;
}

/* =========================================================
   AI ASSISTANT - REAL BACKEND
========================================================= */

async function sendAIMessage() {
    const input = document.getElementById("aiInput");
    const message = input.value.trim();
    if (!message) return;
    addUserMessage(message);
    input.value = "";
    setChatLoading(true);
    try {
        const data = await callBackend(message);
        addAIMessage(formatAIResponse(data));
    } catch (error) {
        console.error("AI Assistant error:", error);
        addAIMessage("Sorry, I couldn't connect to the IP-SAKTI backend. Please make sure the FastAPI backend is running on port 8000.");
    } finally {
        setChatLoading(false);
        input.focus();
    }
}

function askAI(question) {
    const input = document.getElementById("aiInput");
    input.value = question;
    sendAIMessage();
}

/* =========================================================
   PRIOR ART SEARCH - USE SAME AI BACKEND
========================================================= */

async function searchPriorArt() {
    const input = document.getElementById("priorArtInput");
    const results = document.getElementById("searchResults");
    const value = input.value.trim();
    if (!value) { showToast("Please enter an innovation or keyword."); input.focus(); return; }
    showToast("Searching with IP-SAKTI AI...");
    try {
        const data = await callBackend(`Find and analyze possible prior art for this innovation: ${value}`);
        results.classList.remove("hidden");
        results.innerHTML = `<div class="panel-header"><div><h3>AI Prior-Art Analysis</h3><p>Analysis returned by IP-SAKTI AI</p></div></div><div class="result-card"><div class="result-score">AI</div><div><h3>Analysis</h3><div>${formatAIResponse(data)}</div></div></div>`;
        showToast("Prior Art analysis complete!");
    } catch (error) {
        console.error("Prior Art error:", error);
        showToast("Could not connect to the backend.");
    }
}
