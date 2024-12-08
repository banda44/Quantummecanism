import hashlib
import random
import json
import time
import requests
from datetime import datetime
from ecdsa import SECP256k1, SigningKey

# File to store miners' data
MINERS_FILE = "miners.json"

# Load miners data from the JSON file
def load_miners():
    try:
        with open(MINERS_FILE, 'r') as file:
            miners_data = json.load(file)
            # Ensure each miner has balance and transactions fields
            for miner_id, data in miners_data.items():
                if "balance" not in data:
                    data["balance"] = 0.0  # Default balance if missing
                if "transactions" not in data:
                    data["transactions"] = []  # Initialize empty list
            return miners_data
    except FileNotFoundError:
        return {}  # Return an empty dictionary if the file doesn't exist

# Save miners data to the JSON file
def save_miners(miners):
    with open(MINERS_FILE, 'w') as file:
        json.dump(miners, file, indent=4)

# Initialize miners and balances from the file
miners = load_miners()

# Function to generate a random private key (in hex)
def generate_private_key():
    return ''.join(random.choices('0123456789abcdef', k=64))  # 256-bit private key

# Function to generate a public key from the private key
def generate_public_key(private_key_hex):
    private_key_bytes = bytes.fromhex(private_key_hex)
    private_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    public_key = private_key.get_verifying_key()
    return public_key.to_string().hex()

# Function to generate a checksum from the public key
def generate_checksum(public_key_hex):
    return hashlib.sha256(bytes.fromhex(public_key_hex)).hexdigest()[:8]  # Short checksum for Quantumgrafic ID

# Function to register a new miner and generate Quantumgrafic ID
def register_miner():
    private_key_hex = generate_private_key()
    public_key_hex = generate_public_key(private_key_hex)
    quantumgrafic_id = generate_checksum(public_key_hex)

    # Prevent duplicate registration
    if quantumgrafic_id in miners:
        print("Quantumgrafic ID already exists. Registration failed.")
        return None

    miner_data = {
        "Quantumgrafic ID": quantumgrafic_id,
        "Private Key (Hex)": private_key_hex,
        "Public Key (Hex)": public_key_hex,
        "balance": 0.0,  # Initialize balance to 0.0
        "transactions": []
    }

    miners[quantumgrafic_id] = miner_data
    save_miners(miners)

    print(f"Registration successful!")
    print(f"Quantumgrafic ID: {quantumgrafic_id}")
    print(f"Private Key (Hex): {private_key_hex}")
    print(f"Public Key (Hex): {public_key_hex}")

    return miner_data

# Function to log in a miner
def login_miner():
    quantumgrafic_id = input("Enter your Quantumgrafic ID: ")
    if quantumgrafic_id in miners:
        print(f"Welcome back, {quantumgrafic_id}!")
    else:
        print("Quantumgrafic ID not found. Please register first.")

# Function to confirm if the Quantumgrafic ID matches the private key
def confirm_quantumgrafic_id():
    quantumgrafic_id = input("Enter your Quantumgrafic ID: ")
    private_key_hex = input("Enter your private key (Hex): ")

    # Generate public key from the private key
    public_key_hex = generate_public_key(private_key_hex)

    # Generate the checksum from the public key
    expected_quantumgrafic_id = generate_checksum(public_key_hex)

    if expected_quantumgrafic_id == quantumgrafic_id:
        print("Quantumgrafic ID and Private Key match successfully!")
    else:
        print("Quantumgrafic ID and Private Key do not match!")

# Function to make a transaction
def make_transaction():
    sender_quantumgrafic_id = input("Enter your Quantumgrafic ID: ")
    sender_private_key = input("Enter your private key (Hex): ")

    if sender_quantumgrafic_id not in miners:
        print("Sender Quantumgrafic ID not found. Please register first.")
        return

    sender = miners[sender_quantumgrafic_id]

    # Verify private key
    expected_public_key = generate_public_key(sender_private_key)
    if expected_public_key != sender['Public Key (Hex)']:
        print("Private key does not match the Quantumgrafic ID!")
        return

    receiver_quantumgrafic_id = input("Enter receiver's Quantumgrafic ID: ")
    amount = float(input("Enter amount of Quantum Units to send: "))

    if receiver_quantumgrafic_id not in miners:
        print("Receiver Quantumgrafic ID not found. Please check the ID.")
        return

    if sender['balance'] < amount:
        print("Insufficient balance! Transaction failed.")
        return

    # Deduct from sender and add to receiver
    miners[sender_quantumgrafic_id]['balance'] -= amount
    miners[receiver_quantumgrafic_id]['balance'] += amount

    # Record the transaction
    transaction = {
        "timestamp": datetime.now().isoformat(),
        "from": sender_quantumgrafic_id,
        "to": receiver_quantumgrafic_id,
        "amount": amount
    }

    miners[sender_quantumgrafic_id]['transactions'].append(transaction)
    miners[receiver_quantumgrafic_id]['transactions'].append(transaction)

    save_miners(miners)

    print(f"Transaction successful! Sent {amount} Quantum Units from {sender_quantumgrafic_id} to {receiver_quantumgrafic_id}.")

