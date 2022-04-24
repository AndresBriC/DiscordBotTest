import discord
from discord.ext import commands
from discord.utils import get

import pandas as pd
import random
import datetime

from github import Github

#For web scrapping
import requests
from bs4 import BeautifulSoup

from io import BytesIO

import os
from dotenv import load_dotenv
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

#Github api access
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)
repository = g.get_repo('AndresBriC/DiscordBotTest') #Get reference to the bot repo

prefix = "$" #Sets the prefix
intents = discord.Intents.all() #Specifies intents
client = commands.Bot(command_prefix = prefix, intents = intents)

#Ideas:
#Alexa play Despacito con comando de voz, integracion con API de league

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
    #Gets the leaderboard csv from github
    lastToLeaveLeaderboardCSV = repository.get_contents("LastToLeaveLeaderboard.csv")

    #Make a pandas dataframe from the csv in the repo
    leaderboardDf = pd.read_csv('https://raw.githubusercontent.com/AndresBriC/DiscordBotTest/main/LastToLeaveLeaderboard.csv', index_col=0) #Used to keep track of last people to leave

    #Adds 1 point if the user exists
    if userExists(memberName, leaderboardDf) == True:
        index = getIndexOfUser(memberName, leaderboardDf)
        leaderboardDf.at[index, 'Score'] = leaderboardDf.loc[index]['Score'] + 1
        print("User was found")
    else: #If the user isn't in the leaderboard, it gets added and sets the score to 1
        leaderboardDf = leaderboardDf.append({'User':memberName,'Score':1}, ignore_index=True)
        print("User was added")

    #Updates the file in the repo, using the csv transformed back from the pandas dataframe
    repository.update_file(lastToLeaveLeaderboardCSV.path, "Updates the LastToLeaveLeaderboard csv", leaderboardDf.to_csv(), lastToLeaveLeaderboardCSV.sha, branch="main")

#-------------------------------COMMANDS-------------------------------#

#Dumb sutff cog
class dumbStuff(commands.Cog, name = "Dumb Stuff"):

    #Greets the person that calls the command
    @commands.command(help = "Greet the bot :D")
    async def hello(self, ctx):
        await ctx.send("Hello " + ctx.author.name)

    @commands.command(help = "Shows the amount of days since we went to San Mike :'(")
    async def sadmike(self, ctx):
        ultimoSanMike = datetime.datetime(2021,6,12)
        hoyEnFecha = datetime.datetime(datetime.datetime.now().year,datetime.datetime.now().month,datetime.datetime.now().day)
        diasDesdeSanMike = hoyEnFecha.date()-ultimoSanMike.date()

        await ctx.send(str(diasDesdeSanMike.days) + " dias desde que se hizo San Mike :(")

    #Displays the LastToLeaveLeaderboard as a discord message, without indexes and headers
    @commands.command(help = "Shows who has left last the most.")
    async def leaderboard(self, ctx):
        leaderboardDf = pd.read_csv('https://raw.githubusercontent.com/AndresBriC/DiscordBotTest/main/LastToLeaveLeaderboard.csv', index_col=0) #Used to keep track of last people to leave
        await ctx.send(leaderboardDf.to_string(index=False, header=False))

    #Sends a message for each word in lyrics until the 25th word
    @commands.command(brief = "Lets the bot repeat up to 25 words you say.", help = "Lets the bot repeat up to 25 words you say. Has a minute cooldown to prevent spam.")
    @commands.cooldown(1, 60) #Sets a cooldown of a minute after one use
    async def sing(self, ctx, *lyrics):
        limitCounter = 0

        for word in lyrics:
            limitCounter += 1       
            await ctx.send(word + "\n")
            if limitCounter == 26:
                break

    #Prints a random choice
    @commands.command(help = "In case you wanna know.")
    async def amidumb(self, ctx):
        await ctx.send(random.choice(["Yes", "No"]))

    #Returns a response from one of 20 choices taken from the 8 Ball toy
    @commands.command(help = "Ask a yes/no question and you'll be answered with the truth.")
    async def eightball(self, ctx):
        await ctx.send(random.choice(["En mi opinión, sí", "Es cierto", "Es decididamente así", "Probablemente", "Buen pronóstico", "Todo apunta a que sí", "Sin duda", "Sí", "Sí - definitivamente", "Debes confiar en ello", "Respuesta vaga, vuelve a intentarlo", "Pregunta en otro momento", "Será mejor que no te lo diga ahora", "No puedo predecirlo ahora", "Concéntrate y vuelve a preguntar", "No cuentes con ello", "Mi respuesta es no", "Mis fuentes me dicen que no", "Las perspectivas no son buenas", "Muy dudoso"]))

    #Makes a triangle pattern with a given word
    @commands.command(brief = "Turns a word into a pyramid.", help = "Turns single a word into a pyramid, limited to short words.")
    async def pyramid(self, ctx, word):
        
        triangleWord = ""
        lengthLimit = 12

        if len(word) < lengthLimit:
            #From the first letter to the full word
            for i in range(0, len(word)+1):
                triangleWord += word[:i] + "\n"

            #From full word-1 to first letter
            for i in range(len(word)-1, -1, -1):
                triangleWord += word[:i] + "\n"
            
            await ctx.send(triangleWord)
        else:
            await ctx.send("Word is too large, limit is " + str(lengthLimit) + " characters.")
    
    #Lets a user spam ping another user once per hour
    @commands.command(brief = "Spam pings a user", help = "Spam pings a user. Limited to one use per hour.")
    @commands.cooldown(1,3600)
    async def spamping(self, ctx, user):
        for i in range (0,16):
            await ctx.send(user)


