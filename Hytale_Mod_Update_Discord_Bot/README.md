# Hytale Mod Update Discord Bot

A Discord bot that checks your Hytale server or singleplayer world mods against CurseForge and notifies a chosen channel about available updates.

## Requirements

- Python 3.8 or above
- Discord bot token (created in the [Discord Developer Portal](https://discord.com/developers/applications))
- CurseForge API key (from the [CurseForge Developer Console](https://console.curseforge.com/))
- Access to your Hytale server or singleplayer mods folder

---

## Instructions

1. Clone or download this repository

       git clone https://github.com/YOUR_USERNAME/hytale-mod-update-bot.git
       cd hytale-mod-update-bot

2. Install Python dependencies

    - You need Python 3.8 or above. Download here: [python.org](https://www.python.org/downloads/)
    - Then run:

          pip install -r requirements.txt

3. Create a Discord bot and get a bot token

    - Go to: [Discord Developer Portal](https://discord.com/developers/applications)
    - Click "New Application", name it
    - Go to "Bot", click "Add Bot"
    - Copy the Token (keep this secret)

    See: [discord.py documentation](https://discordpy.readthedocs.io/en/stable/discord.html)

4. Register for a CurseForge API Key

    - Go to: [CurseForge Developer Console](https://console.curseforge.com/)
    - Log in or sign up
    - Click "Add Application", fill in the info, submit
    - Copy your Client API Key

    See: [CurseForge API documentation](https://docs.curseforge.com/)

5. Configure the bot

    - Copy `.env.example` to `.env`
          cp .env.example .env
    - Fill in your Discord token and CurseForge API key

          DISCORD_TOKEN=your_discord_token_here
          CURSEFORGE_API_KEY=your_curseforge_key_here
          DEFAULT_SERVER_MODS_DIR=/path/to/server/mods
          DEFAULT_SP_MODS_DIR=/path/to/singleplayer/mods

    - Adjust mod directory paths if needed

6. Run the bot

       python bot.py

## Bot Setup in Discord

- Add/invite the bot to your Discord server using the invite link from the Developer Portal.
- The bot will DM the server owner for configuration.
    - It will ask if you want to check a server or singleplayer world (reply `server` or `singleplayer`)
    - It will ask for your mods folder path (paste or reply `default`)
- In the desired Discord channel, run:  
      !setupdatechannel
- To manually check for updates, run:  
      !checkmods
- The bot checks automatically every 60 minutes and posts results in the selected channel.

## Links

- [Discord Developer Portal](https://discord.com/developers/applications)
- [discord.py documentation](https://discordpy.readthedocs.io/en/stable/discord.html)
- [CurseForge Developer Console](https://console.curseforge.com/)
- [CurseForge API documentation](https://docs.curseforge.com/)
- [python.org](https://www.python.org/downloads/)

## Notes

- Never share your .env file or API keys publicly.
- Run the bot on the same machine that can access your mods folder.
- This project is experimental. Hytale is currently in a pre-release state, so modding tools and practices may change as the game develops.
- For support, submit an issue in this repository or contact the maintainer.
