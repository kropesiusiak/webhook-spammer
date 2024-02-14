# https://github.com/kropesiusiak/webhook-spammer

import aiohttp
import asyncio
import random
import string
from colorama import Fore, Style, init
init()

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def send_message(webhook_url, content, ping_everyone):
    random_string = generate_random_string()
    if ping_everyone.lower() == 'y':
        content += " @everyone"
    data = {
        "content": f"{content} - {random_string}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=data) as response:
            if response.status == 204:
                print(Fore.LIGHTGREEN_EX + f"[+]{Style.RESET_ALL} Message sent successfully to {webhook_url}")
            elif response.status == 429:
                rate_limit_sleep = float(input("Enter sleep duration after rate limit (in seconds): "))
                print(Fore.LIGHTRED_EX + f"[-]{Style.RESET_ALL} Rate limited for {webhook_url}. Sleeping for {rate_limit_sleep} seconds.")
                await asyncio.sleep(rate_limit_sleep)
                await send_message(webhook_url, content, ping_everyone)  # Retry the same message
            else:
                print(Fore.LIGHTRED_EX + f"[-]{Style.RESET_ALL} Failed to send message to {webhook_url}. Status code: {response.status}")
                try:
                    error_json = await response.json()
                    print(Fore.LIGHTRED_EX + f"[-]{Style.RESET_ALL} Error JSON: {error_json}")
                except aiohttp.ContentTypeError:
                    print(Fore.LIGHTRED_EX + f"[-]{Style.RESET_ALL} Error: Unable to parse error JSON")

async def send_messages_from_webhooks(webhooks, num_requests, ping_everyone, request_sleep):
    for i in range(1, num_requests + 1):
        random.shuffle(webhooks)
        for webhook in webhooks:
            webhook_url = webhook["url"]
            message_content = webhook["content"]
            await send_message(webhook_url, message_content, ping_everyone)
            await asyncio.sleep(request_sleep)  # Wait between requests

async def main():
    try:
        num_webhooks = int(input(Fore.LIGHTYELLOW_EX + f"[?]{Style.RESET_ALL} Enter the number of webhooks to use: "))
    except ValueError:
        print(Fore.LIGHTRED_EX + f"[-]{Style.RESET_ALL} Invalid input. Please enter a valid number.")
        return

    webhooks = []
    for i in range(1, num_webhooks + 1):
        webhook_url = input(Fore.LIGHTYELLOW_EX + f"[?]{Style.RESET_ALL} Enter the webhook URL for webhook {i}: ").strip()
        message_content = input(Fore.LIGHTYELLOW_EX + f"[?]{Style.RESET_ALL} Enter the message content for webhook {i}: ")

        try:
            num_requests = int(input(Fore.LIGHTYELLOW_EX + f"[?]{Style.RESET_ALL} Enter the number of requests to send for webhook {i}: "))
        except ValueError:
            print(Fore.LIGHTRED_EX + f"[-]{Style.RESET_ALL} Invalid input for webhook {i}. Skipping.")
            continue

        webhooks.append({"url": webhook_url, "content": message_content})

    ping_everyone = input(Fore.LIGHTYELLOW_EX + f"[?]{Style.RESET_ALL} Do you want to ping everyone? (y/n): ")
    request_sleep = float(input(Fore.LIGHTYELLOW_EX + f"[?]{Style.RESET_ALL} Enter sleep duration between every request (in seconds): "))
    rate_limit_sleep = float(input(Fore.LIGHTYELLOW_EX + f"[?]{Style.RESET_ALL} Enter sleep duration after rate limit (in seconds): "))

    await send_messages_from_webhooks(webhooks, num_requests, ping_everyone, request_sleep)

if __name__ == "__main__":
    asyncio.run(main())
