import discord
from discord import app_commands
import json
import os
import secrets
import time
from datetime import datetime

TOKEN = 'MTQ4NTQ3MDMxMDA2ODEyOTg3Mg.GfUZ_c.aOwltuESK8dnIuEZQY4qGTaGas3e-uBxqCrqQc
GUILD_ID = 1395990315500044458
KEYS_FILE = 'keys.json'

def load_keys():
    if not os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'w') as f:
            json.dump({}, f)
    with open(KEYS_FILE, 'r') as f:
        return json.load(f)

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def generate_key(key_type):
    prefix = 'LT' if key_type == 'lifetime' else 'MO'
    random = secrets.token_hex(8).upper()
    return f"SFS-{prefix}-{random[0:4]}-{random[4:8]}-{random[8:12]}"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
guild = discord.Object(id=GUILD_ID)

@client.event
async def on_ready():
    await tree.sync(guild=guild)
    print(f'Bot ready as {client.user}')

@tree.command(guild=guild, name="generate", description="Generate a new key")
@app_commands.describe(
    key_type="Key type: monthly or lifetime",
    hwid="Lock to HWID (leave blank for any)",
    note="Note e.g. username"
)
@app_commands.choices(key_type=[
    app_commands.Choice(name="Monthly", value="monthly"),
    app_commands.Choice(name="Lifetime", value="lifetime"),
])
async def generate(interaction: discord.Interaction, key_type: str, hwid: str = "any", note: str = ""):
    key = generate_key(key_type)
    keys = load_keys()
    now = int(time.time())

    keys[key] = {
        "keyType": key_type,
        "hwid": hwid,
        "created": now,
        "createdBy": str(interaction.user),
        "note": note,
    }
    save_keys(keys)

    expiry_ts = now + 30*24*60*60
    expiry_text = f"<t:{expiry_ts}:R>" if key_type == "monthly" else "Never expires"

    embed = discord.Embed(title="🗡️ Key Generated", color=0x4141a0, timestamp=datetime.utcnow())
    embed.add_field(name="Key", value=f"`{key}`", inline=False)
    embed.add_field(name="Type", value=key_type.capitalize(), inline=True)
    embed.add_field(name="HWID", value="Any (not locked)" if hwid == "any" else f"`{hwid}`", inline=True)
    embed.add_field(name="Expiry", value=expiry_text, inline=True)
    embed.add_field(name="Note", value=note or "None", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(guild=guild, name="revoke", description="Revoke a key")
@app_commands.describe(key="Key to revoke")
async def revoke(interaction: discord.Interaction, key: str):
    keys = load_keys()
    if key not in keys:
        await interaction.response.send_message("❌ Key not found.", ephemeral=True)
        return
    del keys[key]
    save_keys(keys)
    await interaction.response.send_message(f"✅ Key `{key}` revoked.", ephemeral=True)

@tree.command(guild=guild, name="listkeys", description="List all keys")
async def listkeys(interaction: discord.Interaction):
    keys = load_keys()
    if not keys:
        await interaction.response.send_message("No keys found.", ephemeral=True)
        return

    now = int(time.time())
    lines = []
    for k, v in keys.items():
        if v["keyType"] == "monthly":
            expiry = v["created"] + 30*24*60*60
            status = "❌ Expired" if now > expiry else f"<t:{expiry}:R>"
        else:
            status = "♾️ Lifetime"
        hwid_display = "any" if v["hwid"] == "any" else v["hwid"][:8] + "..."
        lines.append(f"`{k}` | {v['keyType']} | {hwid_display} | {status} | {v.get('note','')}")

    chunks = [lines[i:i+10] for i in range(0, len(lines), 10)]
    embeds = []
    for i, chunk in enumerate(chunks):
        embed = discord.Embed(
            title="🗝️ All Keys" if i == 0 else "",
            description="\n".join(chunk),
            color=0x4141a0
        )
        embeds.append(embed)

    await interaction.response.send_message(embeds=embeds[:10], ephemeral=True)

@tree.command(guild=guild, name="keyinfo", description="Get info on a key")
@app_commands.describe(key="Key to look up")
async def keyinfo(interaction: discord.Interaction, key: str):
    keys = load_keys()
    if key not in keys:
        await interaction.response.send_message("❌ Key not found.", ephemeral=True)
        return

    data = keys[key]
    now = int(time.time())
    expired = data["keyType"] == "monthly" and now > data["created"] + 30*24*60*60

    embed = discord.Embed(
        title="🔍 Key Info",
        color=0xff4444 if expired else 0x4141a0
    )
    embed.add_field(name="Key", value=f"`{key}`", inline=False)
    embed.add_field(name="Type", value=data["keyType"], inline=True)
    embed.add_field(name="Status", value="❌ Expired" if expired else "✅ Valid", inline=True)
    embed.add_field(name="HWID", value="Any" if data["hwid"] == "any" else f"`{data['hwid']}`", inline=False)
    embed.add_field(name="Created by", value=data["createdBy"], inline=True)
    embed.add_field(name="Note", value=data.get("note") or "None", inline=True)
    embed.add_field(name="Created", value=f"<t:{data['created']}:F>", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(guild=guild, name="updatehwid", description="Update HWID for a key")
@app_commands.describe(key="Key", hwid="New HWID")
async def updatehwid(interaction: discord.Interaction, key: str, hwid: str):
    keys = load_keys()
    if key not in keys:
        await interaction.response.send_message("❌ Key not found.", ephemeral=True)
        return
    keys[key]["hwid"] = hwid
    save_keys(keys)
    await interaction.response.send_message(f"✅ HWID updated for `{key}`", ephemeral=True)

client.run(MTQ4NTQ3MDMxMDA2ODEyOTg3Mg.GfUZ_c.aOwltuESK8dnIuEZQY4qGTaGas3e-uBxqCrqQc)