#Useful stuff cog
class usefulStuff(commands.Cog, name = "Useful Stuff"):

#Opens a poll with n, up to 10 number of options, inspired by the Simple Poll bot https://top.gg/bot/simplepoll and https://github.com/stayingqold/Poll-Bot/blob/master/cogs/poll.py
    @commands.command(brief = "Lets you run a 10 option poll.", help = "Lets you run a poll with up to 10 options. Put each option and the title between quotation marks.")
    async def poll(self, ctx, pollTitle, *options):
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

        embedPollMsg = discord.Embed(title = pollTitle, description = completePoll, color = discord.Colour.red()) #Creates the embed
        pollMsg = await ctx.message.channel.send(embed=embedPollMsg) #Sends the embed message and asigns it to a variable
        
        #Does another loop to add the reactions
        index = 1
        for option in options:
            await pollMsg.add_reaction(emojiLetters[index-1])    
            index += 1
            if index == 11: #Stops the options at the 10th
                break

    @commands.command(brief = 'Gene slicing tool', help = 'Type ' + prefix + "geneslice and the justpaste.it URL containing ONLY the gene you want to slice.")
    async def geneslice(self, ctx, url):
        
        messageToSend = ""

        page = requests.get(str(url)) 
        soup = BeautifulSoup(page.content, 'html.parser')

        siteText = soup.select('p')#Gets all the <p>'s in the site

        #Gene info
        geneSequence = siteText[0].text #Extracts the first one, which contains the gene sequence in the case of justpaste.it
        geneLength = len(geneSequence)
        numA = 0 #Number of A's
        numT = 0 #Number of T's
        numG = 0 #Number of G's
        numC = 0 #Number of C's

        #Important codons
        startingCodon = "ATG"
        stoppingCodon1 = "TAG"
        stoppingCodon2 = "TAA"
        stoppingCodon3 = "TGA"

        #Variables for codon checking
        codonDict = {"name"  : ' ', "position" : 0}
        currentCodonPos = 0

        #CDS info
        cdsStartingPos = 0
        cdsWithLastPiece = ""
        cdsWithoutLastPiece = ""

        #Groups every three nucleotide and returns the codon and the position of the next codon
        def codonFinder(geneToParse, nextCodonPos):
            codonToReturn = geneToParse[nextCodonPos] + geneToParse[nextCodonPos + 1] + geneToParse[nextCodonPos + 2]
            
            return {'name' : codonToReturn, 'position' : nextCodonPos + 3}

        messageToSend = ("Original gene sequece: " + geneSequence)
        messageToSend += "\n" + ("Gene length: " + str(geneLength))

        counterSequence = ""
        #Creates counter sequence and counts each base
        for base in geneSequence:
            if base == 'A':
                counterSequence += 'T'
                numA += 1
            if base == 'T':
                counterSequence += 'A'
                numT += 1
            if base == 'G':
                counterSequence += 'C'
                numG += 1
            if base == 'C':
                counterSequence += 'G'
                numC += 1

        #Checks the gene until the end is reached
        while(currentCodonPos <= (geneLength-3)):

            codonDict = codonFinder(geneSequence, currentCodonPos)
            currentCodonPos = codonDict["position"] #Updates the current codon's position

            #Stops the loop when the starting codon is found
            if codonDict['name'] == startingCodon:
                messageToSend += "\n\n" + ("Found the starting codon at position: " + str(currentCodonPos-2))
                cdsStartingPos = currentCodonPos-2
                break

        #Stores the CDS based on the last loop's info
        cdsWithLastPiece = geneSequence[cdsStartingPos-1:geneLength]

        messageToSend += "\n" + ("CDS with last piece: \n" + cdsWithLastPiece)

        #Checks the gene until the end is reached
        while(currentCodonPos <= (geneLength-3)):

            codonDict = codonFinder(geneSequence, currentCodonPos)
            currentCodonPos = codonDict["position"] #Updates the current codon's position

            #Stops the loop when the starting codon is found
            if codonDict['name'] == stoppingCodon1 or codonDict['name'] == stoppingCodon2 or codonDict['name'] == stoppingCodon3:
                messageToSend += "\n\n" + ("Found the stopping codon at position: " + str(currentCodonPos-2))
                messageToSend += "\n" + ("Codon found: " + codonDict['name'])
                cdsLastPos = currentCodonPos-3
                break

        cdsWithoutLastPiece = geneSequence[cdsStartingPos-1:cdsLastPos]
        #lastPiece = geneSequence[cdsLastPos:geneLength] #Protection thing

        messageToSend += "\n" + ("CDS without last piece: " + cdsWithoutLastPiece)
        messageToSend += "\n" + ("Counter sequence: " + counterSequence)
        messageToSend += "\n" + ("Counter sequence length: " + str(len(counterSequence)))
        messageToSend += "\n" + ("Number of A's: " + str(numA))
        messageToSend += "\n" + ("Number of T's: " + str(numT))
        messageToSend += "\n" + ("Number of G's: " + str(numG))
        messageToSend += "\n" + ("Number of C's: " + str(numC))
        messageToSend += "\n" + ('GC percentage: '+ str((numG+numC)/(numA+numC+numG+numT)))

        #Taken from https://stackoverflow.com/questions/61786264/discord-py-send-long-messages
        as_bytes = map(str.encode, messageToSend)
        content = b"".join(as_bytes)

        await ctx.send("Sliced gene: ", file = discord.File(BytesIO(content), "slicedGene.txt"))

#-------------------------------EVENTS-------------------------------#

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client)) #Console on ready message
    
    #Adds current activity
    await client.change_presence(activity=discord.Game(name= prefix + 'help'))

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
            leaveTextChoices = random.choice([member.name + " is slow af lmao", member.name + " ate dirt", member.name + " es un huevo jodido", member.name + " was eaten by zombies", member.name + " wasn't paying attention"])
            print(member.name + " was the last to leave")
            await generalTextChannel.send(leaveTextChoices) #Last to leave message

            #Updates the leaderboard
            updateLastToLeaveLeaderBoard(member.name) #Need to move it to an online database

@client.event
async def on_typing(channel, user, when):
    if random.randint(0,1000) == 1: #Generates a number from 1 to 1000
        await channel.send('Ke andas escriviendo') #If the random number was 1, send this message

@client.event
async def on_command_error(ctx, error):
    await ctx.send(error) #To notify discord users of the error

#Adds cogs
client.add_cog(dumbStuff(client))
client.add_cog(usefulStuff(client))

client.run(DISCORD_TOKEN) #Calls the key from the env file