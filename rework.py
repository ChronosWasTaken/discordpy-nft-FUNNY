#Awful awful code. such a fucking mess. Why the fuck are there so many returns with 0 instead of true?
import discord, asyncio
from discord.ext import commands
from time import sleep
import genning, db

bot = commands.Bot(command_prefix='$')
discorddb = db.DB("./db/build.db", "./db/build.sql")
helpful = "> [$balance](https://lmgtfy.app/?q=money&t=i) - Check your social standing\n> [$top10](https://lmgtfy.app/?q=cave+story+quote&t=i) - See who the richest members of Clang Clang Gang are"

#TODO: Is this really necessary?
async def nested_db(realbot, database):
    fullstring = ''
    count = 1
    for i in database:
        #Instead of smartly saving the first one from here I'd rather be stupid and do another call previous to this
        #Hurr durr
        realmember = await realbot.fetch_user(i[0])
        fullstring += f'{count}. {realmember.name} - ${i[1]:,.1f} USD\n'
        count += 1
    return fullstring

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Do '$help' for more info.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if genning.timelimitcheck():
        await bot.process_commands(message)
        return
    if discorddb.channelwhitelist(message.channel.id) == False:
        await bot.process_commands(message)
        return
    sleep(0.3)
    print(f'> {message.content}')
    

    #I'd rather use blacklists and do unnecesary checks for everything than actually think before I code. Hurr durr
    blacklist = []
    #Built-in Discord Attachments
    for item in message.attachments:
        if genning.blacklistcheck(item.url, blacklist) == 0:
            continue
        else:
            #FYI I'm keeping the whole price/embed shebang here because discord.py hates receiving embed items from outside an event.
            print('Embed - Attachment link')
            embed = discord.Embed()
            price, embed = genning.genembed(embed, item.url, message.author.name, message.id)
            await message.channel.send(embed=embed)
            discorddb.mixbalance(message.author.id,price)
            blacklist.append(item.url)
            continue
        
    #Built-in Discord Embeds
    #[!] If the client has embeds disabled client-side (?) or is posting an image it hasn't cached before (external sources)
    #it won't generate an embed for us.
    for item in message.embeds:
        if genning.blacklistcheck(item.url, blacklist) == 0:
            continue
        else:
            if item.image:
                print('Embed - Img link')
                embed = discord.Embed()
                price, embed = genning.genembed(embed, item.image.url, message.author.name, message.id)
                await message.channel.send(embed=embed)
                discorddb.mixbalance(message.author.id,price)
                blacklist.append(item.url)
                continue

            if item.thumbnail:
                print('Embed - Thumbnail link')
                embed = discord.Embed()
                price, embed = genning.genembed(embed, item.thumbnail.url, message.author.name, message.id)
                await message.channel.send(embed=embed)
                discorddb.mixbalance(message.author.id,price)
                blacklist.append(item.url)
                continue
        
    #Anything else
    url_matches = genning.compiled_url_regex.findall(message.content)
    for matches in url_matches: #regex returns tuples inside a dict because cringe regex is cringe
        single_url_match = matches[0]

        if genning.blacklistcheck(single_url_match, blacklist) == 0:
            continue

        #Direct links to images
        if (genning.compiled_format_regex.search(single_url_match)[0] != '') and (genning.checkurl(single_url_match) == 0): #My regex pattern is so shit, it returns matches even when there aren't any.
            print('Direct link')
            embed = discord.Embed()
            price, embed = genning.genembed(embed, single_url_match, message.author.name, message.id)
            await message.channel.send(embed=embed)
            discorddb.mixbalance(message.author.id,price)
            blacklist.append(single_url_match)
            continue
            

        #Boorus, run of the mill websites. Even Youtube
        if (genning.checkurl(single_url_match) == 0) and (og_image_url := genning.ogimagecheck(single_url_match)): #Right is only actually checked if left proves to be True
            print('Website link')
            embed = discord.Embed()
            price, embed = genning.genembed(embed, og_image_url, message.author.name, message.id)
            await message.channel.send(embed=embed)
            discorddb.mixbalance(message.author.id,price)
            blacklist.append(single_url_match)
            continue

        else:
            print('Unsupported or dead link')
            continue #Unsupported link

    print('End')
    await bot.process_commands(message)
    

    #Since we're calling the on_message event but with all our code in
    #the method for processing commands in the original class won't get to be ran?
    #I think.
    
    


