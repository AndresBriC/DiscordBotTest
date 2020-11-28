import discord
import json

client = discord.Client()

configJsonFile = open('config.json')
jsonData = json.load(configJsonFile)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(jsonData['token']) #Referenciar la key
