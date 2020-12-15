import discord
from discord.ext import commands
import json
import pandas

configJsonFile = open('config.json') #config.json contains the token and prefix
jsonData = json.load(configJsonFile)
prefix = jsonData['prefix'] #Reference to the prefix stated in the config.json
token = jsonData['token']
intents = discord.Intents(voice_states = True, members = True) #Specifies intents
client = commands.Bot(command_prefix = prefix)

#Ideas:
#Contador de días desde ultima salida a San Mike, Alexa play Despacito con comando de voz

inVoiceChannels = 0 #Counts how many people are currently in any voice channel

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
    await ctx.send("He gay")

#Greets the person that calls the command
@client.command()
async def hello(ctx):
    await ctx.send("Hello " + ctx.author.name)

@client.command()
async def leaderboard(ctx):
    leaderboardDf = pandas.read_csv('LastToLeaveLeaderboard.csv', index_col=0) #Used to keep track of last people to leave
    await ctx.send(leaderboardDf.to_string(index=False, header=False))

#----------------------------------------------------------------------#

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

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
            
        print("People in voice channels: " + str(inVoiceChannels))
        print(member.name + " connected to " + after.channel.name)

    #When a user leaves the voice channels
    if before.channel is not None and after.channel is None:
        isBot = memberIsBot(member)
        
        #If the member is not a bot
        if(isBot == False and inVoiceChannels > 0):
            inVoiceChannels -= 1

        print("People in voice channels: " + str(inVoiceChannels))
        print(member.name + " disconnected from " + before.channel.name)
        
        #If the number of people in the voice channel is 0 and the user that left is not a bot
        if(inVoiceChannels == 0 and isBot == False):
            print(member.name + " is gay lol")
            await generalTextChannel.send(member.name + ' was the last to leave :)') #Last to leave message

            #Updates the leaderboard
            updateLastToLeaveLeaderBoard(member.name)

client.run(token) #Calls the key from the config.json file