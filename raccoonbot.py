import discord
from discord.ext import commands, tasks
from itertools import cycle
import json
import os
import random
import yfinance
import math
import time

help_command = commands.DefaultHelpCommand(no_category = 'Commands')
client = commands.Bot(command_prefix = '!', help_command=help_command)

raccoon_status = cycle(["Inside a Garbage Can", "With a Stick", "On a Pile of Garbage", "With a Garbage Can", "In the Landfill"])

serveropened = open('server.json', 'r')
data = json.loads(serveropened.read())



'''
BOT EVENTS 
'''
@client.event
async def on_ready():
    change_status.start()
    # await client.change_presence(status=discord.Status.online, activity=discord.Game("Inside Garbage Can"))
    print('Logged in as {0.user} successfully'.format(client))


#Audit Log -> On Message Delete, send message to the private audit log channel.
@client.event
async def on_message_delete(message):
    #Gathers the content of the deleted message
    channel = client.get_channel(data['channels']['audit'])
    embed = discord.Embed(title = "Message Deleted", color = discord.Colour.red())
    embed.add_field(name=f'Sent By: {message.author}', value = f'Channel: #{message.channel} \n Message: "{message.content}"')
    #await channel.send(f'```MESSAGE DELETED IN #{message.channel}: \n{message.author}: {message.content}```')
    await channel.send(embed = embed)

#On User Join, Greet the user
# @client.event
# async def on_


'''
BOT COMMANDS
'''

#ctx.channel.guild.channels -> list of all channels in the server


#Set Channels
@client.command(help = "Set Channels")
@commands.has_permissions(administrator=True)
async def set(ctx, designator: str):
    keysArray = []
    if (designator.lower() in data['channels']):
        #await ctx.send(ctx.channel.id)

        data['channels'][designator] = ctx.channel.id
        with open('server.json', 'w') as outfile:
            json.dump(data, outfile)

        await ctx.send(f"This channel (#{ctx.channel.name}) has been set as the {designator} channel")
        return

    for key in data['channels']:
        keysArray.append(key)

    await ctx.send(f"Supported designators are: {keysArray}")



#List Emojis
# @client.command(help = "List Emojis")
# async def emojis(ctx):
#     await ctx.send(ctx.channel.guild.emojis)

#Send back the ping
@client.command(help = "Return the ping time")
async def ping(ctx):
    if (ctx.channel.id == data['channels']['commands']):
        await ctx.send(f'Pong! {round(client.latency*1000)} ms')

#8ball
@client.command(aliases = ['8ball'], help = "Alias: 8Ball - 8Ball replies")
async def _8ball(ctx, *, question):
    if (ctx.channel.id == data['channels']['commands'] or ctx.channel.id == data['channels']['games']):
        possible_responses = ["It is certain.","It is decidedly so.","Without a doubt.","Yes - definitely.","You may rely on it.","As I see it, yes.","Most likely.","Outlook good.","Yes.","Signs point to yes.","Reply hazy, try.","Ask again later.","Better not tell you now.","Cannot predict now.","Concentrate and ask again.","Don't count on it.","My reply is no.","My sources say no.","Outlook not so good.","Very doubtful."]
        await ctx.send(random.choice(possible_responses))
#8ball bot error handling
@_8ball.error
async def _8ball_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("I cannot predict nothing")


#prune a certain number of messages
@client.command(help = "Prune a given number of messages")
@commands.has_permissions(manage_messages=True) # Ensure that the user using this command actually has permission to remove messages.
async def prune(ctx, *, amount: int):
    delete_count = await ctx.channel.purge(limit = (amount+1))
    if (amount == 1):
        await ctx.send(f"{amount} message has been removed", delete_after=5)
    else:
        await ctx.send(f"{amount} messages have been removed", delete_after=5)
#Prune error handling, if no message count is given
@prune.error
async def prune_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter the amount of messages to prune")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command")


#Relaxation/Meditation Command to join the channel and play meditation stuff. If no one in channel for like 5 minutes, then leave the channel.
# @client.command()
# async def meditate(ctx):
#     if not ctx.message.author.voice:
#         await ctx.send("You are not connected to the meditation channel")
#         return
#     # elif (ctx.message.author.voice != 845379944300150854):
#     #     await ctx.send("Please connect to the Meditation Tree")
#     #     return
#     else:
#         meditate_channel = ctx.message.author.voice.channel
#     await meditate_channel.connect()

# @client.command()
# async def leave(ctx):
#     voice_client = ctx.message.guild.voice_client
#     await voice_client.disconnect()

# @client.command()
# async def leave(ctx):


# @client.commands(aliases=['bj'])
# async def blackjack(ctx):



# #Raccoon Images Command
#  WIP


