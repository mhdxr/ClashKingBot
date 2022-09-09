from disnake.ext import commands
import disnake
from CustomClasses.CustomBot import CustomClient


class Linking(commands.Cog):

    def __init__(self, bot: CustomClient):
        self.bot = bot

    @commands.slash_command(name="refresh", description="Self evaluate & refresh your server roles")
    async def refresh(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        tags = await self.bot.get_tags(str(ctx.author.id))
        if tags !=[]:
            evalua = self.bot.get_cog("Eval")
            changes = await evalua.eval_member(ctx, ctx.author, False)
            embed = disnake.Embed(
                description=f"Refreshed your roles {ctx.author.mention}.\n"
                            f"Added: {changes[0]}\n"
                            f"Removed: {changes[1]}", color=disnake.Color.green())
            return await ctx.edit_original_message(embed=embed)
        else:
            embed = disnake.Embed(
                description=f"You have no accounts linked.", color=disnake.Color.red())
            return await ctx.edit_original_message(embed=embed)

    @commands.slash_command(name="link", description="Link clash of clans accounts to your discord profile")
    async def link(self,  ctx: disnake.ApplicationCommandInteraction, player_tag, api_token):
        """
            Parameters
            ----------
            player_tag: player_tag as found in-game
            api_token: player api-token, use /linkhelp for more info
        """
        await ctx.response.defer()
        try:
            player = await self.bot.getPlayer(player_tag)
            if player is None:
                embed = disnake.Embed(description=f"{player_tag} is not a valid player tag. Use the photo below to help find your player tag.", color=disnake.Color.red())
                embed.set_image(
                    url="https://cdn.discordapp.com/attachments/886889518890885141/933932859545247794/bRsLbL1.png")
                return await ctx.edit_original_message(embed=embed)

            verified = await self.bot.verifyPlayer(player.tag, api_token)
            linked = await self.bot.link_client.get_link(player.tag)
            is_linked = (linked is not None)

            if verified and is_linked:
                if linked == ctx.author.id:
                    evalua = self.bot.get_cog("Eval")
                    changes = await evalua.eval_member(ctx, ctx.author, False)
                    embed = disnake.Embed(
                        description=f"[{player.name}]({player.share_link}) is already linked to you {ctx.author.mention}.\n"
                                    f"Added: {changes[0]}\n"
                                    f"Removed: {changes[1]}", color=disnake.Color.green())
                    await ctx.edit_original_message(embed=embed)
                else:
                    embed = disnake.Embed(
                        description=f"[{player.name}]({player.share_link}) is already linked to another discord user. Use `/unlink` to remove the link first.", color=disnake.Color.red())
                    await ctx.edit_original_message(embed=embed)

            elif verified and not is_linked:
                await self.bot.link_client.add_link(player.tag, ctx.author.id)
                evalua = self.bot.get_cog("Eval")
                changes = await evalua.eval_member(ctx, ctx.author, False)
                embed = disnake.Embed(
                    description=f"[{player.name}]({player.share_link}) is successfully linked to {ctx.author.mention}.\n"
                                f"Added: {changes[0]}\n"
                                f"Removed: {changes[1]}", color=disnake.Color.green())
                await ctx.edit_original_message(embed=embed)
                try:
                    results = await self.bot.server_db.find_one({"server": ctx.guild.id})
                    greeting = results.get("greeting")
                    if greeting is None:
                        greeting = ""

                    results = await self.bot.clan_db.find_one({"$and": [
                        {"tag": player.clan.tag},
                        {"server": ctx.guild.id}
                    ]})
                    if results is not None:
                        channel = results.get("clanChannel")
                        channel = self.bot.get_channel(channel)
                        await channel.send(f"{ctx.author.mention}, welcome to {ctx.guild.name}! {greeting}")
                except:
                    pass

            elif not verified and is_linked:
                if linked == ctx.author.id:
                    evalua = self.bot.get_cog("eval")
                    changes = await evalua.eval_member(ctx, ctx.author, False)
                    embed = disnake.Embed(
                        description=f"[{player.name}]({player.share_link}) is already linked to you {ctx.author.mention}.\n"
                                    f"Added: {changes[0]}\n"
                                    f"Removed: {changes[1]}", color=disnake.Color.green())
                    await ctx.edit_original_message(embed=embed)
                else:
                    embed = disnake.Embed(
                        title="API Token is Incorrect!",
                        description=f"- Reference below for help finding your api token.\n- Open Clash and navigate to Settings > More Settings - OR use the below link:\nhttps://link.clashofclans.com/?action=OpenMoreSettings" +
                                    "\n- Scroll down to the bottom and copy the api token.\n- View the picture below for reference.",
                        color=disnake.Color.red())
                    embed.set_image(
                        url="https://cdn.discordapp.com/attachments/843624785560993833/961379232955658270/image0_2.png")
                    await ctx.edit_original_message(embed=embed)

            elif not verified and not is_linked:
                embed = disnake.Embed(
                    title="API Token is Incorrect!",
                    description=f"- Reference below for help finding your api token.\n- Open Clash and navigate to Settings > More Settings - OR use the below link:\nhttps://link.clashofclans.com/?action=OpenMoreSettings" +
                                "\n- Scroll down to the bottom and copy the api token.\n- View the picture below for reference.",
                    color=disnake.Color.red())
                embed.set_image(
                    url="https://cdn.discordapp.com/attachments/843624785560993833/961379232955658270/image0_2.png")
                await ctx.edit_original_message(embed=embed)
        except Exception as e:
            await ctx.edit_original_message(content=(str(e))[:1000])

    @commands.slash_command(name="verify", description="Link clash of clans accounts to your discord profile", guild_ids=[548297912443207706])
    async def verify(self, ctx: disnake.ApplicationCommandInteraction, player_tag):
        """
            Parameters
            ----------
            player_tag: player_tag as found in-game
        """

        try:
            player = await self.bot.getPlayer(player_tag)
            if player is None:
                embed = disnake.Embed(
                    description=f"{player_tag} is not a valid player tag. Use the photo below to help find your player tag.",
                    color=disnake.Color.red())
                embed.set_image(
                    url="https://cdn.discordapp.com/attachments/886889518890885141/933932859545247794/bRsLbL1.png")
                return await ctx.send(embed=embed)

            linked = await self.bot.link_client.get_link(player.tag)
            is_linked = (linked is not None)

            if is_linked:
                if linked == ctx.author.id:
                    evalua = self.bot.get_cog("Eval")
                    changes = await evalua.eval_member(ctx, ctx.author, False)
                    embed = disnake.Embed(
                        description=f"[{player.name}]({player.share_link}) is already linked to you {ctx.author.mention}.\n"
                                    f"Added: {changes[0]}\n"
                                    f"Removed: {changes[1]}", color=disnake.Color.green())
                    await ctx.send(embed=embed)
                else:
                    embed = disnake.Embed(
                        description=f"[{player.name}]({player.share_link}) is already linked to another discord user. Use `/unlink` to remove the link first.",
                        color=disnake.Color.red())
                    await ctx.send(embed=embed)

            elif not is_linked:
                await self.bot.link_client.add_link(player.tag, ctx.author.id)
                evalua = self.bot.get_cog("Eval")
                changes = await evalua.eval_member(ctx, ctx.author, False)
                embed = disnake.Embed(
                    description=f"[{player.name}]({player.share_link}) is successfully linked to {ctx.author.mention}.\n"
                                f"Added: {changes[0]}\n"
                                f"Removed: {changes[1]}", color=disnake.Color.green())
                await ctx.send(embed=embed)
                try:
                    results = await self.bot.server_db.find_one({"server": ctx.guild.id})
                    greeting = results.get("greeting")
                    if greeting is None:
                        greeting = ""

                    results = await self.bot.clan_db.find_one({"$and": [
                        {"tag": player.clan.tag},
                        {"server": ctx.guild.id}
                    ]})
                    if results is not None:
                        channel = results.get("clanChannel")
                        channel = self.bot.get_channel(channel)
                        await channel.send(f"{ctx.author.mention}, welcome to {ctx.guild.name}! {greeting}")
                except:
                    pass
        except Exception as e:
            await ctx.send(e[0:1000])

    @commands.slash_command(name="linkhelp", description="Help & Reference guide for /link command")
    async def linkhelp(self, ctx: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(title="Finding a player tag",
            description=f"- Open Game\n- Navigate to your account's profile\n- Near top left click copy icon to copy player tag to clipboard\n"
                        f"- Make sure it is the player tag & **not** the clan\n- View photo below for reference",
            color=disnake.Color.red())
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/886889518890885141/933932859545247794/bRsLbL1.png")
        embed2 = disnake.Embed(
            title="What is your api token? ",
            description=f"- Reference below for help finding your api token.\n- Open Clash and navigate to Settings > More Settings\n- **OR** use the following link:\nhttps://link.clashofclans.com/?action=OpenMoreSettings" +
                        "\n- Scroll down to the bottom and copy the api token.\n- View the picture below for reference.",
            color=disnake.Color.red())
        embed2.set_image(
            url="https://cdn.discordapp.com/attachments/843624785560993833/961379232955658270/image0_2.png")
        await ctx.send(embeds=[embed, embed2])


    @commands.slash_command(name="modlink", description="Links clash account to a discord member, on their behalf.")
    async def modlink(self, ctx: disnake.ApplicationCommandInteraction, member : disnake.Member, player_tag, greet=commands.Param(default="Yes", choices=["Yes", "No"])):
        """
            Parameters
            ----------
            player_tag: player_tag as found in-game
            member: discord member to link this player to
            greet: (optional) don't send the clan greeting for a newly linked account
        """
        perms = ctx.author.guild_permissions.manage_guild
        if not perms:
            embed = disnake.Embed(description="Command requires you to have `Manage Server` permissions.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        await ctx.response.defer()
        player = await self.bot.getPlayer(player_tag)
        if player is None:
            embed = disnake.Embed(description="Invalid Player Tag", color=disnake.Color.red())
            return await ctx.edit_original_message(embed=embed)

        linked = await self.bot.link_client.get_link(player.tag)

        if linked is not None:
            if linked == member.id:
                embed = disnake.Embed(
                    description=f"{player.name} is already linked to {member.mention}",
                    color=disnake.Color.red())
                return await ctx.edit_original_message(embed=embed)
            else:
                embed = disnake.Embed(
                    title=f"{player.name} is already linked to a discord user.",
                    color=disnake.Color.red())
                return await ctx.edit_original_message(embed=embed)


        await self.bot.link_client.add_link(player.tag, member.id)

        evalua = self.bot.get_cog("Eval")
        changes = await evalua.eval_member(ctx, member, False)

        embed = disnake.Embed(description=f"[{player.name}]({player.share_link}) has been linked to {member.mention}.\n"
                                          f"Added: {changes[0]}\n"
                                        f"Removed: {changes[1]}", color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)

        if greet != "No":
            try:
                results = await self.bot.server_db.find_one({"server": ctx.guild.id})
                greeting = results.get("greeting")
                if greeting is None:
                    greeting = ""

                results = await self.bot.clan_db.find_one({"$and": [
                    {"tag": player.clan.tag},
                    {"server": ctx.guild.id}
                ]})
                if results is not None:
                    channel = results.get("clanChannel")
                    channel = self.bot.get_channel(channel)
                    await channel.send(f"{member.mention}, welcome to {ctx.guild.name}! {greeting}")
            except:
                pass

    @commands.slash_command(name="unlink", description="Unlinks a clash account from discord")
    async def unlink(self, ctx: disnake.ApplicationCommandInteraction, player_tag, api_token=None):
        """
            Parameters
            ----------
            player_tag: player_tag as found in-game
            api_token: required if
        """
        if api_token is None:
            perms = ctx.author.guild_permissions.manage_guild
            if ctx.author.id == 706149153431879760:
                perms = True
            if not perms:
                embed = disnake.Embed(description="Must have `Manage Server` permissions to use command without `api_token`.",
                                      color=disnake.Color.red())
                return await ctx.send(embed=embed)

        player = await self.bot.getPlayer(player_tag)
        if player is None:
            embed = disnake.Embed(description="Invalid Player Tag", color=disnake.Color.red())
            return await ctx.send(embed=embed)

        linked = await self.bot.link_client.get_link(player.tag)
        if linked is None:
            embed = disnake.Embed(
                title=player.name + " is not linked to a discord user.",
                color=disnake.Color.red())
            return await ctx.send(embed=embed)

        if api_token is None:
            member = await self.bot.pingToMember(ctx, linked)
            is_member = (member is not None)
            if ctx.author.id == 706149153431879760 or ctx.author.id == 161053630038802433:
                is_member = True

            if is_member is False:
                embed = disnake.Embed(description=f"[{player.name}]({player.share_link}), cannot unlink players not on this server.",
                                      color=disnake.Color.red())
                return await ctx.send(embed=embed)
            await self.bot.link_client.delete_link(player.tag)
            embed = disnake.Embed(description=f"[{player.name}]({player.share_link}) has been unlinked from discord.",
                                  color=disnake.Color.green())
            await ctx.send(embed=embed)
        else:
            verified = await self.bot.verifyPlayer(playerTag=player.tag, playerToken=api_token)
            if verified:
                embed = disnake.Embed(
                    description=f"[{player.name}]({player.share_link}) has been unlinked from discord.",
                    color=disnake.Color.green())
                await ctx.send(embed=embed)
            else:
                embed = disnake.Embed(
                    description=f"Invalid Api Token for [{player.name}]({player.share_link}).",
                    color=disnake.Color.green())
                await ctx.send(embed=embed)



def setup(bot: CustomClient):
    bot.add_cog(Linking(bot))