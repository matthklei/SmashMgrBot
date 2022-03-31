#bot.py
import os
import discord
import json
import requests
from replit import db
from graphqlclient import GraphQLClient
from discord.ext import commands

TOKEN = os.environ['DISCORD_TOKEN']
SMASHTOKEN = os.environ['SMASHGG_TOKEN']
ggApiVersion = 'alpha'

bot = commands.Bot(command_prefix='!')

gql = GraphQLClient('https://api.smash.gg/gql/' + ggApiVersion)
gql.inject_token('Bearer ' + SMASHTOKEN)

@bot.command(name = 'setTag', help='Sets your smash.gg tag in the database for use with tournament entrant related commands.')
async def cmdtag(ctx, tag):
	discid = ctx.author.id
	db['discid' + str(discid)] = tag
	await ctx.send(f'I now know your smash.gg tag is {tag}. Thanks!')

@bot.command(name = 'amRegistered', help='Returns whether or not sender is registered for any event in a given tournament')
async def cmdreg(ctx, tourneyslug):
    discid = str(ctx.author.id)
    tag = ''
    if 'discid'+discid in db.keys():
        tag = db['discid'+discid]
    else:
        await ctx.send('Your discord id is not in the database. Try !setTag first.')
        return
    getTourneyBySlug = gql.execute('''
query TournamentInfo($slug: String! $page: Int!) {
    tournament(slug: $slug) {
      id
      name
      events {
        	id
			name
            entrants(query: {
                page: $page
                perPage: 500
            }) {
      pageInfo {
        total
        totalPages
      }
      nodes {
        id
        participants {
          id
          gamerTag
        }
      }
    }
      }
  }
}
    ''',
    {
        "slug": tourneyslug,
        "page": 1
    })
    tourney = json.loads(getTourneyBySlug)
    message = f'{tag} is registered in the following events:\n'
    eventlist = ''
    for event in tourney["data"]["tournament"]["events"]:
        for entrant in event["entrants"]["nodes"]:
            #print(f'participants[0] = {entrant["participants"][0]["gamerTag"]}\n')
            if entrant["participants"][0]["gamerTag"] == tag:
                eventlist += f'{event["name"]}\n'
    if eventlist == '':
        await ctx.send('You are not registered in any events for this tournament')
    else:
        await ctx.send(message + eventlist)


@bot.command(name = 'isRegistered', help='Returns whether or not someone is registered for any event in a given tournament. Be sure to use their smash.gg tag exactly how it appears!')
async def cmdreg(ctx, tourneyslug, tag):
    getTourneyBySlug = gql.execute('''
query TournamentInfo($slug: String! $page: Int!) {
    tournament(slug: $slug) {
      id
      name
      events {
        	id
			name
            entrants(query: {
                page: $page
                perPage: 500
            }) {
      pageInfo {
        total
        totalPages
      }
      nodes {
        id
        participants {
          id
          gamerTag
        }
      }
    }
      }
  }
}
    ''',
    {
        "slug": tourneyslug,
        "page": 1
    })
    tourney = json.loads(getTourneyBySlug)
    message = f'{tag} is registered in the following events:\n'
    eventlist = ''
    for event in tourney["data"]["tournament"]["events"]:
        for entrant in event["entrants"]["nodes"]:
            #print(f'participants[0] = {entrant["participants"][0]["gamerTag"]}\n')
            if entrant["participants"][0]["gamerTag"] == tag:
                eventlist += f'{event["name"]}\n'
    if eventlist == '':
        await ctx.send(f'{tag} is not registered in any events for this tournament')
    else:
        await ctx.send(message + eventlist)



@bot.command(name = 'standings', help='Returns standings for a tournament. tourneyslug = part after \'/tournament/\' in smash.gg link')
async def cmdstandings(ctx, tourneyslug, eventname, amount: int):
	#query for tourney info
    getTourneyBySlug = gql.execute('''
    query TournamentInfo($slug: String!) {
    tournament(slug: $slug) {
        id
        name
        events {
        id
		name
        }
    }
    }
    ''',
    {
        "slug": tourneyslug
    })
    tourney = json.loads(getTourneyBySlug)
    eventfound = False
    for event in tourney["data"]["tournament"]["events"]:
        if event["name"] == eventname:
            eventID = event["id"]
            eventfound = True
    if eventfound == False:
        await ctx.send('Sorry, event not found.')
        return
	#query for standings based on previous query tournament
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


@bot.command(name = 'listEvents', help = 'Returns list of events for a tournament.')
async def listevents(ctx, tourneyslug):
    getTourneyBySlug = gql.execute('''
    query TournamentInfo($slug: String!) {
    tournament(slug: $slug) {
        id
        name
        events {
        id
		name
        }
    }
    }
    ''',
    {
        "slug": tourneyslug
    })
    tourney = json.loads(getTourneyBySlug)
    message = f'Events held at {tourney["data"]["tournament"]["name"]}:\n'
    for event in tourney["data"]["tournament"]["events"]:
        message += event["name"] + '\n'
    await ctx.send(message)

@bot.command(name='helloBot', help='Say hi!')
async def navi(ctx):
    await ctx.send('hey!')


@bot.event
async def on_ready():
	print(bot.user.name + ' connected')
	
bot.run(TOKEN)