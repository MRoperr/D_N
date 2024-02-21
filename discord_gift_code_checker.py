import requests
import random
import string
import time
from tqdm import tqdm
import threading
import pickle

# Discord webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1209941036256985118/AvKyTOZlqdUvhi3WQfdqXjBy3S-UMbYahEOxlbwn3IawgDxs9yyENAMi5zGYCVwOVaQT"

# Event to signal pause/resume
pause_event = threading.Event()

# File to store progress
PROGRESS_FILE = "progress.pkl"

def generate_random_string(length):
    """Generate a random alphanumeric string of given length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def send_to_discord_webhook(message):
    """Send message to Discord webhook."""
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print("Failed to send message to Discord webhook")

def check_gift_code(code):
    """Check gift code validity."""
    url = f"https://discordapp.com/api/v9/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            send_to_discord_webhook(code)
            return True  # Return True if a valid code is found
    except Exception as e:
        print(f"An error occurred: {e}")
    return False  # Return False if no valid code is found

def hourglass():
    while True:
        for frame in ['⏳', '⌛']:
            print(f'\rChecking gift codes {frame}', end='', flush=True)
            time.sleep(0.5)

def pause_resume():
    paused = False
    while True:
        try:
            input("Press Enter to pause/resume...")
            if paused:
                send_to_discord_webhook("Program paused")
                pause_event.clear()
                paused = False
            else:
                send_to_discord_webhook("Program resumed")
                pause_event.set()
                paused = True
        except EOFError:
            # Continue execution without pausing or resuming the program
            pass

def save_progress(progress):
    """Save progress to a file."""
    with open(PROGRESS_FILE, 'wb') as file:
        pickle.dump(progress, file)

def load_progress():
    """Load progress from a file."""
    try:
        with open(PROGRESS_FILE, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return 0

if __name__ == "__main__":
    # Send program running message
    send_to_discord_webhook("Program running")
    
    try:
        # Load progress from file
        current_progress = load_progress()

        # Start the hourglass animation and pause/resume functionality in separate threads
        threading.Thread(target=hourglass, daemon=True).start()
        threading.Thread(target=pause_resume, daemon=True).start()

        num_iterations = 9999999999  # Number of iterations for the progress bar
        with tqdm(total=num_iterations, desc="Checking gift codes", initial=current_progress) as pbar:
            for i in range(current_progress, num_iterations):
                # Check if pause event is set, if set, wait until cleared
                pause_event.wait()
                random_string = generate_random_string(18)
                if check_gift_code(random_string):
                    print("\nValid gift code found. Exiting...")
                    break  # Exit the loop if a valid code is found
                pbar.update(1)
                time.sleep(0.1)  # Add a small delay for smoother progress bar
                save_progress(i+1)  # Save progress to file
    
    finally:
        # Send program ended message
        send_to_discord_webhook("Program ended")
