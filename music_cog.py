import discord
from discord.ext import commands
from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.isplaying = False
        self.ispaused = False
        self.musicqueue = []
        self.YDLOPTIONS = {"format": "best audio", "noplaylist": "True"}
        self.FFMPEGOPTIONS = {"beforeoptions": "reconnect 1 -reconnect_streamed 1 -reconnected_delay_max 5", "options": "-vn"}
        self.vc = None

        def search_yt(self, item):
            with YoutubeDL(self.YDLOPTIONS) as ydl:
                try:
                    info = ydl.extract_info("ytsearch:%s" % item, download=False["entries"][0])
                except Exception:
                    return False
            return{"source": info["formats"][0]["url"], "title":info["title"]}

        def playnext(self):
            if len(self.musicqueue)>0:
                self.isplaying = True
                aurl = self.musicqueue[0][0]["source"]
                self.musicqueue.pop(0)
                self.vc.play(discord.FFmpegOpusAudio(aurl,**self.FFMPEGOPTIONS), after= lambda e: self.play_next())
            else:
                self.isplaying = False

        async def playmusic(self, ctx):
            if len(self.musicqueue)>0:
                self.isplaying = True
                aurl = self.musicqueue[0][0]["source"]
                if self.vc == None or not self.vcisconnected():
                    self.vc = await self.musicqueue[0][1].connected()
                    if self.vc == None:
                        await ctx.send("Could not connect to the voice channel")
                        return
                else:
                    await self.vcmoveto(self.musicqueue[0][1])
                self.musicqueue.pop(0)
                self.vc.play(discord.FFmpegOpusAudio(aurl, **self.FFMPEGOPTIONS), after=lambda e: self.play_next())
            else:
                self.isplaying = False

        @commands.command(name="play", aliases = ["p", "playing"], help= "Play the selected song from Youtube")
        async def play(self,ctx, *args):
            query = " ".join(args)
            voicechannel = ctx.author.voice.channel
            if voicechannel is None:
                await ctx.send("Connect to a voice channel")
            elif self.ispaused:
                self.vc.resume()
            else:
                song = self.searchyt(query)
                if type(song)==type(True):
                    await ctx.send("Could not download the song. Incorrect format, try a different keyword")
                else:
                    await ctx.send("Song added to the queue")
                    self.musicqueue.append([song, voicechannel])
                    if self.isplaying==False:
                        await self.playmusic(ctx)
        @commands.command(name="pause", help="Pause the current song being played")
        async def pause(self, ctx, *args):
            if self.isplaying:
                self.isplaying = False
                self.ispaused = True
                self.vc.pause()
            elif self.ispaused:
                self.isplaying = True
                self.ispaused = False
                self.vc.resume()

        @commands.command(name="resume", aliases=["r"], help="Resume playing the current song")
        async def resume(self, ctx, *args):
            if self.ispaused:
                self.isplaying = True
                self.ispaused = False
                self.vc.resume()

        @commands.command(name="skip", aliases=["s"], help="Skips the currently played song")
        async def skip(self, ctx, *args):
            if self.vc!= None and self.vc:
                self.vc.stop()
                await self.playmusic(ctx)

        @commands.command(name="queue", aliases=["q"], help="Skips the currently played song")
        async def queue(self, ctx):
            retval = ""
            for x in range(0, len(self.musicqueue)):
                if x>4:
                    break
                retval = self.musicqueue[x][0]["title"] + "\n"
                if retval!= "":
                    await ctx.send(retval)
                else:
                    await ctx.send("No music in the queue")

        @commands.command(name="clear", aliases=["c", "bin"], help="Stops the current song and clears the queue")
        async def clear(self, ctx, *args):
            if self.vc!= None and self.isplaying:
                self.vc.stop()
            self.musicqueue = []
            await ctx.send("Music queue cleared")

        @commands.command(name="leave", aliases=["disconnect", "1","d"], help="Kick the bot from the voice channel")
        async def leave(self, ctx):
            self.isplaying = False
            self.ispaused = False
            await self.vc.disconnect()
