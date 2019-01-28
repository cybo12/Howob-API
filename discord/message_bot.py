import logging
import time
import asyncio
import json
import datetime
import aiohttp
import discord
import os
from mq import mq
# LOGGING PART

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

endpoint = 'https://XX/api'
TOKEN = 'TOKEN'


class MyClient(discord.Client):
    async def on_ready(self):
        game = discord.Game("Howob")
        await client.change_presence(activity=game)
        print('howob bot ready')
        print(discord.__version__)
        ch = client.get_channel(519192291794223107)
        await ch.purge(limit=600)
        payload = """```md\n# !perso {account_name} {player_name}\nGive you characther's infomation (it's case sensitive) ``` ```md\n# !status \nGive you the server's status and overall latence with howob and RTS's server```"""
        await ch.send(payload)
        await self.get_from_howob()

    async def on_message(self, message):
        base = ""
        if message.author != client.user and message.channel.id == 519192291794223107:
            split = message.content.split(" ")
            if split[0] == '!perso':
                await self.des(message.channel, split[1], split[2])
            elif split[0] == '!status':
                await self.status(message.channel)
            elif split[0] == '!help':
                payload = """```md\n# !perso {account_name} {player_name}\nGive you characther's infomation (it's case sensitive) ``` ```md\n# !status \nGive you the server's status and overall latence with howob and RTS's server```"""
                await message.channel.send(payload)
            else:
                if message.attachments:
                    base = message.attachments[0].url
                payload = {
                    "user_name": message.author.name,
                    "message": message.content,
                    "date_time": int(time.mktime(message.created_at.timetuple())),
                    "important": False,
                    "from": "Discord",
                    "image_url": base
                }
                print(payload)
                async with aiohttp.ClientSession() as cs:
                    async with cs.post(f'{endpoint}/messages', json=payload) as r:
                        print(r.status)

    async def send_message(self, payload):
        ch = client.get_channel(519192291794223107)
        payload = json.loads(payload.decode('utf-8'))
        payload['date_time'] = datetime.datetime.fromtimestamp(
            int(payload['date_time']))
        if payload['from'] == "RTS":
            embed = discord.Embed(title=payload['user_name'], description=payload['message'], color=0xff002e,
                                  timestamp=payload['date_time'])
            embed.set_thumbnail(
                url="https://XX/cdn/rts.png")
        else:
            embed = discord.Embed(title=payload['user_name'], description=payload['message'], color=0x415fd8,
                                  timestamp=payload['date_time'])
            embed.set_thumbnail(
                url="https://XX/cdn/mmo.png")
        embed.set_author(name=payload['from'])
        await ch.send(embed=embed)

    async def get_from_howob(self):
        while True:
            await asyncio.sleep(0.5)
            method_frame, header_frame, body = mq.get_channel().basic_get(
                'discord')
            if method_frame:
                mq.get_channel().basic_ack(method_frame.delivery_tag)
                await self.send_message(body)

    async def des(self, channel, name, npc_name):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'{endpoint}/discord/{name}/{npc_name}') as r:
                res = await r.json()
                if 'message' in res:
                    await channel.send(res['message'])
                else:
                    description = f'**{res["classe_name"]}**\n\n'
                    description = description + f'**Level :** {res["character_level"]}\n'
                    description = description + f'**Life :** {res["character_life"]}/{res["character_max_life"]}\n'
                    description = description + f'**Mana :** {res["character_mana"]}/{res["character_max_mana"]}\n'
                    description = description + f'**Gold :** {res["character_nb_gold"]}\n'
                    embed = discord.Embed(
                        title=res["character_name"], color=0x415fd8, description=description)
                    embed.set_author(name=f'{res["account_name"]}')
                    cdn_search = res["classe_name"].lower() + ".png"
                    if ' ' in cdn_search:
                        cdn_search = cdn_search.replace(" ", "_")
                    embed.set_thumbnail(
                        url=f'https://XX/cdn/{cdn_search}')
                    print(embed.to_dict())
                    await channel.send(embed=embed)

    async def status(self, channel):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'{endpoint}/system') as r:
                res = await r.json()
                print(res)
                print(res["latency"]["Howob"])
                if 'message' in res:
                    await channel.send(res['message'])
                else:
                    if(res["latency"]["Howob"] != "unreachable"):
                        author = "Howob is running :)"
                        description = f'**Uptime :** {res["utc_time"]}\n'
                        description = description + f'**Latency Howob:** {res["latency"]["Howob"]}\n'
                        description = description + f'**Latency RTS:** {res["latency"]["Boomcraft"]}\n'
                        description = description + f'**Nb players :** {res["nbr_players"]}\n'
                        description = description + f'**Nb quests :** {res["nbr_quests"]}\n'
                    else:
                        description = ""
                        author = f"Howob is down :'("
                    embed = discord.Embed(
                        title=author, color=0x415fd8, description=description)
                    embed.set_author(name="Howob server's status")
                    cdn_search = "mmo.png"
                    embed.set_thumbnail(
                        url=f'https://XX/cdn/{cdn_search}')
                    await channel.send(embed=embed)


client = MyClient()
client.run(TOKEN)
