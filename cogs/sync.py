import discord
from discord.ext import commands

class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = bot.supabase

    @commands.command(name="nSync2")
    @commands.has_permissions(administrator=True)
    async def nSync(self, ctx):
        """Sincroniza cargos e canais com o banco de dados do Dashboard"""
        guild = ctx.guild
        gid = str(guild.id)
        
        cargos_data = []
        canais_data = []

        # 1. Coleta de Cargos (Filtrando @everyone e cargos de bots)
        for role in guild.roles:
            if not role.is_default() and not role.managed:
                cargos_data.append({
                    "guild_id": gid,
                    "role_id": str(role.id),
                    "role_name": role.name
                })

        # 2. Coleta de Canais de Texto
        for channel in guild.text_channels:
            canais_data.append({
                "guild_id": gid,
                "channel_id": str(channel.id),
                "channel_name": channel.name
            })

        try:
            # --- SINCRONIZAÇÃO DE CARGOS ---
            self.supabase.table("servidor_cargos").delete().eq("guild_id", gid).execute()
            if cargos_data:
                self.supabase.table("servidor_cargos").insert(cargos_data).execute()

            # --- SINCRONIZAÇÃO DE CANAIS ---
            self.supabase.table("servidor_canais").delete().eq("guild_id", gid).execute()
            if canais_data:
                self.supabase.table("servidor_canais").insert(canais_data).execute()
            
            await ctx.send(
                f"✅ **Sincronização Concluída!**\n"
                f"🔹 {len(cargos_data)} cargos atualizados.\n"
                f"🔹 {len(canais_data)} canais de texto mapeados."
            )
        
        except Exception as e:
            print(f"Erro no nSync: {e}")
            await ctx.send(f"❌ Erro ao sincronizar com o banco: {e}")

async def setup(bot):
    await bot.add_cog(Sync(bot))