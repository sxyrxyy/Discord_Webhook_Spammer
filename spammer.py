import requests
import time
import random
import os
from concurrent.futures import ThreadPoolExecutor

def send_messages_to_webhook(webhook_url, bot_username, content, times, file_name):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "username": bot_username,
        "content": content
    }

    rate_limit_count = 0  # Track the number of consecutive 429 responses

    for i in range(times):
        response = requests.post(webhook_url, json=data, headers=headers)
        
        if response.status_code == 204:
            print(f"[+] {response.status_code} Message {i+1}: Sent successfully to {webhook_url}.")
            rate_limit_count = 0  # Reset rate limit count on successful request
        elif response.status_code == 404:
            print(f"[-] {response.status_code} Webhook {webhook_url} not found. Removing from list.")
            remove_webhook_from_file(webhook_url, file_name)
            break  # Stop sending further requests to this webhook
        elif response.status_code == 429:
            rate_limit_count += 1
            print(f"[-] {response.status_code} Rate limited on {webhook_url}. Count: {rate_limit_count}")
            if rate_limit_count > 50:
                print(f"[-] Webhook {webhook_url} hit rate limit 50 times. Removing from list.")
                remove_webhook_from_file(webhook_url, file_name)
                break  # Stop sending further requests to this webhook
        else:
            print(f"[-] {response.status_code} Message {i+1}: Failed to send to {webhook_url}.")
        delay = random.uniform(1, 3)
        time.sleep(delay)

def remove_webhook_from_file(webhook_url, file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            webhooks = f.readlines()
        with open(file_name, 'w') as f:
            for line in webhooks:
                if line.strip() != webhook_url:
                    f.write(line)

def get_webhook_urls(file_name='webhooks.txt'):
    webhook_urls = set()
    if os.path.exists(file_name):
        load_existing = input("Do you want to load existing webhooks from file? (yes/no): ").strip().lower()
        if load_existing == "yes":
            with open(file_name, 'r') as f:
                webhook_urls.update([line.strip() for line in f])
            print(f"Loaded {len(webhook_urls)} webhooks from {file_name}.")
            add_more = input("Do you want to add another webhook? (yes/no): ").strip().lower()
            if add_more == "yes":
                webhook_urls.add(input("Enter another Discord webhook URL: "))
        elif load_existing == "no":
            webhook_urls.add(input("Enter your Discord webhook URL: "))
        else:
            print("Invalid response. Please enter 'yes' or 'no'.")
            return get_webhook_urls(file_name)  # Restart the process in case of invalid input
    else:
        webhook_urls.add(input("Enter your Discord webhook URL: "))
    with open(file_name, 'w') as f:
        for url in sorted(webhook_urls):
            f.write(url + '\n')

    return list(webhook_urls)

def send_discord_messages_async(webhook_urls, bot_username, content, times, file_name='webhooks.txt'):
    with ThreadPoolExecutor() as executor:
        for webhook_url in webhook_urls:
            executor.submit(send_messages_to_webhook, webhook_url, bot_username, content, times, file_name)

webhook_urls = get_webhook_urls()
bot_username = "Bot"
content = "Hello"
times = 1000000000000

send_discord_messages_async(webhook_urls, bot_username, content, times)
