#bot.py
import os
import discord
import json
import requests
from graphqlclient import GraphQLClient
from dotenv import load_dotenv
from discord.ext import commands
#from qlient import Client, GraphQLResponse

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SMASHTOKEN = os.getenv('SMASHGG_TOKEN')
ggApiVersion = 'alpha'

bot = commands.Bot(command_prefix='!')




# @bot.command(name='helloBot')
# async def navi(ctx):
#     await ctx.send('hey!')

# @bot.event
# async def on_ready():
#     print(f'{bot.user.name} has connected to Discord!')

# bot.run(TOKEN)