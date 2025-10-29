# 🌟 Discord Bot — Modular, Scalable, and PostgreSQL Powered

A modular and extensible Discord bot built with **discord.py**, designed for scalability, performance, and maintainability.
This bot leverages **asynchronous PostgreSQL (asyncpg)**, a **cog-based architecture**, and an optional **Flask keep-alive server** for cloud or Repl.it deployment.

---

## 🧰 Features

✅ Modular **Cog System** — each feature is isolated for easy maintenance.

✅ Built-in **database handler** for PostgreSQL (asyncpg).

✅ **Automatic cog loader** on startup.

✅ **Reload** and **hot-update** commands for developers.

✅ Supports **development** and **production** modes.

✅ **Web keep-alive server** for Repl.it or UptimeRobot.

✅ Fully configurable through `.env` environment variables.

---

## 📦 Prerequisites

Before installation, make sure you have the following tools installed:

- **Python 3.13**
- **Git** (for cloning repositories)
- **PostgreSQL** database server
- A **Discord Bot Token** from the [Discord Developer Portal](https://discord.com/developers/applications)

---

## ⚙️ Installation Guide

### Clone the repository

```bash
git clone https://github.com/InitialShip/ZamnBot.git
cd ZamnBot
```

### Install dependencies

Install all required Python packages from the provided requirements.txt file:

```bash
pip install -r requirements.txt
```

### Environment Configuration

Copy **.env** file

#### Windows

```bash
copy .env.example .env
```

#### Linux / macOS

```bash
cp .env.example .env
```

### Edit the **.env** file

| Variable         | Description                                               |
| ---------------- | --------------------------------------------------------- |
| `DISCORD_TOKEN`  | Your Discord bot token obtained from the Developer Portal |
| `DATABASE_URL`   | PostgreSQL connection string                              |
| `COMMAND_PREFIX` | The bot’s prefix (default: `t!`)                          |
| `IS_DEVELOPMENT` | Enables debug logging if set to `true`                    |

## Run the bot

```bash
python main.py
```
