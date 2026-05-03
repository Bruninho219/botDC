import discord
from discord.ext import commands
import datetime

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = bot.supabase
        self.voice_tracker = {} 

    async def buscar_cargo_por_nivel(self, guild_id, nivel_atual):
        try:
            # Busca a patente específica para o nível atual
            res = self.supabase.table("patentes").select("role_id").eq("guild_id", str(guild_id)).eq("level_required", nivel_atual).execute()
            return res.data[0]['role_id'] if res.data else None
        except: return None

    @commands.Cog.listener()
    async def on_message(self, message):
        # 1. Ignora bots e mensagens fora de servidores
        if message.author.bot or not message.guild: 
            return

        # 2. Ignora comandos específicos para não somar XP/Mensagens
        # Isso evita que o !nRank mostre um valor e some +20 logo em seguida
        comandos_ignorados = ["!nrank", "!nsync", "!setchannel"]
        if message.content.lower().startswith(tuple(comandos_ignorados)):
            return

        # 3. Filtro de tamanho (opcional, você já tinha esse)
        if len(message.content.strip()) < 3:
            return

        # 4. Soma o XP normalmente para conversas reais
        await self.adicionar_xp(message.author, message.guild, message.channel, 20)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or not reaction.message.guild:
            return
        if reaction.count > 1:
            return
        await self.adicionar_xp(user, reaction.message.guild, None, 5)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot: return
        uid, gid = str(member.id), str(member.guild.id)

        if before.channel is None and after.channel is not None:
            self.voice_tracker[uid] = datetime.datetime.now()
        elif before.channel is not None and after.channel is None:
            if uid in self.voice_tracker:
                entrada = self.voice_tracker.pop(uid)
                minutos = int((datetime.datetime.now() - entrada).total_seconds() / 60)
                if minutos > 0:
                    await self.adicionar_xp(member, member.guild, None, minutos * 15, minutos_voz=minutos)

    async def adicionar_xp(self, user, guild, channel, xp_ganho, minutos_voz=0):
        uid, gid = str(user.id), str(guild.id)
        nickname = user.display_name
        
        try:
            res = self.supabase.table("niveis").select("*").eq("guild_id", gid).eq("user_id", uid).execute()
            
            if not res.data:
                self.supabase.table("niveis").insert({
                    "guild_id": gid, "user_id": uid, "username": nickname,
                    "xp": xp_ganho, "level": 0, "msg_count": 1 if channel else 0,
                    "voice_minutes": minutos_voz, "reacoes": 5 if xp_ganho == 5 else 0
                }).execute()
                return

            d = res.data[0]
            novo_xp = d['xp'] + xp_ganho
            novo_level = d['level']
            level_inicial = d['level']

            # Lógica de Level Up Progressivo: (level * 100) + 75
            while novo_xp >= (novo_level * 100) + 75:
                novo_xp -= (novo_level * 100) + 75
                novo_level += 1

            # Atualização dos contadores
            msg_inc = 1 if channel else 0
            reacao_inc = 1 if xp_ganho == 5 else 0
            
            update_data = {
                "username": nickname,
                "xp": int(novo_xp), 
                "level": int(novo_level), 
                "msg_count": d['msg_count'] + msg_inc,
                "voice_minutes": (d.get('voice_minutes', 0) or 0) + minutos_voz,
                "reacoes": (d.get('reacoes', 0) or 0) + reacao_inc
            }
            
            self.supabase.table("niveis").update(update_data).eq("guild_id", gid).eq("user_id", uid).execute()

            # Se upou de nível, gerencia cargos e envia aviso
            if novo_level > level_inicial:
                rid = await self.buscar_cargo_por_nivel(gid, novo_level)
                if rid:
                    role = guild.get_role(int(rid))
                    if role:
                        # Remove patentes antigas
                        res_p = self.supabase.table("patentes").select("role_id").eq("guild_id", gid).execute()
                        if res_p.data:
                            ids_p = [int(p['role_id']) for p in res_p.data]
                            cargos_remover = [guild.get_role(r_id) for r_id in ids_p if r_id in [r.id for r in user.roles] and r_id != int(rid)]
                            await user.remove_roles(*[r for r in cargos_remover if r])
                        await user.add_roles(role)
                
                # Envio de mensagem de level up
                config_res = self.supabase.table("servidor_configs").select("canal_avisos_id").eq("guild_id", gid).execute()
                canal_destino = guild.get_channel(int(config_res.data[0]['canal_avisos_id'])) if config_res.data and config_res.data[0]['canal_avisos_id'] else channel
                if canal_destino:
                    await canal_destino.send(f"{user.mention} >> **{novo_level}**.")
                    
        except Exception as e:
            print(f"Erro Leveling: {e}")

async def setup(bot):
    await bot.add_cog(Leveling(bot))