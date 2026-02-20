import os
import re
import requests
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CURSEFORGE_API_KEY = os.getenv('CURSEFORGE_API_KEY')
DEFAULT_SERVER_MODS_DIR = os.getenv('DEFAULT_SERVER_MODS_DIR', '../mods')
DEFAULT_SP_MODS_DIR = os.getenv('DEFAULT_SP_MODS_DIR', '../singleplayer/world_name/mods')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
server_settings = {}

def extract_mod_info(filename):
    match = re.match(r"(.+)-([\d\.]+)\.hymod$", filename)
    if not match:
        return None
    return {'name': match.group(1), 'version': match.group(2)}

def get_curseforge_mod_info(mod_name):
    url = 'https://api.curseforge.com/v1/mods/search'
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    params = {"gameId": 5316, "searchFilter": mod_name}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        mods = r.json().get('data', [])
        for m in mods:
            if m['name'].lower() == mod_name.lower():
                return m
    return None

def get_latest_curseforge_version(mod_id):
    url = f'https://api.curseforge.com/v1/mods/{mod_id}/files'
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        files = r.json().get('data', [])
        if files:
            return files[0]['displayName']
    return None

async def do_checkmods(guild_id, channel_id, mods_dir):
    channel = bot.get_channel(channel_id)
    if not channel:
        return
    if not os.path.isdir(mods_dir):
        await channel.send(f"The directory `{mods_dir}` does not exist or cannot be read. Update it with `!setmoddir /path/to/mods`.")
        return
    updates = []
    for fname in os.listdir(mods_dir):
        info = extract_mod_info(fname)
        if info:
            mod_info = get_curseforge_mod_info(info['name'])
            if mod_info:
                latest_version = get_latest_curseforge_version(mod_info['id'])
                if latest_version and latest_version not in fname:
                    updates.append(f"{info['name']}: Installed `{info['version']}` → Latest CurseForge: `{latest_version}`")
            else:
                updates.append(f"{info['name']} not found on CurseForge.")
        else:
            updates.append(f"Unrecognized file: `{fname}`")
    if not updates:
        await channel.send("All mods are up-to-date.")
    else:
        await channel.send("Mod Update Report:\n" + "\n".join(updates))

@tasks.loop(minutes=60)
async def scheduled_mod_check():
    for guild_id, info in server_settings.items():
        channel_id = info.get('channel_id')
        mods_dir = info.get('mods_dir')
        if channel_id and mods_dir:
            await do_checkmods(guild_id, channel_id, mods_dir)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    scheduled_mod_check.start()

@bot.event
async def on_guild_join(guild):
    owner = guild.owner
    if owner is not None:
        try:
            await owner.send(f"Thanks for adding me to {guild.name}!\nIs this for a server or singleplayer world?\nReply with `server` or `singleplayer`.")
            server_settings[guild.id] = {'await_type': True}
        except:
            print(f"Couldn't DM owner of {guild.name}")

@bot.event
async def on_message(message):
    if not message.guild and message.author != bot.user:
        for guild_id, ss in server_settings.items():
            if ss.get('await_type'):
                mtype = message.content.strip().lower()
                if mtype not in ('server', 'singleplayer'):
                    await message.channel.send("Please reply with `server` or `singleplayer`.")
                    return
                ss['type'] = mtype
                ss['await_type'] = False
                ss['await_dir'] = True
                suggested_path = DEFAULT_SERVER_MODS_DIR if mtype == 'server' else DEFAULT_SP_MODS_DIR
                label = "server's" if mtype == "server" else "singleplayer world's"
                await message.channel.send(f"Please reply with your {label} mods directory path, or reply `default` to use `{suggested_path}`.")
                return
            if ss.get('await_dir'):
                mods_dir = message.content.strip()
                if mods_dir.lower() == 'default':
                    mods_dir = DEFAULT_SERVER_MODS_DIR if ss.get('type') == 'server' else DEFAULT_SP_MODS_DIR
                ss['mods_dir'] = mods_dir
                ss['await_dir'] = False
                await message.channel.send(
                    f"Mod directory set to `{mods_dir}`.\nGo to the server and type `!setupdatechannel` in the channel you want updates in, then `!checkmods` to run the check!")
                return
    await bot.process_commands(message)

@bot.command()
async def setmoddir(ctx, *, dirpath=None):
    guild_id = ctx.guild.id
    if not dirpath:
        cur_ss = server_settings.get(guild_id, {})
        await ctx.send(
            f"Usage: `!setmoddir /your/mods/dir` (Current: `{cur_ss.get('mods_dir') or '[Not set yet]'}`)")
        return
    server_settings.setdefault(guild_id, {})
    server_settings[guild_id]['mods_dir'] = dirpath
    await ctx.send(f"Mod directory updated to `{dirpath}`.")

@bot.command()
async def setupdatechannel(ctx):
    guild_id = ctx.guild.id
    server_settings.setdefault(guild_id, {})
    server_settings[guild_id]['channel_id'] = ctx.channel.id
    await ctx.send(f"I'll post update notifications here.")

@bot.command()
async def checkmods(ctx):
    guild_id = ctx.guild.id
    ss = server_settings.get(guild_id, {})
    mods_dir = ss.get('mods_dir')
    if not mods_dir:
        await ctx.send("Mods directory hasn't been set yet. Retry setup or use `!setmoddir /path/to/mods`.")
        return
    channel_id = ss.get('channel_id') or ctx.channel.id
    await do_checkmods(guild_id, channel_id, mods_dir)

bot.run(DISCORD_TOKEN)
