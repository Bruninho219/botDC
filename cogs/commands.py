import discord
from discord.ext import commands

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = bot.supabase

    @commands.command(name="nRank")
    async def rank(self, ctx, target: discord.Member = None):
        target = target or ctx.author
        try:
            res = self.supabase.table("niveis").select("*")\
                .eq("guild_id", str(ctx.guild.id))\
                .eq("user_id", str(target.id)).execute()

            if not res.data:
                return await ctx.send(f"❌ {target.display_name} ainda não tem registros.")

            d = res.data[0]
            xp_prox = (d['level'] * 100) + 75
            
            embed = discord.Embed(title=f"📊 Rank de {target.display_name}", color=0x5865f2)
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.add_field(name="📈 Nível", value=f"**{d['level']}**", inline=True)
            embed.add_field(name="⭐ XP", value=f"**{d['xp']}/{xp_prox}**", inline=True)
            embed.set_footer(text=f"Mensagens: {d['msg_count']}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Erro no rank: {e}")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setchannel(self, ctx):
        guild_id = str(ctx.guild.id)
        channel_id = str(ctx.channel.id)

        # Salva o ID do canal atual como o canal de anúncios do servidor
        # Aqui estou usando a tabela 'servidor_cargos' como exemplo, 
        # mas adapte para sua tabela de configs se tiver uma separada.
        res = self.supabase.table("servidor_cargos").update({
            "channel_announce_id": channel_id
        }).eq("guild_id", guild_id).execute()

        await ctx.send(f"✅ Canal de anúncios definido para {ctx.channel.mention}!")

    @commands.command(name="nSync")
    @commands.has_permissions(administrator=True)
    async def nSync(self, ctx):
        """Sincroniza os cargos do servidor com o banco para o Dashboard"""
        guild = ctx.guild
        status_msg = await ctx.send("🔄 Sincronizando cargos com o Dashboard...")
        
        cargos_data = []
        for role in guild.roles:
            # Ignora @everyone e cargos de bots/integrações
            if not role.is_default() and not role.managed:
                cargos_data.append({
                    "guild_id": str(guild.id),
                    "role_id": str(role.id),
                    "role_name": role.name
                })
        
        if not cargos_data:
            return await status_msg.edit(content="⚠ Nenhum cargo manual encontrado.")

        try:
            # Limpa e atualiza o cache de cargos
            self.supabase.table("servidor_cargos").delete().eq("guild_id", str(guild.id)).execute()
            self.supabase.table("servidor_cargos").insert(cargos_data).execute()
            
            await status_msg.edit(content=f"✅ **{len(cargos_data)}** cargos sincronizados! Verifique seu Dashboard.")
        except Exception as e:
            await status_msg.edit(content=f"❌ Erro no Supabase: {e}")

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))