# Function to check balance
def check_balance():
    quantumgrafic_id = input("Enter your Quantumgrafic ID to check balance: ")
    if quantumgrafic_id in miners:
        balance = miners[quantumgrafic_id]['balance']
        print(f"Balance for Quantumgrafic ID {quantumgrafic_id}: {balance} Quantum Units")
    else:
        print("Quantumgrafic ID not found. Please register first.")

# Function to confirm transactions (view transaction history)
def confirm_transactions():
    quantumgrafic_id = input("Enter your Quantumgrafic ID to view transactions: ")
    if quantumgrafic_id not in miners:
        print("Quantumgrafic ID not found. Please register first.")
        return

    miner = miners[quantumgrafic_id]
    transactions = miner.get('transactions', [])

    if not transactions:
        print("No transactions found for your account.")
    else:
        print(f"\nTransactions for Quantumgrafic ID {quantumgrafic_id}:")
        for tx in transactions:
            print(f"Timestamp: {tx['timestamp']}, From: {tx['from']}, To: {tx['to']}, Amount: {tx['amount']} Quantum Units")

# Function to continue mining (rewards given every 10 minutes)
def continue_mining():
    quantumgrafic_id = input("Enter your Quantumgrafic ID to start mining: ")

    if quantumgrafic_id not in miners:
        print("Quantumgrafic ID not found. Please register first.")
        return

    print(f"Mining started for {quantumgrafic_id}. Rewards will be earned every 10 minutes.")

    # Use hardcoded location for weather data
    latitude, longitude = 41.9028, 12.4964  # Example: Rome, Italy
    api_key = "8b18090bcf960d2a288dcaa1a1963af1"  # Your OpenWeatherMap API key

    while True:
        try:
            time.sleep(600)  # Wait for 10 minutes

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
            response = requests.get(weather_url)
            data = response.json()

            # Check if response is valid
            if response.status_code != 200 or 'main' not in data:
                print("Error fetching weather data.")
                continue

            temperature = data['main'].get('temp')
            conditions = data['weather'][0].get('main', '')
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            reward = 0.0  # Default reward

            # Check for solar energy or electromagnetic waves
            if conditions == 'Clear':
                reward = 0.05  # Bonus reward
                energy_type = 'Solar Energy Detected'
            elif conditions in ['Thunderstorm', 'Drizzle']:
                reward = 0.05  # Bonus reward
                energy_type = 'Electromagnetic Waves Detected'
            elif temperature < 0 or temperature > 30:
                reward = 0.0005  # Hot or cold reward
                energy_type = 'Extreme Temperature Detected'
            else:
                reward = 0.0
                energy_type = 'No Bonus Energy Detected'

            # Add reward to miner's balance
            miners[quantumgrafic_id]['balance'] += reward
            save_miners(miners)

            print(f"\nTime: {current_time}")
            print(f"Temperature: {temperature}°C")
            print(f"Weather Condition: {conditions}")
            print(f"Energy Status: {energy_type}")
            print(f"Reward Earned: {reward} Qubits")
            print(f"Total Balance: {miners[quantumgrafic_id]['balance']} Qubits")

        except Exception as e:
            print(f"Error during mining: {e}")
            break

# Main menu
def main():
    while True:
        print("\n1. Log in to your Quantumgrafic ID")
        print("2. New Registration")
        print("3. Confirm if your Quantumgrafic ID matches your private key")
        print("4. Exit")
        print("5. Make Transaction")
        print("6. Check Balance")
        print("7. Confirm Transaction")
        print("8. Continue Mining")

        option = input("Choose an option: ")

        if option == "1":
            login_miner()
        elif option == "2":
            miner = register_miner()
            if miner:
                print(f"Miner with Quantumgrafic ID {miner['Quantumgrafic ID']} successfully registered.")
        elif option == "3":
            confirm_quantumgrafic_id()
        elif option == "4":
            print("Exiting...")
            break
        elif option == "5":
            make_transaction()
        elif option == "6":
            check_balance()
        elif option == "7":
            confirm_transactions()
        elif option == "8":
            continue_mining()
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()

