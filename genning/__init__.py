from bs4 import BeautifulSoup
from random import randrange, choices, randint
from datetime import datetime
from pytz import timezone
import re, requests

allchances = (5, 15, 35, 65, 100)
allpicks = [(100000,10000001) , (10000,100001), (1000,10001), (100,1001), (0,101)] 
cstimezone = timezone("CST6CDT")
compiled_yt_regex = re.compile(r"youtu\.?be(?:\.com)?(?:\/watch\?v=)([-0-z]*)")
compiled_url_regex = re.compile(r"(https?:\/\/([a-z0-9]+\.)?[a-z0-9]+\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)*)", re.IGNORECASE)
compiled_format_regex = re.compile(r"(\.png)?(\.jpe?g)?(\.jfif)?(\.gif)?(\.mp4)?(\.webm)?(\?width=\d+\&height=\d+)?$")

crawlheaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
}

def fakegen(discordmsgid):
    #generate fake eth wallet starting with hex converted message id as """easter egg"""
    hexdisc = hex(discordmsgid)
    hexdisc = hexdisc+('%027x' % randrange(16**27)) #7 usec per loop! massive waste of resources!

    if len(hexdisc) != 42:
        #hexdisc too long, bollocks
        hexdisc = hexdisc[:42]
    
    range_min, range_max = choices(allpicks, cum_weights=allchances)[0]
    return hexdisc, randrange(range_min, range_max)+(randint(0,9)/10)

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
    missingtime = timelimitstring()
    tokenstring, moneystring = fakegen(msgid)
    date = datetime.now(cstimezone).strftime("%Y-%m-%d %I:%M %p")
    trueembed.set_author(name="Discord Tokenizer", icon_url="https://cdn.discordapp.com/attachments/821581008544858113/821789524928626718/quotecoin.png")
    trueembed.set_thumbnail(url=thumb) 
    trueembed.add_field(name=f"Token Value: {tokenstring}", value=f"Priced at: ${moneystring:,.1f} USD, which have been added to your portfolio.", inline=False)
    trueembed.set_footer(text=f"Owned by {author} | Minted at {date} | {missingtime} left.")
    return moneystring, trueembed

def blacklistcheck(url, blacklist):
    for item in blacklist:
        #if both are same
        if url == item:
            return 0        
        #if both are yt
        #won't match if youtube.com, but will if youtube.com/watch?v=
        if compiled_yt_regex.search(item) is not None and compiled_yt_regex.search(url) is not None:
            #if both have the same watch id
            if compiled_yt_regex.search(url)[1] and compiled_yt_regex.search(item)[1]: # [0] youtube.com/watch?v= [1] urEDLQsEnlI
                return 0
    return None


def ogimagecheck(url):
    try:
        print('OGIMAGECHECK')
        html = requests.get(url, headers=crawlheaders).content #requests.get follows redirects by default
        htmlparsed = BeautifulSoup(html, 'html.parser')
        og_image_url = htmlparsed.find("meta", property="og:image")['content'] #Exception: TypeError: 'NoneType' object is not subscriptable
        return og_image_url
    except:
        return None

    """
    except TypeError: 
        print('Failed to find og:image meta property')
        return None
    except requests.exceptions.ConnectionError: #requests.exceptions.ConnectionError
        print('Failed to connect')
        return None #URL does not exist
    """

def checkurl(url):
    print('URL CHECK')
    if requests.head(url, headers=crawlheaders).status_code <= 399: #Response codes over 400 indicate Client & Server errors
        return 0
    else:
        return None

def timelimitstring(): #Why are there so many date and time modules? searching for SU examples for this stuff is such a pain.
    __datenow = datetime.now(cstimezone)
    __finaldate = datetime(2021, 4, 2, 0, 0)
    __tilldate = cstimezone.localize(__finaldate) - __datenow
    __hrs, __r = divmod(__tilldate.total_seconds(), 3600)
    __min, __secs = divmod(__r, 60)
    __days, __hrs = divmod(__hrs, 24)
    return f'{__days:g}d {__hrs:g}h {__min:g}m {int(__secs)}s'

def timelimitcheck():
    __datenow = datetime.now(cstimezone)
    __finaldate = datetime(2021, 4, 2, 0, 0)
    __tilldate = cstimezone.localize(__finaldate) - __datenow
    if __tilldate.total_seconds() <= 0:
        return True
    else:
        return None