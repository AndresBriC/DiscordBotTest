import discord
from discord.ext import commands
from discord.utils import get

import pandas
import random
import datetime

import os
from dotenv import load_dotenv
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

prefix = "$" #Sets the prefix
intents = discord.Intents.all() #Specifies intents
client = commands.Bot(command_prefix = prefix, intents = intents)

#Ideas:
#Contador de días desde ultima salida a San Mike, Alexa play Despacito con comando de voz, integracion con API de league

#-------------------------------GLOBAL VARIABLES----------------------------------#

inVoiceChannels = 0 #Counts how many people are currently in any voice channel

#-------------------------------AUXILIARY FUNCTIONS-------------------------------#

#Returns a bool depending if the indicated user exists within the given pandas database
def userExists(user, df):
    found = df[df['User'].str.contains(user)]

    if len(found) == 0:
        return False
    else:
        return True

#Returns the index of the indicated user, within the given database
def getIndexOfUser(user, df):
    dataTop = df.head()

    for i in dataTop.index:
        if df.loc[i]['User'] == user:
            return i

#Returns True if member has "Bots" as a role
def memberIsBot(member):
    isABot = False

    #Checks if the member has the Bots role
    for role in member.roles:
        if str(role) == "Bots":
            print("A bot joined a voice channel")
            isABot = True
            break
    
    return isABot

#Adds user to the leaderboard if not present, if not, adds 1 point to the user
def updateLastToLeaveLeaderBoard(memberName):
    leaderboardDf = pandas.read_csv('LastToLeaveLeaderboard.csv', index_col=0) #Used to keep track of last people to leave

    if userExists(memberName, leaderboardDf) == True:
        index = getIndexOfUser(memberName, leaderboardDf)
        leaderboardDf.at[index, 'Score'] = leaderboardDf.loc[index]['Score'] + 1
        print("User was found")
    else:
        leaderboardDf = leaderboardDf.append({'User':memberName,'Score':1}, ignore_index=True)
        print("User was added")

    leaderboardDf.to_csv('LastToLeaveLeaderboard.csv')

#-------------------------------COMMANDS-------------------------------#

@client.command()
async def hegay(ctx):
    await ctx.send("El que use este comando le gusta besar hombres")

#Greets the person that calls the command
@client.command()
async def hello(ctx):
    await ctx.send("Hello " + ctx.author.name)

@client.command()
async def sadmike(ctx):
    ultimoSanMike = datetime.datetime(2019,11,7)
    hoyEnFecha = datetime.datetime(datetime.datetime.now().year,datetime.datetime.now().month,datetime.datetime.now().day)
    diasDesdeSanMike = hoyEnFecha.date()-ultimoSanMike.date()

    await ctx.send(str(diasDesdeSanMike.days) + " dias desde que se hizo San Mike :(")

#Displays the LastToLeaveLeaderboard as a discord message, without indexes and headers
@client.command()
async def leaderboard(ctx):
    leaderboardDf = pandas.read_csv('LastToLeaveLeaderboard.csv', index_col=0) #Used to keep track of last people to leave
    await ctx.send(leaderboardDf.to_string(index=False, header=False))

#Opens a poll with n, up to 10 number of options, inspired by the Simple Poll bot https://top.gg/bot/simplepoll and https://github.com/stayingqold/Poll-Bot/blob/master/cogs/poll.py
@client.command()
async def poll(ctx, *options):
    index = 1 #Used to number each option
    completePoll = "" #Used to display all the poll options
    #Emoji letters from a to j 
    emojiLetters = [
            "\N{REGIONAL INDICATOR SYMBOL LETTER A}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER C}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER E}", 
            "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER G}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER H}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER I}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER J}"
    ]

    #Builds the embed with all the options
    for option in options:
        completePoll += emojiLetters[index-1] + " - "  + option + "\n\n"
        index += 1
        if index == 11: #Stops the options at the 10th
            break

    embedPollMsg = discord.Embed(title = "POLL", description = completePoll, color = discord.Colour.red()) #Creates the embed
    pollMsg = await ctx.message.channel.send(embed=embedPollMsg) #Sends the embed message and asigns it to a variable
    
    #Does another loop to add the reactions for easy access
    index = 1
    for option in options:
        await pollMsg.add_reaction(emojiLetters[index-1])    
        index += 1
        if index == 11: #Stops the options at the 10th
            break


#Sends a message for each word in lyrics until the 25th word
@client.command()
@commands.cooldown(1, 60) #Sets a cooldown of a minute after one use
async def sing(ctx, *lyrics):
    limitCounter = 0

    for word in lyrics:
        limitCounter += 1       
        await ctx.send(word + "\n")
        if limitCounter == 26:
            break

#Prints a random choice
@client.command()
async def amIDumb(ctx):
    await ctx.send(random.choice(["Yes", "No"]))

#Returns a response from one of 20 choices taken from the 8 Ball toy
@client.command()
async def eightBall(ctx):
    await ctx.send(random.choice(["En mi opinión, sí", "Es cierto", "Es decididamente así", "Probablemente", "Buen pronóstico", "Todo apunta a que sí", "Sin duda", "Sí", "Sí - definitivamente", "Debes confiar en ello", "Respuesta vaga, vuelve a intentarlo", "Pregunta en otro momento", "Será mejor que no te lo diga ahora", "No puedo predecirlo ahora", "Concéntrate y vuelve a preguntar", "No cuentes con ello", "Mi respuesta es no", "Mis fuentes me dicen que no", "Las perspectivas no son buenas", "Muy dudoso"]))
    

#-------------------------------EVENTS-------------------------------#

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client)) #Console on ready message

@client.event
async def on_voice_state_update(member, before, after):
    generalTextChannel = discord.utils.get(member.guild.channels, name = 'general') #Looks for text channel named general

    global inVoiceChannels #Counts how many people are currently in any voice channel

    #When the user joins a voice channel
    if before.channel is None and after.channel is not None:

        #Checks if the member has the Bots role
        isBot = memberIsBot(member)
        
        #If the member is not a bot
        if(isBot == False):
            inVoiceChannels += 1
            
        #Console messages
        print("People in voice channels: " + str(inVoiceChannels))
        print(member.name + " connected to " + after.channel.name)

    #When a user leaves the voice channels
    if before.channel is not None and after.channel is None:
        isBot = memberIsBot(member)
        
        #If the member is not a bot
        if(isBot == False and inVoiceChannels > 0):
            inVoiceChannels -= 1

        #Console messages
        print("People in voice channels: " + str(inVoiceChannels))
        print(member.name + " disconnected from " + before.channel.name)
        
        #If the number of people in the voice channel is 0 and the user that left is not a bot
        if(inVoiceChannels == 0 and isBot == False):
            print(member.name + " was the last to leave")
            await generalTextChannel.send(member.name + ' was the last to leave') #Last to leave message

            #Updates the leaderboard
            #updateLastToLeaveLeaderBoard(member.name) #Need to move it to an online database

@client.event
async def on_typing(channel, user, when):
    if random.randint(0,1000) == 1: #Generates a number from 1 to 1000
        await channel.send('Ke andas escriviendo') #If the random number was 1, send this message

@client.event
async def on_command_error(ctx, error):
    await ctx.send(error) #To notify discord users of the error

client.run(DISCORD_TOKEN) #Calls the key from the env file