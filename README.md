## Credential Nexus - Password Extraction & Management Tool

### 🛡️ Overview
Credential Nexus is a command-line tool designed to securely extract, decrypt, and manage saved login credentials from various sources, including Google Chrome, Discord, and Firefox. It provides robust decryption capabilities using AES-GCM and Windows DPAPI, offering comprehensive password recovery and storage functionality.

### ✨ Key Features
- **Multi-Source Extraction**: Retrieves passwords from Chrome, Discord, and Firefox.
- **Advanced Decryption**: Employs AES-GCM (v10/v11) and DPAPI for strong password decryption.
- **Secure Storage**: Saves extracted passwords in an encrypted SQLite database (`stored_passwords.db`).
- **Flexible Search**: Allows searching by website, username, or source within stored credentials.
- **User-Friendly Interface**: Provides a command-line menu for easy navigation and operation.
- **Robust Error Handling**: Implements detailed logging and exception handling for reliable performance.

### ⚙️ Technical Architecture
Credential Nexus operates through the following key steps:

1.  **Data Acquisition**: Copies the relevant login data files (e.g., "Login Data" from Chrome).
2.  **Database Connection**: Establishes connections to source databases and the storage database.
3.  **Key Extraction**: Retrieves the encryption key from Chrome's "Local State" file using Windows DPAPI.
4.  **Password Decryption**: Iterates through saved logins, decrypting passwords based on their encryption method.
5.  **Secure Storage**: Stores the decrypted credentials in the SQLite database, avoiding duplicates.
6.  **Search and Retrieval**: Implements search functions to locate specific passwords based on user criteria.

### 🛠️ Installation & Setup
1.  **Clone the Repository**

    ```bash
    git clone https://github.com/Muhammad-Ilyas-Ibrahim/Credential-Nexus.git
    cd Credential-Nexus
    ```
2.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

### 🔑 Preparing Chrome's Login Data

**Before running Credential Nexus, you must copy the "Login Data" file from your Chrome profile directory to the same location as the script.**

1.  **Locate the "Login Data" file:**
    *   **Default Path (Windows):** `C:\Users\[YourUsername]\AppData\Local\Google\Chrome\User Data\Default\Login Data`
    *   Replace `[YourUsername]` with your actual Windows username.

2.  **Copy the File:**
    *   Ensure Chrome is closed to prevent file locking issues.
    *   Copy the `Login Data` file and place it in the same directory as the `extract_Passwords.py` script.

3.  **Multiple Profiles:**
    *   If you use multiple Chrome profiles, the "Login Data" file will be located in a profile-specific directory instead of "Default". For example:
        `C:\Users\[YourUsername]\AppData\Local\Google\Chrome\User Data\Profile 1\Login Data`
        `C:\Users\[YourUsername]\AppData\Local\Google\Chrome\User Data\Profile 2\Login Data`
    *   Copy the `Login Data` from the relevant profile if needed.

4.  **Run the Tool**

    ```bash
    python extract_Passwords.py
    ```

### 📝 Usage Instructions
1.  **Main Menu**
    *   Run the script to access the main menu.
    *   Choose options using the number keys:
        *   `1`: Extract Chrome Passwords
        *   `2`: Search Saved Passwords
        *   `3`: View Database Statistics
        *   `4`: Exit
2.  **Password Extraction**
    *   Select option `1` to begin extracting and decrypting passwords.
    *   The tool will display a summary of successfully added passwords and decryption failures.
3.  **Password Search**
    *   Select option `2` to search the stored passwords.
    *   Choose a search method:
        *   `1`: Search by website/username
        *   `2`: Search by source (Chrome/Discord/Firefox)
        *   `3`: Show all entries
    *   Enter the search term if prompted and view the results.
4.  **Database Statistics**
    *   Select option `3` to view database statistics
    *   Displays total number of stored passwords
    *   Shows breakdown of passwords by source
    *   Indicates the last update timestamp

### 🧩 Code Structure

```
Credential Nexus/
├── extract_Passwords.py   # Main script with extraction and decryption logic
├── stored_passwords.db    # SQLite database for storing decrypted passwords
├── LoginData_Copy         # Temporary copy of Chrome's Login Data
├── requirements.txt       # List of Python dependencies
└── README.md              # Documentation file
```


### ⚠️ Important Considerations
- **Security**: Credential Nexus handles sensitive data. Ensure the script is used in a secure environment.
- **Permissions**: The script requires access to Chrome's "Local State" and "Login Data" files, which may necessitate elevated privileges.
- **Legal Compliance**: Use this tool responsibly and ethically. Avoid unauthorized access to personal data.
- **File Locations**: Ensure the "Login Data" file is correctly copied to the script's directory before extraction.

### 🤝 Contributing
Contributions to Credential Nexus are welcome! Please fork the repository, create a feature branch, and submit a pull request with detailed changes.

### 📄 License

Credential Nexus is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.