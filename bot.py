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

gql = GraphQLClient('https://api.smash.gg/gql/' + ggApiVersion)
gql.inject_token('Bearer ' + SMASHTOKEN)



@bot.command(name = 'standings')
async def cmdstandings(ctx, tourneyslug, amount: int):
    getTourneyBySlug = gql.execute('''
    query TournamentInfo($slug: String!) {
    tournament(slug: $slug) {
        id
        name
        events {
        id
        }
    }
    }
    ''',
    {
        "slug": tourneyslug
    })
    tourney = json.loads(getTourneyBySlug)
    eventID = tourney["data"]["tournament"]["events"][0]["id"]



    getEventStandings = gql.execute('''
    query EventStandings($eventId: ID!, $page: Int!, $perPage: Int!) {
    event(id: $eventId) {
        id
        name
        standings(query: {
        perPage: $perPage,
        page: $page
        }){
        nodes {
            placement
            entrant {
            id
            name
            }
        }
        }
    }
    }
    ''',
    {
        "eventId": eventID,
        "page": 1,
        "perPage": amount
    })

    standings = json.loads(getEventStandings)
    message = f'Top {amount} for {standings["data"]["event"]["name"]}:\n'
    for _standing in standings["data"]["event"]["standings"]["nodes"]:
        message += f'{_standing["placement"]}: {_standing["entrant"]["name"]}\n'
    await ctx.send(message)




@bot.command(name='helloBot')
async def navi(ctx):
    await ctx.send('hey!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)