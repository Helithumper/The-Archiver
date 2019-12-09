import discord 
from datetime import datetime, timezone
import os

async def handle_message(message):
    # Determine which command this message is attempting
    channel = message.channel
    category = message.channel.category_id

    if '!archive' not in message.content:
        return
    
    tokens = message.content.split(' ')[1:]

    if tokens[0] == 'help':
        await channel.send('I can handle archiving channels and categories!')
        await channel.send(f"""Commands:\n```!archive category [name] -- Archives an entire category\n!archive channel [name] -- Archives an entire channel```""")
        return 
    
    if tokens[0] == 'channel':
        channel_name = tokens[1]
        channels = channel.guild.channels
        matching_channels = list(filter(lambda x: x.name == channel_name, channels))

        if len(matching_channels) == 0:
            await channel.send('No Matching Channels')
            return
        

        await channel.send('Maching Channels:')
        for matching in matching_channels:
            if matching.category != None:
                await channel.send(f'\tArchiving *{matching.category.name}/{matching.name}*')
            else:
                await channel.send(f"\tArchiving *{matching.name}*")
            await archive_channel(matching)
    
    if tokens[0] == 'category':
        category_name = tokens[1]
        categories = channel.guild.categories
        matching_categories = list(filter(lambda x: x.name.lower() == category_name.lower(), categories))

        if len(matching_categories) == 0:
            await channel.send('No Matching Categories')
            return
        
        await channel.send('Matching Categories:')
        for matching in matching_categories:
            await channel.send(f'\t**{matching.name}**')
            for child_channel in matching.channels:
                await channel.send(f'\tArchiving *{child_channel.name}*')
                await archive_channel(child_channel)
    
    else:
        await channel.send("Unknown command")


async def archive_channel(channel):
    # Archives a given channel
    if channel.type != discord.ChannelType.text:
        return
    messages = await channel.history(limit=None, oldest_first=True).flatten()
    now = datetime.now(timezone.utc)
    archive_path = './archive/'
    if channel.category:
        name = f"{channel.category.name}"
        try:
            os.mkdir(f'./archive/{name}')
        except FileExistsError:
            pass
        archive_path = archive_path+f'{name}/'
        name = f"{channel.category.name}-{channel.name}"
    else:
        name = f"{channel.name}"

    try:
        os.mkdir(f'{archive_path}/{name}')
    except FileExistsError:
        pass

    f = open(f'{archive_path}/{name}/message-log.txt', 'a')
    for message in messages:
        if message.attachments != []:
            for attach in message.attachments:
                await attach.save(f'{archive_path}/{name}/{attach.filename}')
        f.write(f"{message.created_at} [{message.author.name}]: {message.content}\n")
    f.close()
    return

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        if message.author.bot:
            print(f'Ignoring message from {message.author.name} as they are a bot.')
            return
        message_type = await handle_message(message)

client = MyClient()
client.run(os.getenv('DISCORD_TOKEN'))