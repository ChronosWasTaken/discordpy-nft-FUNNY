#Tests passed:
# Dupes
# Normal Twitter post
# Normal Twitter gif/vid
# Normal Single direct img
# Normal Attachment
# Attachment + Any
# Multiple requests (sleep(0.3) to avoid ratelimit)

#Should fix:
# Multiple attachments
# Ignoring urls when going over the discord cap (4)

#Big wall of TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO: Rewrite the whole project in OOP format
#TODO: Use discord.ext instead of discord.client
#TODO: Hard check for date, stop making tokens after 2nd of April, 12AM GMT-6 - CST
#FUCK DATETIME ALL MY NIGGAS HATE DATETIME
#FUCK PYTZ ALL MY NIGGAS HATE PYTZ
#WHAT THE FUCK IS WITH ALL THE IMPORTS JUST TO GET THE LOCAL TIME THAT ISN'T YOURS DUDE

import db
from time import sleep
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import discord, random, requests, re
client = discord.Client()

#pic_ext = ['.jpg','.png','.jpeg', '.jfif', '.webm', '.mp4']
pic_ext = re.compile(r"(\.png)?(\.jpe?g)?(\.jfif)?(\.mp4)?(\.webm)?(\?width=\d+\&height=\d+)?$")
noyt = re.compile(r"((youtube\.com)?(youtu\.be)?(www\.youtube\.com)?(m\.youtube\.com)?(www\.youtu\.be)?)")
allchances = (5, 15, 35, 65, 100)
allpicks = [(100000,10000001) , (10000,100001), (1000,10001), (100,1001), (0,101)] 
#alternatively, r"(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))"
elregexo = re.compile(r"(https?:\/\/([a-z0-9]+\.)?[a-z0-9]+\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)*)", re.IGNORECASE)

#this is a lot of cringe but it should only run and hog a thread for 300 msec or less when it actually is run
#i honest to god hope nobody tries to abuse the fuck out of this thing by spamming links otherwise my pc is done for

def theballadofihaventfuckingslept(discordmsgid):
    #generate fake eth wallet starting with hex converted message id as """easter egg"""
    hexdisc = hex(discordmsgid)
    hexdisc = hexdisc+('%027x' % random.randrange(16**27)) #7 usec per loop! massive waste of resources!

    if len(hexdisc) != 42:
        #hexdisc too long, bollocks
        hexdisc = hexdisc[:42]
    
    range_min, range_max = random.choices(allpicks, cum_weights=allchances)[0]
    return hexdisc, random.randrange(range_min, range_max)+(random.randint(0,9)/10)

