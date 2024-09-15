# Telegram Anonymous ChatBot

Welcome to this example of ChatBot, a Telegram bot that connects users for random anonymous chats!

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [How It Works](#how-it-works)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [List of Commands](#list-of-commands)
- [Contributing](#contributing)

## Introduction

This is an example of a Telegram bot that allows users to connect with random partners for chats while ensuring anonymity between users. 
This project was born out of my curiosity to understand how a generic ChatBot works on Telegram. As a result, I created this bot from scratch! 
All of this is made possible thanks to this interface for the Telegram Bot API  [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

## Features
- **NEW**! Scalable approach with sqlite3 database to handle users pairs and chat statistics (Improvements are always possible!).
- Randomly pairs users for one-on-one chats.
- Ensures anonymity between users.
- Offers an easy-to-use Telegram interface.
- Gracefully handles partner exits and chat interruptions.
- New feature implementations are possible, such as adding states for settings, blocked users, special commands for admins, and more.

## How It Works

### Prerequisites

- Python (3.8 or higher)
- Telegram Bot API token (obtain it from @BotFather on Telegram, see [here](https://core.telegram.org/bots/tutorial#obtain-your-bot-token))
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library installed (see [here](https://github.com/python-telegram-bot/python-telegram-bot#installing))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Alb-24/TelegramChatBot

2. Create a file config.py with your own user_id as ADMIN_ID and Telegram Bot API Token as BOT_TOKEN.
    ```python
    # config.py
    
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    ADMIN_ID = "YOUR_ADMIN_USER_ID"
    
3. Make any modifications you desire to bot.py and UserStatus.py. 
   For example, you can change the welcome message, add new commands or User status. 
4. Run bot.py and have fun with your bot:
   ```bash
   python bot.py

### List of Commands

These are the supported commands, for now:

    /start - 🤖 Starts the bot
    /chat -  💬 Start searching for a partner
    /exit - 🔚 Exit from the chat
    /newchat - ⏭ Exit from the chat and open a new one
    /stats - 📊 Show bot statistics (only for admin)

### Contributing

**Contributions** are **highly welcome**! I'm new to the world of Telegram bots, so I've likely only scratched the surface of all possibilities. 
There could be countless functionalities unknown to me, but this is just a starting point.

If you have any **suggestions**, bug reports, or feature requests, please open an **issue** or a **discussion** and share your thoughts! 
Anything is appreciated 😄.


Feel free to use or modify this version as needed!


