import discord
from discord.ext import commands
import os
from core import Cog, Cypher, Context
import games as games
from utils.Tools import *
from games import button_games as btn
import random
import asyncio



class Games(Cog):
    def __init__(self, client: Cypher):
        self.client = client


    @commands.hybrid_command(name="chess",
                             help="Play Chess with a user.",
                             usage="Chess <user>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(5, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _chess(self, ctx: Context, player: discord.Member):
        if player == ctx.author:
            await ctx.send("You Cannot play game with yourself!",
                           mention_author=False)
        elif player.bot:
            await ctx.send("You cannot play with bots!")
        else:
            game = btn.BetaChess(white=ctx.author, black=player)
            await game.start(ctx)


    @commands.hybrid_command(name="rps",
                             help="Play Rock Paper Scissor with bot/user.",
                             aliases=["rockpaperscissors"],
                             usage="Rockpaperscissors")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(5, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _rps(self, ctx: Context, player: discord.Member = None):
        game = btn.BetaRockPaperScissors(player)
        await game.start(ctx, timeout=120)

    @commands.hybrid_command(name="tic-tac-toe",
                             help="play tic-tac-toe game with a user.",
                             aliases=["ttt", "tictactoe"],
                             usage="Ticktactoe <member>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(5, per=commands.BucketType.user, wait=False)
    @commands.guild_only()
    async def _ttt(self, ctx: Context, player: discord.Member):
        if player == ctx.author:
            await ctx.send("You Cannot play game with yourself!",
                           mention_author=False)
        elif player.bot:
            await ctx.send("You cannot play with bots!")
        else:
            game = btn.BetaTictactoe(cross=ctx.author, circle=player)
            await game.start(ctx, timeout=30)

    @commands.hybrid_command(name="wordle",
                             help="Wordle Game | Play with bot.",
                             usage="Wordle")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _wordle(self, ctx: Context):
        game = games.Wordle()
        await game.start(ctx, timeout=120)
        
    @commands.hybrid_command(name="connect4",
                             help="Play connect4 game with bot.",
                             usage="connect4")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _connectfour(self, ctx: Context, member: discord.User):
        game = games.ConnectFour(
            red=ctx.author,
            blue=member,
        )
        await game.start(ctx)

    @commands.hybrid_command(name="2048",
                             help="Play 2048 game with bot.",
                             aliases=["twenty48"],
                             usage="2048")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _2048(self, ctx: Context):
        game = btn.BetaTwenty48()
        await game.start(ctx, win_at=2048)
        
async def setup(client):
    await client.add_cog(Games(client))