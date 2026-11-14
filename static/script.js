const form = document.getElementById("reminderForm");

form.addEventListener("submit", async function(event) {

    event.preventDefault();

    const data = {
        email: document.getElementById("email").value,
        message: document.getElementById("message").value,
        date: document.getElementById("date").value,
        time: document.getElementById("time").value
    };

    try {
        const response = await fetch("/schedule", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        alert(result.message);

    } catch (error) {
        alert("Server connection failed!");
    }
});
