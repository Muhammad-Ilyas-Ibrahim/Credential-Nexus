import os
import json
import sqlite3
import base64
import win32crypt
from Crypto.Cipher import AES
from shutil import copyfile

# Function to get the encryption key
def get_encryption_key():
    local_state_path = os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\User Data\Local State")
    
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)

    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

    print(f"Extracted Key: {decrypted_key.hex()}")  # Debugging
    return decrypted_key

# Function to decrypt password
def decrypt_password(password, key):
    try:
        # Handle Discord's specific format
        if isinstance(password, bytes) and len(password) > 0:
            # Discord specific pattern check
            if b'dQw4w9WgXcQ:' in password:
                try:
                    encoded = password.decode('utf-8').split('dQw4w9WgXcQ:')[1]
                    decoded = base64.b64decode(encoded.encode())
                    return win32crypt.CryptUnprotectData(decoded, None, None, None, 0)[1].decode()
                except Exception as e:
                    print(f"Debug - Discord decryption failed: {str(e)}")

            # First try the v10/v11 format
            if password[:3] == b'v10' or password[:3] == b'v11':
                try:
                    iv = password[3:15]
                    encrypted_password = password[15:-16]
                    tag = password[-16:]
                    cipher = AES.new(key, AES.MODE_GCM, iv)
                    decrypted_password = cipher.decrypt_and_verify(encrypted_password, tag).decode('utf-8')
                    return decrypted_password
                except Exception as e:
                    print(f"Debug - AES decryption failed: {str(e)}")
            
            # Try direct CryptUnprotectData
            try:
                return win32crypt.CryptUnprotectData(password, None, None, None, 0)[1].decode('utf-8')
            except Exception as e:
                print(f"Debug - CryptUnprotectData failed: {str(e)}")
                
                # Last resort: try decrypting without version prefix
                try:
                    if len(password) > 31:  # Ensure minimum length for this method
                        iv = password[:12]
                        encrypted_password = password[12:-16]
                        tag = password[-16:]
                        cipher = AES.new(key, AES.MODE_GCM, iv)
                        decrypted_password = cipher.decrypt_and_verify(encrypted_password, tag).decode('utf-8')
                        return decrypted_password
                except Exception as e:
                    print(f"Debug - Last resort decryption failed: {str(e)}")
                    
        return "[Password could not be decrypted]"
    except Exception as e:
        return f"[Decryption Failed: {str(e)}]"

def create_storage_db():
    storage_db = sqlite3.connect("stored_passwords.db")
    cursor = storage_db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT,
            username TEXT,
            password TEXT,
            source TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    storage_db.commit()
    return storage_db

def extract_passwords():
    try:
        # Copy the file (so Chrome isn't locked)
        copyfile("Login Data", "LoginData_Copy")
        
        # Connect to databases
        chrome_db = sqlite3.connect("LoginData_Copy")
        chrome_cursor = chrome_db.cursor()
        
        storage_db = create_storage_db()
        storage_cursor = storage_db.cursor()

        # Get encryption key
        key = get_encryption_key()

        # Query all saved logins
        chrome_cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        # Counter for new passwords
        new_passwords = 0
        failed_decryptions = 0

        # Process each password
        for row in chrome_cursor.fetchall():
            site, username, password = row
            
            # Determine source based on URL
            source = "Chrome"
            if "discord" in site.lower():
                source = "Discord"
            elif "mozilla" in site.lower():
                source = "Firefox"
            
            decrypted_password = decrypt_password(password, key)
            
            if decrypted_password == "[Password could not be decrypted]":
                failed_decryptions += 1
                print(f"\nFailed to decrypt password for site: {site}")
                print(f"Username: {username}")
                continue
            
            # Check if this entry already exists
            storage_cursor.execute('''
                SELECT COUNT(*) FROM saved_passwords 
                WHERE site = ? AND username = ? AND password = ?
            ''', (site, username, decrypted_password))
            
            if storage_cursor.fetchone()[0] == 0:
                storage_cursor.execute('''
                    INSERT INTO saved_passwords (site, username, password, source)
                    VALUES (?, ?, ?, ?)
                ''', (site, username, decrypted_password, source))
                new_passwords += 1
                print(f"New password saved for {site} ({source})")

        storage_db.commit()
        print(f"\nExtraction Summary:")
        print(f"- Successfully added: {new_passwords} new passwords")
        print(f"- Failed decryptions: {failed_decryptions}")

        # Clean up
        chrome_cursor.close()
        chrome_db.close()
        storage_cursor.close()
        storage_db.close()
        os.remove("LoginData_Copy")
        
    except Exception as e:
        print(f"Error during extraction: {str(e)}")

def search_passwords():
    try:
        storage_db = sqlite3.connect("stored_passwords.db")
        cursor = storage_db.cursor()
        
        print("\nSearch options:")
        print("1. Search by website/username")
        print("2. Search by source (Chrome/Discord/Firefox)")
        print("3. Show all")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            search_term = input("Enter website or username to search: ").strip()
            cursor.execute('''
                SELECT site, username, password, source FROM saved_passwords
                WHERE site LIKE ? OR username LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%'))
        elif choice == "2":
            source = input("Enter source (Chrome/Discord/Firefox): ").strip()
            cursor.execute('''
                SELECT site, username, password, source FROM saved_passwords
                WHERE source LIKE ?
            ''', (f'%{source}%',))
        else:
            cursor.execute('SELECT site, username, password, source FROM saved_passwords')
        
        results = cursor.fetchall()
        
        if not results:
            print("No matching passwords found.")
        else:
            print(f"\nFound {len(results)} matching entries:")
            print("-" * 60)
            for site, username, password, source in results:
                print(f"Source: {source}")
                print(f"Website: {site}")
                print(f"Username: {username}")
                print(f"Password: {password}")
                print("-" * 60)
        
        cursor.close()
        storage_db.close()
        
    except Exception as e:
        print(f"Error during search: {str(e)}")

def main_menu():
    while True:
        os.system("cls")
        os.system("title Password Manager")
        os.system("color a")
        print("\n=== Password Manager Menu ===")
        print("1. Extract Chrome Passwords")
        print("2. Search Saved Passwords")
        print("3. Exit")
        
        choice = input("\n>> ").strip()
        
        os.system("cls")
        if choice == "1":
            extract_passwords()
        elif choice == "2":
            search_passwords()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        input("\nPress Enter to continue...")
if __name__ == "__main__":
    main_menu()