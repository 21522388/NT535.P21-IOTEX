import serial
import json
from web3 import Web3
from eth_account import Account
from time import sleep

# Config
SERIAL_PORT = 'COM5'
BAUD_RATE = 115200
IOTEX_RPC_URL = "https://babel-api.testnet.iotex.io"
SENDING_ENABLED = True

WALLET_ADDRESS = ""
PRIVATE_KEY = ""

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(IOTEX_RPC_URL))
if not w3.is_connected():
    raise ConnectionError("❌ Failed to connect to IoTeX")

# Create account from private key
account = Account.from_key(PRIVATE_KEY)

print(f"=== IoTeX Edge Layer ===")
print(f"📶 Network: {IOTEX_RPC_URL}")
print(f"👛 Account: {account.address}")
print(f"🔗 Blockchain Sending: {'ENABLED' if SENDING_ENABLED else 'DISABLED'}\n")

# Send to IoTeX Blockchain
def send_to_iotex(data):
    if not SENDING_ENABLED:
        print("⚠️ [Dry Run] Blockchain submission disabled")
        return None

    try:
        # Prepare transaction
        nonce = w3.eth.get_transaction_count(account.address)
        tx = {
            'to': WALLET_ADDRESS,
            'value': 0,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
            'chainId': 4690,  # IoTeX testnet ChainID
            'data': w3.to_hex(text=json.dumps(data))
        }

        # Sign and send transaction
        signed_tx = Account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return tx_hash.hex()

    except ValueError as ve:
        print(f"❌ Validation failed: {str(ve)}")
    except Exception as e:
        print(f"❌ Submission error: {type(e).__name__}: {str(e)}")
    return None

# Read from Serial
def read_serial_data():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"📡 Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
        print("🔄 Waiting for data... (Ctrl+C to stop)\n")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()

                try:
                    if line.startswith('{') and line.endswith('}'):
                        data = json.loads(line)
                        print("\n📦 Received Data:")
                        print(json.dumps(data, indent=2))

                        tx_hash = send_to_iotex(data)
                        if tx_hash:
                            print(f"✅ Success! TX Hash: {tx_hash}")
                            print(f"🔗 Explorer: https://iotexscan.io/tx/{tx_hash}")

                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON: {line[:50]}...")
                except Exception as e:
                    print(f"⚠️ Processing error: {type(e).__name__}: {str(e)}")

            sleep(0.1)

    except serial.SerialException as e:
        print(f"❌ Serial error: {str(e)}")
    except KeyboardInterrupt:
        print("\n🛑 Script stopped by user")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("🔌 Serial port closed")

# Main
if __name__ == "__main__":
    read_serial_data()