@bot.command(name='genone',help="Test if the generators are working")
async def genone(ctx):
    qw = genning.fakegen(ctx.id)
    await ctx.send(f'{qw[0]}, {qw[1]}')

@bot.command(name='balance',help="Check your wallet")
async def balance(ctx):
    #Walrus for one-liner check "if db call returns not None"
    if (qw := discorddb.balanceof(ctx.author.id)):
        missingtime = genning.timelimitstring()
        embed=discord.Embed(title="Balance",description=f"There are currently:\n> ${qw:,.1f} USD `- in your wallet.`")
        embed.add_field(name="Useful Commands:", value=helpful, inline=False)
        embed.set_footer(text=f"{missingtime} left.")
        await ctx.send(embed=embed)
    else:
        missingtime = genning.timelimitstring()
        embed=discord.Embed(title="Balance",description=f"You don't have anything to your name!\nPost something for me to tokenize it first!")
        embed.add_field(name="Useful Commands:", value=helpful, inline=False)
        embed.set_footer(text=f"{missingtime} left.")
        await ctx.send(embed=embed)

@bot.command(name='portfolio',help="Check your wallet")
async def portfolio(ctx):
    await balance(ctx)

@bot.command(name='enable',help="Whitelist a channel for this bot to work on")
async def enable(ctx, arg1: discord.TextChannel):
    for item in ctx.author.roles:
        if item.name == 'Robot Overlord' or item.name == 'Mods' or item.name == 'Actually a Bot': #awful check for role
            if discorddb.addchannelwhitelist(arg1.id) == True:
                await ctx.send(f'Succesfully enabled bot on {arg1}')
            elif discorddb.addchannelwhitelist(arg1.id) == 'IE':
                await ctx.send(f'Bot already enabled on {arg1}')
            else:
                await ctx.send(f'Critical error! database may be corrupt')
            return 0
        else:
            continue

@bot.command(name='disable',help="Remove channel from the whitelist")
async def disable(ctx, arg1: discord.TextChannel):
    for item in ctx.author.roles:
        if item.name == 'Robot Overlord' or item.name == 'Mods' or item.name == 'Actually a Bot': #awful check for role
            if discorddb.delchannelwhitelist(arg1.id) == True:
                await ctx.send(f'Succesfully disabled bot on {arg1}')
            else:
                await ctx.send(f'Critical error! database may be corrupt')
            return 0
        else:
            continue
        

@bot.command(name='setbalance',help="Format is '$setbalance @USER AMOUNT'")
async def setbalance(ctx, arg1: discord.Member, arg2: float):
    for item in ctx.author.roles:
        if item.name == 'Robot Overlord' or item.name == 'Mods' or item.name == 'Actually a Bot':
            discorddb.updbalance(arg1.id, arg2)
            await ctx.send(f'Balance for {arg1.name} has been succesfully set to: {arg2}')
            return 0
        else:
            continue


@bot.command(name='deletebalance',help="Format is $deletebalance @USER")
async def deletebalance(ctx, arg1: discord.Member):
    for item in ctx.author.roles:
        if item.name == 'Robot Overlord' or item.name == 'Mods' or item.name == 'Actually a Bot':
            if discorddb.delbalance(arg1.id) == 0:
                await ctx.send(f"Succesfully sent {arg1.name}'s wallet to the shadow realm")
                return 0
            else:
                await ctx.send(f"Critical error! database may be corrupt")
                return 0
        else:
            continue

@bot.command(name='top10',help="See who the richest members of Clang Clang Gang are")
async def top10(ctx):
    qw = discorddb.top10() #Returns a list
    richestuser = await bot.fetch_user(qw[0][0])
    missingtime = genning.timelimitstring()

    embed=discord.Embed(title="Richest people in the world",description=await nested_db(bot, qw))
    embed.set_thumbnail(url=richestuser.avatar_url)
    embed.add_field(name="Useful Commands:", value=helpful, inline=False)
    embed.set_footer(text=f"{missingtime} left.")
    await ctx.send(embed=embed)

bot.run('ODIxNDczNjYwODUwMDEyMjAw.YFEO9g.IArUOPAEAyQuK7_nvwkYWUvaKxI')