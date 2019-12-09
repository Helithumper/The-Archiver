import discord 
from datetime import datetime, timezone
import os

async def send_help_message(channel):
    embed = discord.Embed(title="Archiver Help")
    embed.color = discord.Colour.dark_blue()
    embed.description = """I can handle archiving channels and categories!
    Commands:
```!archive category [name] -- Archives an entire category
!archive channel {category/}[name] -- Archives an entire channel
!archive all -- Archives all channels by category```"""
    await channel.send(embed=embed)

async def archive_category(category_name, channel):
    categories = channel.guild.categories
    matching_categories = list(filter(lambda x: x.name.lower() == category_name.lower(), categories))

    if len(matching_categories) == 0:
        await channel.send('No Matching Categories')
        return
    
    for matching in matching_categories:
        await channel.send(f'\t**{matching.name}**')
        await channel.send(f'Archiving {len(matching.channels)} channels')
        for i, child_channel in enumerate(matching.channels):
            await channel.send(f'({i+1}/{len(matching.channels)}) Archiving *{child_channel.name}*')
            await archive_channel(child_channel)

def parse_channel_name(input_message):
    tokens = input_message.split('/')
    if len(tokens) > 1:
        return tokens[1], tokens[0]
    else:
        return tokens[0], None
async def handle_message(message):
    # Determine which command this message is attempting
    channel = message.channel
    category = message.channel.category_id

    if '!archive' not in message.content:
        return
    
    tokens = message.content.split(' ')[1:]

    if tokens[0] == 'help':
        await send_help_message(channel)
        return 
    
    if tokens[0] == 'channel':
        channel_name, category_name = parse_channel_name(tokens[1])
        channels = channel.guild.channels
        if category_name:
            matching_channels = list(filter(
                lambda x: x.name == channel_name and x.category == category_name
                , channels))
        else:
            matching_channels = list(filter(
                lambda x: x.name == channel_name and x.category == None
                , channels))

        if len(matching_channels) == 0:
            await channel.send('No Matching Channels')
            return
        
        await channel.send('Maching Channels:')
        ##TODO: check for category name. Category must be specified for categorized channels
        for matching in matching_channels:
            if matching.category != None:
                await channel.send(f'\tArchiving *{matching.category.name}/{matching.name}*')
            else:
                await channel.send(f"\tArchiving *{matching.name}*")
            await archive_channel(matching)
        await channel.send("**Archival Complete**")
    
    if tokens[0] == 'category':
        category_name = tokens[1]
        await archive_category(category_name, channel)
        await channel.send("**Archival Complete**")
    
    if tokens[0] == 'all':
        categories = channel.guild.categories
        for category_match in categories:
            await archive_category(category_match.name, channel)
        return
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