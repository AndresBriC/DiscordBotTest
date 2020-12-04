import discord
import json

configJsonFile = open('config.json')
jsonData = json.load(configJsonFile)
prefix = jsonData['prefix'] #Reference to the prefix stated in the config.json
intents = discord.Intents(voice_states = True)


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

        #Prints users in General text channel
        elif lowerCaseMessage == (prefix + "usersinchannel"):
            channel = client.get_channel(273224026464452608)
            members = channel.members
            memnicks = []

            for member in members:
                memnicks.append(member.name)

            await message.channel.send(memnicks)

    async def on_voice_state_update(self, member, before, after):

        #global membersInChannelCounter

        if before.channel is None and after.channel is not None:
            print(member.name + " joined voice channel")
            #membersInChannelCounter = membersInChannelCounter+1
            #print("Users in voice channels: " + str(membersInChannelCounter))

        if before.channel is not None and after.channel is None:
            print(member.name + " disconnected from voice channel")
            #membersInChannelCounter = membersInChannelCounter+1
            #print("Users in voice channels: " + str(membersInChannelCounter))

client = MyClient()
client.run(jsonData['token']) #Calls the key from the config.json file
