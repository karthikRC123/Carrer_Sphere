// Add this to your existing script.js file

document.getElementById("login-form").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevents the form from submitting normally
    
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    
    // Example validation
    if (username === "" || password === "") {
        alert("Please fill out all fields.");
        return;
    }
    
    // For demonstration, we'll log the credentials
    console.log("Username:", username);
    console.log("Password:", password);
    
    // Simulate successful login
    alert("Login successful!");
});
