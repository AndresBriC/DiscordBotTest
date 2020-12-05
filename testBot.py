import discord
import json

configJsonFile = open('config.json')
jsonData = json.load(configJsonFile)
prefix = jsonData['prefix'] #Reference to the prefix stated in the config.json
intents = discord.Intents(voice_states = True, members = True) #Specifies intents

#Ideas:
#Contador de días desde ultima salida a San Mike, Alexa play Despacito

class MyClient(discord.Client):

    #Prints to console when ready
    async def on_ready(self):
        print('We have logged in as ' + self.user.name + " " + str(self.user.id))

    async def on_message(self, message):
        #Prevents bot from replying to itself
        if message.author.id == self.user.id:
            return

        #Greeting message
        lowerCaseMessage = message.content.lower() #Transforms message to lowrcase
        if lowerCaseMessage == (prefix + "hello") or lowerCaseMessage == (prefix + "hi"): #Compares the lowercase version of the message
            await message.channel.send("Hello " + message.author.name)

    async def on_voice_state_update(self, member, before, after):
        #channel = client.get_channel(747620441916571765) #Gets the channel, given the ID
        generalTextChannel = discord.utils.get(member.guild.channels, name = 'general') #Looks for text channel named general

        #global membersInChannelCounter

        if before.channel is None and after.channel is not None:
            afterChannel = client.get_channel(after.channel.id)
            members = afterChannel.members #Gets all members in the selected voice channel
            memNames = [] #To store all members
            for person in members: #Appends each member to the array
                #print(person.name)
                memNames.append(person.name)   
            print(memNames)
            print(member.name + " joined a voice channel")

        if before.channel is not None and after.channel is None:
            beforeChannel = client.get_channel(before.channel.id)
            members = beforeChannel.members #Gets all members in the selected voice channel
            memNames = [] #To store all members
            for person in members: #Appends each member to the array
                #print(person.name)
                memNames.append(person.name)           
            print(memNames)
            print(member.name + " disconnected from a voice channel")
            await generalTextChannel.send(member.name + " disconnected from " + before.channel.name)
            if(len(memNames) == 0): #If the number of people in the voice channel is 0
                print(member.name + " is gay lol")
                await generalTextChannel.send(member.name + " is gay af :eggplant:")

client = MyClient()
client.run(jsonData['token']) #Calls the key from the config.json file
