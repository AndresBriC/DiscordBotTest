import discord
import json

client = discord.Client()

configJsonFile = open('config.json')
jsonData = json.load(configJsonFile)
prefix = jsonData['prefix'] #Reference to the prefix stated in the config.json
intents = discord.Intents(voice_states = True)

#Prints to console when ready
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    lowerCaseMessage = message.content.lower()
    if lowerCaseMessage == (prefix + "hello") or lowerCaseMessage == (prefix + "hi"):
        await message.channel.send("Hellou!")
    elif lowerCaseMessage == (prefix + "usersinchannel"):
        channel = client.get_channel(273224026464452608)
        members = channel.members
        memnicks = []

        for member in members:
            memnicks.append(member.name)

        await message.channel.send(memnicks)

def getCurrentUsersInVoiceChannel()

@client.event
async def on_voice_state_update(member, before, after):

    #global membersInChannelCounter

    if before.channel is None and after.channel is not None:
        print(member.name + " joined voice channel")
        #membersInChannelCounter = membersInChannelCounter+1
        #print("Users in voice channels: " + str(membersInChannelCounter))

    if before.channel is not None and after.channel is None:
        print(member.name + " disconnected from voice channel")
        #membersInChannelCounter = membersInChannelCounter+1
        #print("Users in voice channels: " + str(membersInChannelCounter))

client.run(jsonData['token']) #Calls the key from the config.json file
