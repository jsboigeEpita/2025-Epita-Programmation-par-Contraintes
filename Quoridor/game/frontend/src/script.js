// Creates a new user and initializes the session
async function createUser() {
    const username = document.getElementById("home-username").value;

    const response = await fetch(`${backendURL}/user`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username })
    });

    if (response.ok) {
        const json = await response.json();

        // Clear any existing session and store the new player ID
        sessionStorage.clear();
        sessionStorage.setItem("playerID", json.UUID);

        // Redirect to the games page
        document.location.href = "games";
    } else {
        // Show an error message temporarily if the username is invalid
        const errorElement = document.getElementById("invalid-username");
        errorElement.style.transition = "none";
        errorElement.style.opacity = 1;

        setTimeout(() => {
            errorElement.style.transition = "opacity 1s ease";
            errorElement.style.opacity = 0;
        }, 3000);
    }
}