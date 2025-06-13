<?php
// Hardcoded username and password
$correct_username = "admin";
$correct_password = "1234";

// Read input from command line (only works if running PHP CLI)
echo "Enter your username: ";
$username = trim(fgets(STDIN));

echo "Enter your password: ";
$password = trim(fgets(STDIN));

// Check credentials
if ($username === $correct_username && $password === $correct_password) {
    echo "Login successful!\n";
} else {
    echo "Invalid username or password.\n";
}
?>
