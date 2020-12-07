import discord
import json

configJsonFile = open('config.json')
jsonData = json.load(configJsonFile)
prefix = jsonData['prefix'] #Reference to the prefix stated in the config.json
intents = discord.Intents(voice_states = True, members = True) #Specifies intents

#Ideas:
#Contador de días desde ultima salida a San Mike, Alexa play Despacito con comando de voz

inVoiceChannels = 0 #Counts how many people are currently in any voice channel

class MyClient(discord.Client):

    #Returns True if member has "Bots" as a role
    async def memberIsBot(self, member):
        isABot = False

        for roles in member.roles: #Loops for each role the member has
            if roles == "Bots": #If the member has a role named "Bots"
                print("Member is a bot")
                isABot = True
                break
        
        return isABot

    #Prints to console when ready
    async def on_ready(self):
        print('We have logged in as ' + self.user.name + " ID: " + str(self.user.id))

    async def on_message(self, message):
        #Prevents bot from replying to itself
        if message.author.id == self.user.id:
            return

        #Greeting message
        lowerCaseMessage = message.content.lower() #Transforms message to lowrcase
        if lowerCaseMessage == (prefix + "hello") or lowerCaseMessage == (prefix + "hi"): #Compares the lowercase version of the message
            await message.channel.send("Hello " + message.author.name)

        if lowerCaseMessage == (prefix + "hegay?"):
            await message.channel.send("He gay ")


    async def on_voice_state_update(self, member, before, after):
        generalTextChannel = discord.utils.get(member.guild.channels, name = 'general') #Looks for text channel named general

        global inVoiceChannels #Counts how many people are currently in any voice channel

        #When the user joins a voice channel
        if before.channel is None and after.channel is not None:
            isBot = False

            #Checks if the member has the Bots role
            for role in member.roles:
                if str(role) == "Bots":
                    print("A bot joined a voice channel")
                    isBot = True
            
            #If the member is not a bot
            if(isBot == False):
                inVoiceChannels += 1
                
            print("People in voice channels: " + str(inVoiceChannels))
            print(member.name + " connected to " + after.channel.name)

        #When a user leaves the voice channels
        if before.channel is not None and after.channel is None:
            isBot = False

            #Checks if the member has the Bots role
            for role in member.roles:
                if str(role) == "Bots":
                    print("A bot left a voice channel")
                    isBot = True
            
            #If the member is not a bot
            if(isBot == False):
                inVoiceChannels -= 1

            print("People in voice channels: " + str(inVoiceChannels))
            print(member.name + " disconnected from " + before.channel.name)
            
            #If the number of people in the voice channel is 0
            if(inVoiceChannels == 0 and isBot == False):
                print(member.name + " is gay lol")
                await generalTextChannel.send(member.name + " is gay af :eggplant:")

client = MyClient()
client.run(jsonData['token']) #Calls the key from the config.json file
