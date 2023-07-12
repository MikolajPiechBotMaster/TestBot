from nextcord import Intents
from nextcord.ext import commands
import requests
import random
import json
import datetime
import asyncio
from PIL import Image, ImageFont, ImageDraw
import textwrap
from nextcord import File, ButtonStyle, Embed, Color
from nextcord.ui import Button, View
import nextcord
import os

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

links = json.load(open("gifs.json"))

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name="yo")
async def SendMesssage(ctx):
    await ctx.send("Wussap?")

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name="pic")
async def Dog(ctx):

    response = requests.get("https://dog.ceo/api/breeds/image/random")
    image_link = response.json()["message"]
    await ctx.send(image_link)

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name="gif", aliases=["feed", "play", "sleep"])
async def Gif(ctx):
    await ctx.send(random.choice(links[ctx.invoked_with]))

async def schedule_daily_message(h, m, s, msg, channelID):
    while True:
        now = datetime.datetime.now()
        then = now.replace(hour=h, minute=m, second=s)
        if then < now:
            then += datetime.timedelta(days=1)
        wait_time = (then-now).total_seconds()
        await asyncio.sleep(wait_time)

        channel = bot.get_channel(channelID)

        await channel.send(msg)
        await asyncio.sleep(1)

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name="daily")
async def daily(ctx, mystr:str, hour:int, minute:int, second:int = 0):

    if not (0 < hour < 24 and 0 <= minute <= 60 and 0 <= second < 60):
        raise commands.BadArgument()

    time = datetime.time(hour, minute, second)

    timestr = time.strftime("%I:%M:%S %p")
    await ctx.send(f"A daily message will be sent at {timestr} everyday in this channel.\nDaily message: \"{mystr}\"\nSay \"Ok\" to confirm.")
    try:
        msg = await bot.wait_for("message", timeout=60, check=lambda message : message.author == ctx.author)
    except asyncio.TimeoutError:
        await ctx.send("Not gonna wait that long!")
        return
    
    if (msg.content.lower() == "ok"):
        await ctx.send("Daily message has been set!")
        await schedule_daily_message(hour, minute, second, mystr, ctx.channel.id)
    else:
        await ctx.send("Daily message cancelled")

@daily.error
async def daily_error(ctx, error):
    if (isinstance(error, commands.BadArgument)):
        await ctx.send("""Incorrect format. Use !daily <message> <hour> <minute> <second>""")

def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name="meme")
async def meme(ctx, *args):
    msg = " ".join(args)
    font = ImageFont.truetype("Roboto-Regular.ttf", 15)
    img = Image.open("meme.jpg")
    x, y = (185.0, 62.5)
    
    lines = textwrap.wrap(msg, width=20)

    #w = img.width - (font.getbbox(msg)[0] + font.getbbox(msg)[1])
    #h = img.height - (font.getbbox(msg)[2] + font.getbbox(msg)[3])
    w,h = get_text_dimensions(msg, font)
    y_offset = (len(lines) * h) / 2
    y_text = y-(h/2) - y_offset

    for line in lines:
        draw = ImageDraw.Draw(img)
        #w = img.width - (font.getbbox(line)[0] + font.getbbox(line)[1])
        #h = img.height - (font.getbbox(line)[2] + font.getbbox(line)[3])
        w,h = get_text_dimensions(line, font)
        draw.text((x-(w/2), y_text), line, (0,0,0), font=font)
        img.save("memes/meme_edited.jpg")
        y_text += h


    with open("memes/meme_edited.jpg", "rb") as f:
        img = File(f)
        await ctx.channel.send(file=img)

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name="support")
async def support(ctx):
    hi = Button(label="click me", style=ButtonStyle.blurple)

    async def hi_callback(interaction):
        await interaction.response.send_message("Hello!")

    hi.callback = hi_callback

    myview = View(timeout=180)
    myview.add_item(hi)

    await ctx.send("Hi!", view=myview)

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name="video")
async def video(ctx, url, *args):
    myview = View()
    myview.add_item(Button(label="Watch Now", style=ButtonStyle.link, url=url))

    msg = " ".join(args)

    embed=Embed(title="New video on our channel!", description=msg, color=0xff0000)

    await ctx.send(embed=embed, view=myview)


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.event
async def on_command_error(ctx, error):
    if (isinstance(error, commands.CommandOnCooldown)):
        em = Embed(title="Slot down, bro!", description="Try again in {error.retry_after:.2f}s", color=Color.red())
        await ctx.send(embed=em)


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.event
async def on_ready():
    print(bot.user.name + " is ready to work!")

if __name__ == '__main__':
    bot.run(os.environ["DISCORD_TOKEN"])