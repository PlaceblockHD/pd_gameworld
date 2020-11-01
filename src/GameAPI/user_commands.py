import asyncio
import random

import discord
from discord.ext import commands

from GameAPI.user_extension import get_pets, add_pet, update_player_nick, has_money, deposit_money, withdraw_money, \
    set_money, clear_all_pets, add_xp, set_xp


class Commands(commands.Cog):

    @commands.command()
    async def pets(self, ctx: commands.Context, *args):
        await ctx.message.delete()

        if ctx.channel.id == 772214299997110292:
            if len(args) == 0:
                member = ctx.author
            else:
                member = ctx.guild.get_member_named(args[0])

            if not member == None:

                pets = get_pets(member)

                if (len(pets) == 0):
                    embed = discord.Embed(title="Achtung!",
                                          description="Du hast noch keine Pets",
                                          color=0x999999)
                    embed.set_author(name="Haustiere",
                                     icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await member.send(embed=embed, delete_after=60)

                    return

                rarity_color = {"Gewöhnlich": 0x999999, "Selten": 0x00FF00, "Episch": 0x8800FF, "Legendär": 0xE2B007}

                for pet in pets:
                    embed = discord.Embed(title="Haustier: " + pet.display_name + " :",
                                          description="Daten:",
                                          color=rarity_color.get(pet.rarity, 0x999999))
                    embed.set_author(name="Haustier",
                                     icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.add_field(name="Rarität",
                                    value=pet.rarity,
                                    inline=False)
                    embed.add_field(name="Xp Multiplikator:",
                                    value=str(pet.xp_multiply),
                                    inline=False)
                    embed.add_field(name="Money Multiplikator:",
                                    value=str(pet.money_multiply),
                                    inline=False)
                    await member.send(embed=embed, delete_after=60)


    # Der Chef darf Channels purgen:
    @commands.command()
    async def update_nick(self, ctx: commands.Context, *, member: discord.Member = None):
        await ctx.message.delete()
        role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
        if role in ctx.author.roles:
            members = ctx.guild.members
            for member in members:
                await update_player_nick(member)



    @commands.command()
    async def pet(self, ctx, *, member: discord.Member = None):
        await ctx.message.delete()

        if ctx.channel.id == 772214299997110292:

            cost = 200
            extra_money = 0
            for pet in get_pets(ctx.author):
                extra_money += cost * pet.money_multiply - cost
            cost += extra_money

            if not has_money(ctx.author, cost):
                embed = discord.Embed(title="Du hast nicht genug Money!",
                                      description="Du brauchst mindestens "+ str(cost) +" !",
                                      color=0xFF0000)
                embed.set_author(name="Haustier",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await ctx.channel.send(embed=embed, delete_after=7)
                return

            withdraw_money(ctx.author, cost)

            pet_names = ["Unicorn","Lion","Shark","Icebear","Parrot","Horse","Schildkröte","Affe"]

            pet_data = {"Unicorn": {"xpm": 1.8, "mym": 1.8, "rarity": "Legendär"},
                        "Lion": {"xpm": 1.8, "mym": 1.7, "rarity": "Legendär"},
                        "Shark": {"xpm": 1.6, "mym": 1.6, "rarity": "Episch"},
                        "Icebear": {"xpm": 1.6, "mym": 1.5, "rarity": "Episch"},
                        "Parrot": {"xpm": 1.4, "mym": 1.4, "rarity": "Selten"},
                        "Horse": {"xpm": 1.3, "mym": 1.4, "rarity": "Selten"},
                        "Schildkröte": {"xpm": 1.1, "mym": 1.1, "rarity": "Gewöhnlich"},
                        "Affe": {"xpm": 1.1, "mym": 1.05, "rarity": "Gewöhnlich"}}

            rand_list = random.choices(pet_names, weights = [1,1,3,5,10,15,35,50], k = 100)

            random.shuffle(rand_list)

            winning = rand_list[0]

            winning_data = pet_data[winning]

            add_pet(ctx.author, winning, winning_data["xpm"], winning_data["mym"], winning_data["rarity"])

            rarity_color = {"Gewöhnlich": 0x999999, "Selten": 0x00FF00, "Episch": 0x8800FF, "Legendär": 0xE2B007}

            embed = discord.Embed(title="Du hast " + winning + " gewonnen!",
                                  description="Daten:",
                                  color=rarity_color.get(winning_data["rarity"], 0x999999))
            embed.set_author(name="Haustier",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.add_field(name="Rarität",
                            value=winning_data["rarity"],
                            inline=False)
            embed.add_field(name="Xp Multiplikator:",
                            value=str(winning_data["xpm"]),
                            inline=False)
            embed.add_field(name="Money Multiplikator:",
                            value=str(winning_data["mym"]),
                            inline=False)
            await ctx.channel.send(embed=embed, delete_after=30)

    # Der Chef darf Channels purgen:
    @commands.command()
    async def clear_pets(self, ctx: commands.Context, *, member: discord.Member = None):
        await ctx.message.delete()
        role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
        if role in ctx.author.roles:
            clear_all_pets()

    @commands.command()
    async def money(self, ctx: commands.Context, *args):
        await ctx.message.delete()
        role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
        if role in ctx.author.roles:
            if len(args) == 3:
                member = ctx.guild.get_member_named(args[1])
                if not member == None:
                    if(args[0] == "add"):
                        try:
                            deposit_money(member, int(args[2]))
                        except ValueError:
                            embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                                  description="!money add [name] [zahl]",
                                                  color=0xFF0000)
                            embed.set_author(name="Money",
                                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            await ctx.channel.send(embed=embed, delete_after=7)
                            return
                    if(args[0] == "remove"):
                        try:
                            withdraw_money(member, int(args[2]))
                        except ValueError:
                            embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                                  description="!money withdraw [name] [zahl]",
                                                  color=0xFF0000)
                            embed.set_author(name="Money",
                                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            await ctx.channel.send(embed=embed, delete_after=7)
                            return
                    if(args[0] == "set"):
                        try:
                            set_money(member, int(args[2]))
                        except ValueError:
                            embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                                  description="!money set [name] [zahl]",
                                                  color=0xFF0000)
                            embed.set_author(name="Money",
                                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            await ctx.channel.send(embed=embed, delete_after=7)
                            return
                else:
                    embed = discord.Embed(title="Spieler nicht gefunden!",
                                          description="!money [command] [name] [zahl]",
                                          color=0xFF0000)
                    embed.set_author(name="Money",
                                     icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await ctx.channel.send(embed=embed, delete_after=7)
                    return


    @commands.command()
    async def xp(self, ctx: commands.Context, *args):
        await ctx.message.delete()
        role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
        if role in ctx.author.roles:
            if len(args) == 3:
                member = ctx.guild.get_member_named(args[1])
                if not member == None:
                    if(args[0] == "add"):
                        try:
                            await add_xp(member, int(args[2]))
                        except ValueError:
                            embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                                  description="!xp deposit [name] [zahl]",
                                                  color=0xFF0000)
                            embed.set_author(name="Xp",
                                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            await ctx.channel.send(embed=embed, delete_after=7)
                            return
                    if(args[0] == "set"):
                        try:
                            await set_xp(member, int(args[2]))
                        except ValueError:
                            embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                                  description="!xp set [name] [zahl]",
                                                  color=0xFF0000)
                            embed.set_author(name="Xp",
                                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            await ctx.channel.send(embed=embed, delete_after=7)
                            return
                else:
                    embed = discord.Embed(title="Spieler nicht gefunden!",
                                          description="!xp [command] [name] [zahl]",
                                          color=0xFF0000)
                    embed.set_author(name="Money",
                                     icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await ctx.channel.send(embed=embed, delete_after=7)
                    return





