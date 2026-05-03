# utils/patente.py

TABELA_PATENTES = {
    0:   1497996840317222922, # Entrada (Recruta)
    2:   248922374892,        # Cabo
    5:   2831927324234,       # Taifeiro Mor
    10:  248922374892,        # Sargento 3
    15:  1497996887729639594, # Sargento 2
    20:  0, # Sargento 1
    25:  0, # Subtenente
    30:  0, # Tenente 2
    35:  0, # Tenente 1
    40:  0, # Capitão
    45:  0, # Major
    50:  0, # Tenente-Coronel
    55:  0, # Coronel
    60:  0, # General de Brigada
    70:  0, # General de Divisão
    85:  0, # General de Exército
    100: 0  # Marechal
}

# Lista automática para facilitar a limpeza no código principal
TODOS_CARGOS_PATENTE = list(TABELA_PATENTES.values())