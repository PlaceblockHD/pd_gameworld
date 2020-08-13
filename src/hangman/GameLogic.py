import asyncio
import random

import discord
from discord.ext import commands

from GameAPI.Queue import Queue

from threading import Timer

from hangman.Game import Game


class HangManGameLogic(commands.Cog):
    def __init__(self, bot):
        self.channels_in_use = {
        }
        self.bot: commands.Bot = bot
        self.queue: Queue = Queue()
        self.joinchannel = 743463967996903496
        self.timer: Timer = None

    #After a player join or a game finsihed do this function
    async def check_for_gamestart(self):
        if self.queue.__len__() > 1:
            if self.queue.__len__() == 2:
                embed = discord.Embed(title="Game is starting...", description="Startet Timer (30 seconds) to allow other players to join in", color=0x58ff46)
                embed.set_author(name="Hangman", icon_url = "https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await self.bot.get_channel(self.joinchannel).send(embed=embed, delete_after=10)
                await asyncio.sleep(5)
                await self.start_game(self.queue.queue)
                return
            if self.queue.__len__() == 8:
                await self.start_game(self.queue.queue)
                self.queue.queue.clear()
                self.timer.cancel()
                return
        else:
            if self.timer is not None:
                self.timer.cancel()


    async def start_game(self, playerids):
        guild: discord.Guild = self.bot.get_guild(741823660188500008)
        channel: discord.TextChannel = await guild.create_text_channel(name="🪓hangman-" + str(len(self.channels_in_use) + 1),category=self.bot.get_channel(743386428624601200))
        channelid = channel.id


        embed = discord.Embed(title="Game is starting!", description="Game takes place in " + self.bot.get_channel(channelid).name, color=0x58ff46)
        embed.set_author(name="Hangman", icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        playernames = ""
        for id in playerids:
            playernames += (self.bot.get_user(id).display_name + " ")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="Players",value=playernames, inline=True)
        await self.bot.get_channel(self.joinchannel).send(embed=embed, delete_after=10)

        notguessingplayerid = random.choice(playerids)
        playerids.remove(notguessingplayerid)

        embed = discord.Embed(title="Enter correctword", description="You have to write the word here which the others have to guess")
        embed.set_author(name="Hangman", icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await self.bot.get_user(notguessingplayerid).send(embed=embed, delete_after=30)

        hangmangame = Game(playerids, channelid, self.bot, notguessingplayerid)
        self.bot.add_cog(hangmangame)
        self.channels_in_use[channel.id] = hangmangame


        return

    async def stop(self, channel_id):
        await self.bot.get_channel(self.channels_in_use[channel_id].channelid).delete()
        self.channels_in_use[channel_id].bot.remove_cog(self)
        self.channels_in_use.pop(channel_id)

    @commands.command()
    async def hangman(self, ctx: commands.Context, *, member: discord.Member = None):
        member = ctx.author or member
        await ctx.message.delete()
        commandchannel = ctx.channel
        if commandchannel.id == self.joinchannel:
            if member.id in self.queue:
                self.queue.remove(member.id)
                embed = discord.Embed(title="See you soon!", description=f"""{member.display_name} left the Queue""",color=0x49ff35)
                embed.set_author(name="Hangman",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await ctx.channel.send(embed=embed)
                return

            embed = discord.Embed(title="Nice!", description=f"""{member.display_name} Joined the Queue""", color=0x49ff35)
            embed.set_author(name="Hangman", icon_url = "https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.add_field(name="But:", value="It may take a moment for the game to start, so sit back and relax", inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_footer(text="Thanks vor Playing!")
            await ctx.channel.send(embed=embed, delete_after=10)
            self.queue.put(member.id)
            await self.check_for_gamestart()


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        game = None
        for key in self.channels_in_use:
            if message.author.id in self.channels_in_use[key].playerids or message.author.id == self.channels_in_use[key].not_guessing_player_id:
                game = self.channels_in_use[key]
                break

        if game is not None:
            if game.gamestate == 0:
                if message.author.id == game.not_guessing_player_id and message.channel.type == discord.ChannelType.private:
                    if message.content.isalpha():
                        game.correct_word = message.content.upper()
                        game.gamestate = 1
                        embed = discord.Embed(title="Done!", description="Your can now return to "+game.bot.get_channel(game.channelid).name+"!",color=0x58ff46)
                        embed.set_author(name="Hangman",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await game.bot.get_user(game.not_guessing_player_id).send(embed=embed, delete_after=10)

                        embed = discord.Embed(title="You have to guess:", description=game.get_print_string(), color=0x58ff46)
                        embed.set_author(name="Hangman",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        game.message = await game.bot.get_channel(game.channelid).send(embed=embed)
                    else:
                        embed = discord.Embed(title="Attention", description="Your word can only contains letters!", color=0xff4646)
                        embed.set_author(name="Hangman", icon_url = "https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await game.bot.get_user(game.not_guessing_player_id).send(embed=embed, delete_after=10)
                else:
                    await message.delete()
                return
            if message.channel.id == game.channelid and message.author.id is not game.not_guessing_player_id and message.author.id in game.playerids:
                await message.delete()
                if message.content.upper() == game.correct_word:
                    embed = discord.Embed(title=":tada: " + game.bot.get_user(message.author.display_name) + " has guessed the Word! :tada:", description="Thanks for playing!", color=0x58ff46)
                    embed.set_author(name="Hangman",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await game.bot.get_channel(game.channelid).send(embed=embed)
                    await asyncio.sleep(10)
                    await self.stop(game.channelid)
                elif game.is_valid_guess(message.content.upper()):
                    if not game.has_already_guessed(message.content.upper()):
                        await game.guess(message.content)

                        if game.loose_level == 10:
                            embed = discord.Embed(title="You loose:", description="Hangman was hanged!", color=0x58ff46)
                            embed.set_author(name="Hangman", icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            await game.bot.get_channel(game.channelid).send(embed=embed)
                            # TODO: PROGRAMM BLOCKER SO WHEN THE GAME IS FINSIHED BUT NOT DELETED NO ONE CAN INPUT SOMETHING
                            await asyncio.sleep(10)
                            await self.stop(game.channelid)

                return