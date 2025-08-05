import discord
from discord.ext import commands
import subprocess
import tempfile
import os
import asyncio
from threading import Thread
from flask import Flask

# Set up a minimal web server to keep the service alive on Render free tier
app = Flask(__name__)
@app.route("/")
def index():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# Start Flask in a thread
Thread(target=run_web).start()

# Discord bot setup
FAIRY_STOCKFISH_PATH = "./fairy-stockfish"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

def extract_ini_content(message_content):
    """Extract INI content from message, handling triple backticks if present."""
    content = message_content.replace("!check", "").strip()
    
    # Check if content is wrapped in triple backticks
    if content.startswith('```') and content.endswith('```'):
        lines = content.split('\n')
        
        # Strip opening backticks from first line (keeping any content after)
        if lines and lines[0].startswith('```'):
            first_line = lines[0]
            # Remove ``` and optional language specifier
            after_backticks = first_line[3:]
            # If there's a language specifier (alphabetic), remove it
            if after_backticks and after_backticks[0].isalpha():
                # Find end of language specifier
                i = 0
                while i < len(after_backticks) and after_backticks[i].isalpha():
                    i += 1
                lines[0] = after_backticks[i:].lstrip()  # Strip leading spaces
            else:
                lines[0] = after_backticks.lstrip()  # Strip leading spaces
        
        # Strip closing backticks from last line (keeping any content before)
        if lines and lines[-1].endswith('```'):
            lines[-1] = lines[-1][:-3].rstrip()  # Strip trailing spaces
        
        # Remove empty lines that were created only from backtick stripping
        if lines and not lines[0].strip():
            lines = lines[1:]
        if lines and not lines[-1].strip():
            lines = lines[:-1]
        
        content = '\n'.join(lines)
    
    return content

@bot.command(name="check")
async def check_variant(ctx):
    file = None
    ini_content = None

    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith(".ini"):
            await ctx.send("Please upload a `.ini` file.")
            return
        file = await attachment.read()
    else:
        ini_content = extract_ini_content(ctx.message.content)
        if not ini_content:
            await ctx.send("Please provide `.ini` content or upload a file.")
            return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ini") as tmp:
        if file:
            tmp.write(file)
        else:
            tmp.write(ini_content.encode("utf-8"))
        tmp.flush()

        try:
            proc = await asyncio.create_subprocess_exec(
                FAIRY_STOCKFISH_PATH, "check", tmp.name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            result = ""
            if proc.returncode:
                result = f"**Exit Code:** {proc.returncode}\n"
            if stderr:
                result += f"**Check result:**\n```\n{stderr.decode()[:1900]}\n```"
            elif stdout:
                result += f"**Output:**\n```\n{stdout.decode()[:1900]}\n```"
            else:
                result += "_No output or errors._"

            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
        finally:
            os.unlink(tmp.name)

bot.run(os.getenv("DISCORD_BOT_TOKEN", "YOUR_DISCORD_BOT_TOKEN"))
