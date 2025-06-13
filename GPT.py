# Hardcoded username and password
correct_username = "admin"
correct_password = "1234"

# Ask user for input
username = input("Enter your username: ")
password = input("Enter your password: ")

# Check credentials
if username == correct_username and password == correct_password:
    print("Login successful!")
else:
    print("Invalid username or password.")