def genembed(trueembed, thumb, author, msgid):
    """Function that doesn't do all the work
    Arguments:
        trueembed {discord.Embed}
        thumb {message.content, message.attachments[0].url, message.embeds[0].image.url, message.embeds[0].thumbnail.url}
        author {message.author.name}
        msgid {message.id}
    
    Returns:
        Discord Embed
    """
    tokenstring, moneystring = theballadofihaventfuckingslept(msgid)
    date = datetime.utcnow(timezone.cst).strftime("%Y-%m-%d %I:%M %p")
    trueembed.set_author(name="Discord Tokenizer", icon_url="https://cdn.discordapp.com/attachments/821581008544858113/821789524928626718/quotecoin.png")
    trueembed.set_thumbnail(url=thumb) 
    trueembed.add_field(name=f"Token Value: {tokenstring}", value=f"Priced at: ${moneystring} USD", inline=False)
    trueembed.set_footer(text=f"Owned by {author} | Minted at {date}")
    return trueembed

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    sleep(0.3)
    print(f'> {message.content}')
    if message.author == client.user:
        print('Message posted by us, ignoring')
        return
    if message.content.lower() == '$balance':  
        return
    if message.content.lower() == '$top10':
        return


    #do the funny NFT 
    #this is all running on every message so it's probably incredibly fucking slow
    #actually not really since we're ratelimited by discord anyway

    
    nail = []

    print(f'< Attachments: {message.attachments}')
    #check if message has an img attached to it
    #what's the point of this check if if it's empty it's just gonna skip over it anyway?
    if message.attachments:
        for i in message.attachments:
            die = 0
            for item in nail:
                if item == i.url:
                    die = 1
            if die == 1:
                continue

            print(f'[Ath] {i.url}')
            
            embed=discord.Embed()
            #discord for desktop only lets you attach max one image at a time
            await message.channel.send(embed=genembed(embed,i.url, message.author.name, message.id))
            #no return because if we have an attachment and a url 
            #we want to embed the others as well
            nail.append(i.url)


    #check if Twitter, html url with discord embed or single direct url image
    #print embeds for debug purposes
    print(f'< Embeds: {message.embeds}')
    #I feel this is a dumb way to go around it. 
    #Ifs inside the for loop? when we could have the if checks before entering a loop? eh
    for i in message.embeds:
        die = 0
        #Twitter img post
        if i.image:
            print(f'[Twt] {i.url}')
            
            embed=discord.Embed()
            await message.channel.send(embed=genembed(embed,i.image.url,message.author.name,message.id))
            nail.append(i.url)
            continue

        #check if already posted
        #useful in ignoring duplicates or twitter image posts (which for some reason have both i.image and i.thumbnail attribs)
        #TODO: embeds cap at 4 though?
        for item in nail:
            if item == i.url:
                die = 1
        if die == 1:
            continue

        #anything else
        if i.thumbnail:
            print(f'[TwtMed] {i.url}')
            
            embed=discord.Embed()
            await message.channel.send(embed=genembed(embed,i.thumbnail.url,message.author.name,message.id))
            nail.append(i.url)


    #check if message body includes url to image
    #~1.3 usec per loop. probably nothing to worry about
    print(f'< Blacklist: {nail}')
    regigix = elregexo.findall(message.content) #check if URL
    for regitem in regigix: #Regex returns dict because cringe regex is cringe
        die = 0
        for item in nail:
            #if item is in blacklist
            #ignore and go to the next one duh
            if item == regitem[0]:
                die = 1
        if die == 1:
            print('Url -> Ignoring URL')
            #retarded hack because i can't continue the top loop from the nested one
            continue

        print(f'[Url] {regitem[0]}')
        #if it fits our dumb format criteria
        try:
            #yt gets picked up by twtvid but since the link is different it doesn't get into the nails list
            #so, we use a redundant regex as a fast for me, slow for compiutor copout
            if (noyt.search(regitem[0]) == None) or (noyt.search(regitem[0])[0] == ''):
                print('Not a YT link')
                #lots of "try" loops because requests is retarded and doesn't return None on fail
                #literally cringiest shit ever
                try:
                    requests.head(regitem[0])
                    print("site poke!")
                    #just a lil check at this point to be sure
                    try:
                        letsgetit = requests.get(regitem[0])
                        letsgetit = BeautifulSoup(letsgetit.content, 'html.parser')
                        nr = letsgetit.find("meta", property="og:image")['content']
                        print('OG:IMAGE EMBED')
                        embed=discord.Embed()
                        await message.channel.send(embed=genembed(embed, nr, message.author.name, message.id))
                        nail.append(regitem[0])
                    except:
                        if (pic_ext.search(regitem[0]) != None) or (pic_ext.search(regitem[0]) == ''):
                            print('Not a compatible site or IMG')
                        else:
                            print('DIRECT EMBED')
                            embed=discord.Embed()
                            await message.channel.send(embed=genembed(embed, regitem[0], message.author.name, message.id))
                            nail.append(regitem[0])
                except:
                    print("can't connect to site!")
                    #if url ends with format
                    #but we can't connect
                    #end loop, get to next url
                    break
        except:
            #skip url if it doesn't fit conditions
            pass
    print('End')

try:
    client.run('ODIxNDczNjYwODUwMDEyMjAw.YFEO9g.IArUOPAEAyQuK7_nvwkYWUvaKxI')
except KeyboardInterrupt:
    print('KILLED!')
    db.close()