#Stock
@client.command(help = "Enter a ticker following the command prefix. Example: !stock GME")
async def stock(ctx, *, ticker: str):
    if (ctx.channel.id == data['channels']['stocks']):
        time_start = time.time()
        input_stock = yfinance.Ticker(ticker)
        stock_logo = input_stock.info['logo_url']
        stock_name = input_stock.info['longName']
        stock_symbol = input_stock.info['symbol']
        stock_price = input_stock.info['regularMarketPrice']
        stock_previous_close = input_stock.info['previousClose']
        stock_open = input_stock.info['open']
        stock_day_low = input_stock.info['dayLow']
        stock_day_high = input_stock.info['dayHigh']
        stock_volume = input_stock.info['volume']
        stock_float = input_stock.info['floatShares']
        stock_last_dividend_value = input_stock.info['lastDividendValue']

        calculated_percentage = (stock_price-stock_previous_close)/(stock_previous_close)*100
        rounded_number =  round(calculated_percentage, 4 - int(math.floor(math.log10(abs(calculated_percentage)))) - 1)
        
        embed = discord.Embed(title=f'{stock_name} - [${stock_symbol}]', description = f'${stock_symbol}', color=discord.Colour.blue())
        embed.add_field(name='Opening Price:', value=f"$ {stock_open}", inline=True)
        embed.add_field(name='Current Price:', value=f"$ {stock_price}", inline=True)
        embed.add_field(name='Previous Close:', value=f"$ {stock_previous_close}",inline=True)
        embed.add_field(name='Percentage Change:', value=f'{rounded_number}%')
        embed.add_field(name="Day High:", value=f"$ {stock_day_high}", inline=True)
        embed.add_field(name="Day Low:", value=f"$ {stock_day_low}", inline=True)

        # embed.add_field(name="Dividend Value", value=f"$ {stock_last_dividend_value}", inline=True)
        # embed.add_field(name="Volume", value=f"{stock_volume}", inline=False)
        # embed.add_field(name="Float", value=f"{stock_float}", inline=False)

        embed.set_thumbnail(url=stock_logo)
        time_end = time.time()
        time_elapsed = time_end - time_start
        rounded_time = round(time_elapsed, 3 - int(math.floor(math.log10(abs(time_elapsed)))) - 1)
        embed.set_footer(text=f'Command processed in {rounded_time} seconds')
        await ctx.send(embed=embed)

@stock.error
async def stock_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a valid ticker")


@client.command(aliases = ['qv'], help = "Quick view multiple stocks")
async def quickview(ctx, *, ticker):
    if (ctx.channel.id == data['channels']['stocks']):
        time_start = time.time()
        ticker_list = ticker.upper().split()
        embed = discord.Embed(title="Stock Comparison", description=f"Comparison of ${', $'.join(ticker_list)}", color=discord.Colour.blue())

        for i in ticker_list:
            input_stock = yfinance.Ticker(str(i))

            stock_symbol = input_stock.info['symbol']
            stock_price = input_stock.info['regularMarketPrice']
            stock_previous_close = input_stock.info['previousClose']

            calculated_percentage = (stock_price-stock_previous_close)/(stock_previous_close)*100
            rounded_number =  round(calculated_percentage, 4 - int(math.floor(math.log10(abs(calculated_percentage)))) - 1)

            embed.add_field(name=f"${stock_symbol} \nCurrent Price: ${stock_price}", value = f'Previous Close: ${stock_previous_close} \nPercent Change: {rounded_number}%', inline=False)
        time_end = time.time()
        time_elapsed = time_end - time_start
        rounded_time = round(time_elapsed, 3 - int(math.floor(math.log10(abs(time_elapsed)))) - 1)
        embed.set_footer(text=f'Command processed in {rounded_time} seconds')
        await ctx.send(embed=embed)

@quickview.error
async def quickview_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter stocks to compare")


@client.command(aliases = ['ss'])
async def stocksummary(ctx, *, ticker:str):
    if (ctx.channel.id == data['channels']['stocks']):
        input_stock = yfinance.Ticker(ticker)
        stock_description = input_stock.info['longBusinessSummary']
        stock_symbol = input_stock.info['symbol']
        await ctx.send(f'**Business Summary of ${stock_symbol}**: \n{stock_description}')

@stocksummary.error
async def stocksummary_error(ctx, error):
    if isinstance(error, commands.missingRequiredArgument):
        await ctx.send("Please enter a valid ticker")



#random number from 1 to user input 
@client.command(help = "Enter an upper bound, then a random value between 1 and the upper bound will be selected")
async def roll(ctx, *, given_range: int):
    random_selection = random.randrange(1,given_range)
    await ctx.send(random_selection)

@roll.error
async def roll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a value")



'''
Loops/Background Events
'''
@tasks.loop(seconds = 3600)
async def change_status():
    await client.change_presence(activity=discord.Game(next(raccoon_status)))






'''
Error Handling
'''
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("This command does not exist. Please try again")



client.run(os.getenv('TOKEN'))