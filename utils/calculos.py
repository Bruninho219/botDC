# utils/calculos.py
import math

def calcular_nivel_pelo_xp(xp_total):
    """
    Calcula o nível baseado no XP total acumulado.
    Inverso da soma de P.A. onde cada nível custa (level * 100) + 75.
    """
    if xp_total < 75:
        return 0
    
    # Resolvendo a equação de 2º grau: 50n² + 25n + (75 - xp_total) = 0
    a = 50
    b = 25
    c = 75 - xp_total
    
    delta = (b**2) - (4 * a * c)
    
    if delta < 0:
        return 0
        
    # Bhaskara: n = (-b + √delta) / 2a
    nivel = (-b + math.sqrt(delta)) / (2 * a)
    return int(nivel)

async def buscar_cargo_por_nivel(guild_id, nivel_atual, supabase):
    res = supabase.table("patentes") \
        .select("role_id") \
        .eq("guild_id", str(guild_id)) \
        .lte("level_required", nivel_atual) \
        .order("level_required", descending=True) \
        .limit(1) \
        .execute()
    
    return res.data[0]['role_id'] if res.data else None

async def obter_todos_cargos_guild(guild_id, supabase):
    res = supabase.table("patentes") \
        .select("role_id") \
        .eq("guild_id", str(guild_id)) \
        .execute()
    return [item['role_id'] for item in res.data]