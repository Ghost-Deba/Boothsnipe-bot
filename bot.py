import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the .env file
TOKEN = os.getenv('DISCORD_TOKEN')

# Replace with your API endpoint
API_URL = 'https://biggamesapi.io/api/rap'

# Initialize the bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to fetch data from the API
async def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()  # Assuming the API returns a list of items
    else:
        return None

# Function to transform and format the data
def transform_data(data):
    transformed_items = []
    for item in data:
        transformed_item = {
            "Item": item.get("id", "N/A"),  # id -> name
            "MaxPrice": item.get("Value", "N/A"),  # Value -> MaxPrice
            "Class": item.get("Category", "N/A")  # Category -> Class
        }
        transformed_items.append(transformed_item)
    return transformed_items

# Function to generate the script
def generate_script(items):
    script = """
script_key="UR KEY HERE";
--Settings For Booths Sniper
_G.ZapHubBoothsSniperSettings = {
    MinimumGems = 0,
    Items = { 
"""
    for item in items:
        script += f'        {{Item = "{item["Item"]}", MaxPrice = {item["MaxPrice"]}, Class = "{item["Class"]}"}},\n'
    script += """
    },
    Extras = {
        AnyItem = {Enabled = false, PercentageProfit = "10", MaxPrice = 500000000},
        TitanicPet = {Enabled = false, PercentageProfit = "25", MaxPrice = 500000000},
        HugePet = {Enabled = false, PercentageProfit = "0", MaxPrice = 28000000},
    },
    ServerHop = {
        Enabled = true, -- true / false
    },
    Webhook = {
        Enabled = true, -- true / false
        WebhookURL = "UR WEBHOOK HERE",
    },
}

loadstring(game:HttpGet('https://zaphub.xyz/ExecBoothSniper'))()
"""
    return script

# Slash command to fetch and send data
@bot.tree.command(name="get", description="Fetch items from the API and generate a script")
async def get_command(interaction: discord.Interaction):
    await interaction.response.defer()  # Acknowledge the interaction
    data = await fetch_data()
    if data:
        # Transform the data
        transformed_data = transform_data(data)
        # Generate the script
        script = generate_script(transformed_data)
        # Send the script as a code block
        await interaction.followup.send(f"```lua\n{script}\n```")
    else:
        await interaction.followup.send("Failed to fetch data from the API.")

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        # Sync slash commands with Discord
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Run the bot
bot.run(TOKEN)
