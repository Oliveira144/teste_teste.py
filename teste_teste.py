import streamlit as st
import pandas as pd
import collections

# --- Constantes e Funções Auxiliares ---
NUM_RECENT_RESULTS_FOR_ANALYSIS = 27
MAX_HISTORY_TO_STORE = 1000
NUM_HISTORY_TO_DISPLAY = 100 # Número de resultados do histórico a serem exibidos
EMOJIS_PER_ROW = 9 # Quantos emojis por linha no histórico horizontal
MIN_RESULTS_FOR_SUGGESTION = 9

def get_color(result):
    """Retorna a cor associada ao resultado."""
    if result == 'home':
        return 'red'
    elif result == 'away':
        return 'blue'
    else: # 'draw'
        return 'yellow'

def get_color_emoji(color):
    """Retorna o emoji correspondente à cor."""
    if color == 'red':
        return '🔴'
    elif color == 'blue':
        return '🔵'
    elif color == 'yellow':
        return '🟡'
    return ''

def get_result_emoji(result_type):
    """Retorna o emoji correspondente ao tipo de resultado. Agora retorna uma string vazia para remover os ícones."""
    return ''

# --- Funções de Análise ---

def analyze_surf(results):
    """
    Analisa os padrões de "surf" (sequências de Home/Away/Draw)
    nos últimos N resultados para 'current' e no histórico completo para 'max'.
    """
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    
    current_home_sequence = 0
    current_away_sequence = 0
    current_draw_sequence = 0
    
    if relevant_results:
        # A sequência atual é sempre do resultado mais recente (results[0])
        first_result_current_analysis = relevant_results[0]
        for r in relevant_results:
            if r == first_result_current_analysis:
                if first_result_current_analysis == 'home': 
                    current_home_sequence += 1
                elif first_result_current_analysis == 'away': 
                    current_away_sequence += 1
                else: # draw
                    current_draw_sequence += 1
            else:
                break
    
    # Calcular sequências máximas em todo o histórico disponível para maior precisão
    max_home_sequence = 0
    max_away_sequence = 0
    max_draw_sequence = 0
    
    temp_home_seq = 0
    temp_away_seq = 0
    temp_draw_seq = 0

    for res in results: # Percorre TODOS os resultados (histórico completo) para o máximo
        if res == 'home':
            temp_home_seq += 1
            temp_away_seq = 0
            temp_draw_seq = 0
        elif res == 'away':
            temp_away_seq += 1
            temp_home_seq = 0
            temp_draw_seq = 0
        else: # draw
            temp_draw_seq += 1
            temp_home_seq = 0
            temp_away_seq = 0
        
        max_home_sequence = max(max_home_sequence, temp_home_seq)
        max_away_sequence = max(max_away_sequence, temp_away_seq)
        max_draw_sequence = max(max_draw_sequence, temp_draw_seq)

    return {
        'home_sequence': current_home_sequence,
        'away_sequence': current_away_sequence,
        'draw_sequence': current_draw_sequence,
        'max_home_sequence': max_home_sequence,
        'max_away_sequence': max_away_sequence,
        'max_draw_sequence': max_draw_sequence
    }

def analyze_colors(results):
    """Analisa a contagem e as sequências de cores nos últimos N resultados."""
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'red': 0, 'blue': 0, 'yellow': 0, 'current_color': '', 'streak': 0, 'color_pattern_27': ''}

    color_counts = {'red': 0, 'blue': 0, 'yellow': 0}

    for result in relevant_results:
        color = get_color(result)
        color_counts[color] += 1

    current_color = get_color(results[0]) if results else ''
    streak = 0
    for result in results: # Streak é sempre do resultado mais recente no histórico completo
        if get_color(result) == current_color:
            streak += 1
        else:
            break
            
    color_pattern_27 = ''.join([get_color(r)[0].upper() for r in relevant_results])

    return {
        'red': color_counts['red'],
        'blue': color_counts['blue'],
        'yellow': color_counts['yellow'],
        'current_color': current_color,
        'streak': streak,
        'color_pattern_27': color_pattern_27
    }

def find_complex_patterns(results):
    """
    Identifica padrões de quebra e padrões específicos (2x2, 3x3, 3x1, 2x1, etc.)
    nos últimos N resultados, incluindo os novos padrões. Os nomes dos padrões agora são concisos, sem exemplos ou emojis.
    """
    patterns = collections.defaultdict(int)
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]

    # Converte resultados para cores para facilitar a análise de padrões
    colors = [get_color(r) for r in relevant_results]

    for i in range(len(colors) - 1):
        color1 = colors[i]
        color2 = colors[i+1]

        # 1. Quebra Simples
        if color1 != color2:
            patterns[f"Quebra Simples ({color1.capitalize()} para {color2.capitalize()})"] += 1

        # Verificar padrões que envolvem 3 ou mais resultados
        if i < len(colors) - 2:
            color3 = colors[i+2]
            
            # 2. Padrões 2x1 (Ex: R R B)
            if color1 == color2 and color1 != color3:
                patterns[f"2x1 ({color1.capitalize()} para {color3.capitalize()})"] += 1
            
            # 3. Zig-Zag / Padrão Alternado (Ex: R B R)
            if color1 != color2 and color2 != color3 and color1 == color3:
                patterns[f"Zig-Zag / Alternado ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()})"] += 1

            # 4. Alternância com Empate no Meio (X Draw Y - Ex: R Y B)
            if color2 == 'yellow' and color1 != 'yellow' and color3 != 'yellow' and color1 != color3:
                patterns[f"Alternância c/ Empate no Meio ({color1.capitalize()}-Empate-{color3.capitalize()})"] += 1

            # 5. Padrão Onda 1-2-1 (Ex: R B B R) - variação de espelho ou zig-zag
            if i < len(colors) - 3:
                color4 = colors[i+3]
                if color1 != color2 and color2 == color3 and color3 != color4 and color1 == color4:
                    patterns[f"Padrão Onda 1-2-1 ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()}-{color4.capitalize()})"] += 1

        if i < len(colors) - 3:
            color3 = colors[i+2]
            color4 = colors[i+3]

            # 6. Padrões 3x1 (Ex: R R R B)
            if color1 == color2 and color2 == color3 and color1 != color4:
                patterns[f"3x1 ({color1.capitalize()} para {color4.capitalize()})"] += 1
            
            # 7. Padrões 2x2 (Ex: R R B B)
            if color1 == color2 and color3 == color4 and color1 != color3:
                patterns[f"2x2 ({color1.capitalize()} para {color3.capitalize()})"] += 1
            
            # 8. Padrão de Espelho (Ex: R B B R)
            if color1 != color2 and color2 == color3 and color1 == color4:
                patterns[f"Padrão Espelho ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()}-{color4.capitalize()})"] += 1

        if i < len(colors) - 5:
            color3 = colors[i+2]
            color4 = colors[i+3]
            color5 = colors[i+4]
            color6 = colors[i+5]

            # 9. Padrões 3x3 (Ex: R R R B B B)
            if color1 == color2 and color2 == color3 and color4 == color5 and color5 == color6 and color1 != color4:
                patterns[f"3x3 ({color1.capitalize()} para {color4.capitalize()})"] += 1

    # 10. Duplas Repetidas (Ex: R R, B B, Y Y) - Contagem de ocorrências de duplas
    for i in range(len(colors) - 1):
        if colors[i] == colors[i+1]:
            patterns[f"Dupla Repetida ({colors[i].capitalize()})"] += 1
            
    # Padrão de Reversão / Alternância de Blocos (Ex: RR BB RR BB)
    block_pattern_keys = []
    if len(colors) >= 4:
        for block_size in [2, 3]: # Tamanhos de bloco comuns
            if len(colors) >= 2 * block_size:
                block1_colors = colors[:block_size]
                block2_colors = colors[block_size : 2 * block_size]
                
                if all(c == block1_colors[0] for c in block1_colors) and \
                   all(c == block2_colors[0] for c in block2_colors) and \
                   block1_colors[0] != block2_colors[0]:
                    
                    if len(colors) >= 4 * block_size:
                        block3_colors = colors[2 * block_size : 3 * block_size]
                        block4_colors = colors[3 * block_size : 4 * block_size]
                        if all(c == block3_colors[0] for c in block3_colors) and \
                           all(c == block4_colors[0] for c in block4_colors) and \
                           block1_colors[0] == block3_colors[0] and \
                           block2_colors[0] == block4_colors[0]:
                            block_pattern_keys.append(f"Padrão Reversão/Bloco Alternado {block_size}x{block_size} ({block1_colors[0].capitalize()} {block2_colors[0].capitalize()})")
                    else:
                            block_pattern_keys.append(f"Padrão Reversão/Bloco {block_size}x{block_size} ({block1_colors[0].capitalize()} {block2_colors[0].capitalize()})")
    
    for key in block_pattern_keys:
        patterns[key] += 1

    # --- NOVO PADRÃO: Padrão Escada (1-2-3 ou 3-2-1) ---
    # Este padrão busca sequências de crescentes/decrescentes de um tipo seguido por outro.
    # Ex: R (1) -> BB (2) -> YYY (3)
    # Ex: RRR (3) -> BB (2) -> Y (1)
    if len(colors) >= 6: # Mínimo para 1-2-3
        # 1-2-3 crescente
        if colors[0] != colors[1] and \
           colors[1] == colors[2] and colors[2] != colors[3] and \
           colors[3] == colors[4] and colors[4] == colors[5] and colors[5] != colors[0]: # Ultimo diferente do primeiro
            patterns[f"Padrão Escada Crescente ({colors[0].capitalize()}-{colors[1].capitalize()}2-{colors[3].capitalize()}3)"] += 1
        
        # 3-2-1 decrescente
        if colors[0] == colors[1] and colors[1] == colors[2] and colors[2] != colors[3] and \
           colors[3] == colors[4] and colors[4] != colors[5] and colors[5] != colors[0]: # Ultimo diferente do primeiro
            patterns[f"Padrão Escada Decrescente ({colors[0].capitalize()}3-{colors[3].capitalize()}2-{colors[5].capitalize()}1)"] += 1


    return dict(patterns)

def analyze_break_probability(results):
    """Analisa a probabilidade de quebra com base no histórico dos últimos N resultados."""
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results or len(relevant_results) < 2:
        return {'break_chance': 0, 'last_break_type': ''}
    
    breaks = 0
    total_sequences_considered = 0
    
    for i in range(len(relevant_results) - 1):
        if get_color(relevant_results[i]) != get_color(relevant_results[i+1]):
            breaks += 1
        total_sequences_considered += 1
            
    break_chance = (breaks / total_sequences_considered) * 100 if total_sequences_considered > 0 else 0

    last_break_type = ""
    if len(results) >= 2 and get_color(results[0]) != get_color(results[1]):
        last_break_type = f"Quebrou de {get_color(results[1]).capitalize()} para {get_color(results[0]).capitalize()}"
    
    return {
        'break_chance': round(break_chance, 2),
        'last_break_type': last_break_type
    }

def analyze_draw_specifics(results):
    """Análise específica para empates nos últimos N resultados e padrões de recorrência."""
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'draw_frequency_27': 0, 'time_since_last_draw': -1, 'draw_patterns': {}, 'recurrent_draw': False}

    draw_count_27 = relevant_results.count('draw')
    draw_frequency_27 = (draw_count_27 / len(relevant_results)) * 100 if len(relevant_results) > 0 else 0

    time_since_last_draw = -1
    for i, result in enumerate(results): # Tempo desde o último empate no histórico COMPLETO
        if result == 'draw':
            time_since_last_draw = i
            break
            
    draw_patterns_found = collections.defaultdict(int)
    for i in range(len(relevant_results) - 1):
        color1 = get_color(relevant_results[i])
        color2 = get_color(relevant_results[i+1])

        if color2 == 'yellow' and color1 != 'yellow':
            draw_patterns_found[f"Quebra para Empate ({color1.capitalize()} para Empate)"] += 1
            
        if i < len(relevant_results) - 2:
            color3 = get_color(relevant_results[i+2])
            if color3 == 'yellow':
                if color1 == 'red' and color2 == 'blue':
                    draw_patterns_found["Red-Blue-Draw"] += 1
                elif color1 == 'blue' and color2 == 'red':
                    draw_patterns_found["Blue-Red-Draw"] += 1

    # Detecção de Empate Recorrente (intervalos curtos)
    draw_indices = [i for i, r in enumerate(relevant_results) if r == 'draw']
    recurrent_draw = False
    if len(draw_indices) >= 2:
        for i in range(len(draw_indices) - 1):
            interval = draw_indices[i] - draw_indices[i+1] -1
            if 0 <= interval <= 3: # Empates em até 3 rodadas de distância
                recurrent_draw = True
                break

    return {
        'draw_frequency_27': round(draw_frequency_27, 2),
        'time_since_last_draw': time_since_last_draw,
        'draw_patterns': dict(draw_patterns_found),
        'recurrent_draw': recurrent_draw
    }

def generate_advanced_suggestion(results, surf_analysis, color_analysis, break_patterns, break_probability, draw_specifics):
    """
    Gera uma sugestão de aposta baseada em múltiplas análises usando um sistema de pontuação,
    com foco em segurança e incorporando os novos padrões. Prioriza sugestões mais fortes e evita conflitos.
    """
    if not results or len(results) < MIN_RESULTS_FOR_SUGGESTION: 
        return {'suggestion': f'Aguardando no mínimo {MIN_RESULTS_FOR_SUGGESTION} resultados para análise detalhada.', 'confidence': 0, 'reason': '', 'guarantee_pattern': 'N/A', 'bet_type': 'none'}

    last_result = results[0]
    last_result_color = get_color(last_result)
    current_streak = color_analysis['streak']
    
    bet_scores = {'home': 0, 'away': 0, 'draw': 0}
    reasons = collections.defaultdict(list)
    guarantees = collections.defaultdict(list)

    # --- Nível 1: Sugestões de Alta Confiança (Pontuação 100+) ---

    # 1. Quebra de Sequência Longa (Surf Max)
    # Se a sequência atual já atingiu ou superou o máximo histórico, há grande chance de quebra.
    if last_result_color == 'red' and surf_analysis['max_home_sequence'] > 0 and current_streak >= surf_analysis['max_home_sequence'] and current_streak >= 3:
        bet_scores['away'] += 150 # Pontuação mais alta
        reasons['away'].append(f"Sequência atual de Vermelho ({current_streak}x) atingiu ou superou o máximo histórico de surf ({surf_analysis['max_home_sequence']}x). Alta probabilidade de quebra para Azul.")
        guarantees['away'].append(f"Surf Max Quebra: {last_result_color.capitalize()}")
    elif last_result_color == 'blue' and surf_analysis['max_away_sequence'] > 0 and current_streak >= surf_analysis['max_away_sequence'] and current_streak >= 3:
        bet_scores['home'] += 150
        reasons['home'].append(f"Sequência atual de Azul ({current_streak}x) atingiu ou superou o máximo histórico de surf ({surf_analysis['max_away_sequence']}x). Alta probabilidade de quebra para Vermelho.")
        guarantees['home'].append(f"Surf Max Quebra: {last_result_color.capitalize()}")
    elif last_result_color == 'yellow' and surf_analysis['max_draw_sequence'] > 0 and current_streak >= surf_analysis['max_draw_sequence'] and current_streak >= 2:
        # Se empate atingiu o máximo, pode quebrar para qualquer lado.
        bet_scores['home'] += 100 
        bet_scores['away'] += 100
        reasons['home'].append(f"Sequência atual de Empate ({current_streak}x) atingiu ou superou o máximo histórico.")
        reasons['away'].append(f"Sequência atual de Empate ({current_streak}x) atingiu ou superou o máximo histórico.")
        guarantees['home'].append(f"Surf Max Quebra: Empate")
        guarantees['away'].append(f"Surf Max Quebra: Empate")

    # --- Nível 2: Padrões Recorrentes e Fortes (Pontuação 70-110) ---

    # 2. Padrões 2x1 e 3x1 altamente recorrentes (Indica quebra)
    for pattern, count in break_patterns.items():
        if count >= 3: # Múltiplas ocorrências do padrão
            # 2x1 patterns
            if "2x1 (Red para Blue)" in pattern and last_result_color == 'red' and current_streak == 2:
                bet_scores['away'] += 110
                reasons['away'].append(f"Padrão '{pattern.split('(')[0].strip()}' altamente recorrente ({count}x).")
                guarantees['away'].append(pattern)
            elif "2x1 (Blue para Red)" in pattern and last_result_color == 'blue' and current_streak == 2:
                bet_scores['home'] += 110
                reasons['home'].append(f"Padrão '{pattern.split('(')[0].strip()}' altamente recorrente ({count}x).")
                guarantees['home'].append(pattern)
            
            # 3x1 patterns
            elif "3x1 (Red para Blue)" in pattern and last_result_color == 'red' and current_streak == 3:
                bet_scores['away'] += 120
                reasons['away'].append(f"Padrão '{pattern.split('(')[0].strip()}' altamente recorrente ({count}x).")
                guarantees['away'].append(pattern)
            elif "3x1 (Blue para Red)" in pattern and last_result_color == 'blue' and current_streak == 3:
                bet_scores['home'] += 120
                reasons['home'].append(f"Padrão '{pattern.split('(')[0].strip()}' altamente recorrente ({count}x).")
                guarantees['home'].append(pattern)
            
            # 2x2 patterns
            elif "2x2 (Red para Blue)" in pattern and len(results) >= 2 and get_color(results[0]) == 'red' and get_color(results[1]) == 'red':
                bet_scores['away'] += 100 
                reasons['away'].append(f"Padrão '{pattern.split('(')[0].strip()}' recorrente ({count}x).")
                guarantees['away'].append(pattern)
            elif "2x2 (Blue para Red)" in pattern and len(results) >= 2 and get_color(results[0]) == 'blue' and get_color(results[1]) == 'blue':
                bet_scores['home'] += 100
                reasons['home'].append(f"Padrão '{pattern.split('(')[0].strip()}' recorrente ({count}x).")
                guarantees['home'].append(pattern)

            # 3x3 patterns (similar to 2x2, but stronger due to length)
            elif "3x3 (Red para Blue)" in pattern and len(results) >= 3 and get_color(results[0]) == 'red' and get_color(results[1]) == 'red' and get_color(results[2]) == 'red':
                bet_scores['away'] += 130 
                reasons['away'].append(f"Padrão '{pattern.split('(')[0].strip()}' altamente recorrente ({count}x).")
                guarantees['away'].append(pattern)
            elif "3x3 (Blue para Red)" in pattern and len(results) >= 3 and get_color(results[0]) == 'blue' and get_color(results[1]) == 'blue' and get_color(results[2]) == 'blue':
                bet_scores['home'] += 130
                reasons['home'].append(f"Padrão '{pattern.split('(')[0].strip()}' altamente recorrente ({count}x).")
                guarantees['home'].append(pattern)

            # Padrão Reversão/Bloco Alternado
            if "Padrão Reversão/Bloco Alternado" in pattern:
                # Extrai as cores envolvidas no padrão
                pattern_info_str = pattern.split('(')[1].replace(')', '').strip()
                # Ex: "Red Blue" -> ['Red', 'Blue']
                # Ajuste para garantir que estamos pegando as cores corretamente, ignorando emojis se houver
                pattern_colors_raw = pattern_info_str.split(' ')
                first_block_color = pattern_colors_raw[0].lower() # Ex: 'Red' -> 'red'
                second_block_color = pattern_colors_raw[1].lower() # Ex: 'Blue' -> 'blue'
                
                if len(results) >= 2:
                    current_block_color = get_color(results[0])
                    prev_block_color = get_color(results[1])
                    
                    if current_block_color == prev_block_color: # Se a sequência atual ainda é do mesmo bloco
                        if current_block_color == first_block_color and second_block_color != 'yellow':
                            bet_scores[second_block_color] += 115
                            reasons[second_block_color].append(f"Padrão '{pattern.split('(')[0].strip()}' altamente recorrente ({count}x). Espera-se a reversão para {second_block_color.capitalize()}.")
                            guarantees[second_block_color].append(pattern)
                        elif current_block_color == second_block_color and first_block_color != 'yellow':
                            bet_scores[first_block_color] += 115
                            reasons[first_block_color].append(f"Padrão '{pattern.split('(')[0].strip()}' altamente recorrente ({count}x). Espera-se a reversão para {first_block_color.capitalize()}.")
                            guarantees[first_block_color].append(pattern)

    # 3. Sugestão de Empate (se atrasado OU recorrente)
    # Empate Atrasado: Mais de 7 rodadas sem empate E baixa frequência
    if draw_specifics['time_since_last_draw'] >= 7 and draw_specifics['draw_frequency_27'] < 15: # Frequência ajustada para 15%
        bet_scores['draw'] += 80
        reasons['draw'].append(f"Empate não ocorre há {draw_specifics['time_since_last_draw']} rodadas e frequência baixa ({draw_specifics['draw_frequency_27']}% nos últimos 27).")
        guarantees['draw'].append("Empate Atrasado/Baixa Frequência")
    
    # Padrões específicos de empate (Ex: R B Y ou B R Y)
    if len(results) >= 2:
        if get_color(results[0]) == 'away' and get_color(results[1]) == 'home': # Situação atual é Home (R) -> Away (B)
            if "Red-Blue-Draw" in draw_specifics['draw_patterns']:
                bet_scores['draw'] += 95
                reasons['draw'].append(f"Padrão 'Red-Blue-Draw' detectado e recorrente ({draw_specifics['draw_patterns']['Red-Blue-Draw']}x).")
                guarantees['draw'].append("Padrão Red-Blue-Draw")
        elif get_color(results[0]) == 'home' and get_color(results[1]) == 'away': # Situação atual é Away (B) -> Home (R)
            if "Blue-Red-Draw" in draw_specifics['draw_patterns']:
                bet_scores['draw'] += 95
                reasons['draw'].append(f"Padrão 'Blue-Red-Draw' detectado e recorrente ({draw_specifics['draw_patterns']['Blue-Red-Draw']}x).")
                guarantees['draw'].append("Padrão Blue-Red-Draw")

    # 4. Empate Recorrente (intervalos curtos)
    if draw_specifics['recurrent_draw'] and draw_specifics['time_since_last_draw'] >= 0 and draw_specifics['time_since_last_draw'] <= 3: 
        bet_scores['draw'] += 85 # Um pouco mais de confiança
        reasons['draw'].append(f"Empate é recorrente, ocorrendo em intervalos curtos (último há {draw_specifics['time_since_last_draw']} rodadas).")
        guarantees['draw'].append("Empate Recorrente")

    # 5. Zig-Zag / Padrões Alternados
    for pattern, count in break_patterns.items():
        if count >= 3:
            if "Zig-Zag / Alternado" in pattern:
                if len(results) >= 2:
                    current_pattern_segment = f"{get_color(results[1]).capitalize()}-{get_color(results[0]).capitalize()}"
                    # Verifica se o padrão alternado na string bate com a sequência atual
                    # Ex: Zig-Zag (R-B-R) -> se a sequência atual é B-R, a próxima pode ser B
                    if "Red-Blue-Red" in pattern and current_pattern_segment == "Blue-Red":
                        bet_scores['away'] += 90 # Espera-se que volte para azul
                        reasons['away'].append(f"Padrão '{pattern.split('(')[0].strip()}' recorrente ({count}x). Espera-se o próximo alternado.")
                        guarantees['away'].append(pattern)
                    elif "Blue-Red-Blue" in pattern and current_pattern_segment == "Red-Blue":
                        bet_scores['home'] += 90 # Espera-se que volte para vermelho
                        reasons['home'].append(f"Padrão '{pattern.split('(')[0].strip()}' recorrente ({count}x). Espera-se o próximo alternado.")
                        guarantees['home'].append(pattern)
            
            # Padrão de Espelho
            if "Padrão Espelho" in pattern and len(results) >= 3:
                # Ex: R-B-B-R. Se temos B-B-R, esperamos o próximo R.
                # Extrair as cores do padrão para comparar
                pattern_colors_str = pattern.split('(')[1].strip(')').split('-')
                
                # Assumindo que o padrão espelho é sempre de 4 elementos para a lógica
                if len(pattern_colors_str) == 4:
                    c1_pattern = pattern_colors_str[0].lower()
                    c2_pattern = pattern_colors_str[1].lower()
                    c3_pattern = pattern_colors_str[2].lower() # Deveria ser igual a c2
                    c4_pattern = pattern_colors_str[3].lower() # Deveria ser igual a c1

                    if get_color(results[0]) == c2_pattern and \
                       get_color(results[1]) == c2_pattern and \
                       get_color(results[2]) == c1_pattern:
                        
                        if c4_pattern != 'yellow': # Não sugere empate se o espelho termina em empate
                            # Aposta na cor que completa o espelho.
                            # Se c4_pattern é 'red', a aposta é 'home'. Se é 'blue', a aposta é 'away'.
                            bet_target = 'home' if c4_pattern == 'red' else 'away'
                            bet_scores[bet_target] += 95 
                            reasons[bet_target].append(f"Padrão '{pattern.split('(')[0].strip()}' recorrente ({count}x). Espera-se o fechamento do espelho com {c4_pattern.capitalize()}.")
                            guarantees[bet_target].append(pattern)

            # --- Adição de Lógica para Padrão Escada ---
            if "Padrão Escada" in pattern and len(results) >= 3: # Precisamos de pelo menos 3 para verificar o início de uma escada
                # Ex: Padrão Escada Crescente (Red-Blue2-Yellow3)
                # Verifica se a sequência atual (os 3 últimos) pode iniciar ou continuar o padrão
                # Se o padrão é R-BB-YYY e temos Y-Y-B, a próxima seria B.
                
                pattern_colors_str = pattern.split('(')[1].strip(')').replace('1', '').replace('2', '').replace('3', '').split('-')
                
                if "Escada Crescente" in pattern and len(results) >= 2:
                    # Se o padrão é c1-c2-c3, e a sequência atual é c2 (1x) ou c3 (2x)
                    # Ex: (R-B2-Y3) - se o ultimo é B, e o penultimo é R, esperamos Y.
                    # R (antigo) -> B (atual) -> esperamos Y.
                    if len(results) >= 2 and get_color(results[1]) == pattern_colors_str[0].lower() and get_color(results[0]) == pattern_colors_str[1].lower():
                         if pattern_colors_str[2].lower() != 'yellow': # Não sugere empate se a escada termina em empate
                            bet_target = 'home' if pattern_colors_str[2].lower() == 'red' else 'away'
                            bet_scores[bet_target] += 88
                            reasons[bet_target].append(f"Padrão '{pattern.split('(')[0].strip()}' recorrente ({count}x). Próximo passo da escada crescente esperado: {pattern_colors_str[2].capitalize()}.")
                            guarantees[bet_target].append(pattern)

                elif "Escada Decrescente" in pattern and len(results) >= 2:
                    # Se o padrão é c1-c2-c3 (crescente), e temos c3 (1x) ou c2 (2x)
                    # Ex: (R3-B2-Y1) - se o ultimo é B, e o penultimo é R, esperamos Y.
                    if len(results) >= 2 and get_color(results[1]) == pattern_colors_str[0].lower() and get_color(results[0]) == pattern_colors_str[1].lower():
                        if pattern_colors_str[2].lower() != 'yellow':
                            bet_target = 'home' if pattern_colors_str[2].lower() == 'red' else 'away'
                            bet_scores[bet_target] += 88
                            reasons[bet_target].append(f"Padrão '{pattern.split('(')[0].strip()}' recorrente ({count}x). Próximo passo da escada decrescente esperado: {pattern_colors_str[2].capitalize()}.")
                            guarantees[bet_target].append(pattern)


    # --- Nível 3: Sugestões de Confiança Média (Pontuação 40-70) ---

    # 6. Alta Probabilidade de Quebra Geral (mas sem um padrão específico forte)
    # Esta sugestão só deve ser considerada se não houver uma sugestão mais forte já determinada
    if break_probability['break_chance'] > 60 and current_streak < 4:
        if len(results) >= 1:
            # Não devemos sugerir empate aqui, a não ser que o empate seja a quebra esperada.
            # Essa é uma sugestão de quebra de sequência de cor.
            if last_result_color == 'red':
                if bet_scores['away'] < 70: # Só adiciona se não houver uma sugestão mais forte de 'away'
                    bet_scores['away'] += 60 # Confiança um pouco maior
                    reasons['away'].append(f"Alta chance de quebra geral ({break_probability['break_chance']}%). Previsão de quebra da sequência de {last_result_color.capitalize()}.")
                    guarantees['away'].append("Alta Probabilidade de Quebra Geral")
            elif last_result_color == 'blue':
                if bet_scores['home'] < 70: # Só adiciona se não houver uma sugestão mais forte de 'home'
                    bet_scores['home'] += 60
                    reasons['home'].append(f"Alta chance de quebra geral ({break_probability['break_chance']}%). Previsão de quebra da sequência de {last_result_color.capitalize()}.")
                    guarantees['home'].append("Alta Probabilidade de Quebra Geral")

    # --- Reforço para Duplas Repetidas ---
    # Se a última sequência é uma dupla e o padrão "Dupla Repetida" é frequente,
    # pode ser uma boa hora para a quebra da dupla.
    if len(results) >= 2 and get_color(results[0]) == get_color(results[1]): # Se a sequência atual é uma dupla
        current_double_color = get_color(results[0])
        double_pattern_key = f"Dupla Repetida ({current_double_color.capitalize()})"
        if double_pattern_key in break_patterns and break_patterns[double_pattern_key] >= 3: # Se o padrão de dupla é recorrente
            if current_double_color == 'red' and bet_scores['away'] < 80: # Se ainda não há uma aposta forte em away
                bet_scores['away'] += 75
                reasons['away'].append(f"Padrão de 'Dupla Repetida ({current_double_color.capitalize()})' é recorrente ({break_patterns[double_pattern_key]}x) e a sequência atual é uma dupla. Alta chance de quebra.")
                guarantees['away'].append(f"Quebra de Dupla Recorrente ({current_double_color.capitalize()})")
            elif current_double_color == 'blue' and bet_scores['home'] < 80: # Se ainda não há uma aposta forte em home
                bet_scores['home'] += 75
                reasons['home'].append(f"Padrão de 'Dupla Repetida ({current_double_color.capitalize()})' é recorrente ({break_patterns[double_pattern_key]}x) e a sequência atual é uma dupla. Alta chance de quebra.")
                guarantees['home'].append(f"Quebra de Dupla Recorrente ({current_double_color.capitalize()})")
            elif current_double_color == 'yellow' and bet_scores['home'] < 80 and bet_scores['away'] < 80: # Empate duplo pode quebrar para qualquer lado
                bet_scores['home'] += 70
                bet_scores['away'] += 70
                reasons['home'].append(f"Padrão de 'Dupla Repetida ({current_double_color.capitalize()})' é recorrente ({break_patterns[double_pattern_key]}x) e a sequência atual é uma dupla. Alta chance de quebra.")
                reasons['away'].append(f"Padrão de 'Dupla Repetida ({current_double_color.capitalize()})' é recorrente ({break_patterns[double_pattern_key]}x) e a sequência atual é uma dupla. Alta chance de quebra.")
                guarantees['home'].append(f"Quebra de Dupla Recorrente ({current_double_color.capitalize()})")
                guarantees['away'].append(f"Quebra de Dupla Recorrente ({current_double_color.capitalize()})")


    # --- Determinar a Melhor Sugestão ---
    max_score = 0
    best_bet_type = 'none'

    # Itera em uma ordem preferencial: home, away, draw (para desempate de score)
    # Isso prioriza as apostas em "Casa" e "Visitante" sobre "Empate" se as pontuações forem iguais
    # e garante que a "melhor" seja escolhida.
    preferred_order = ['home', 'away', 'draw']
    for bet_type in preferred_order:
        score = bet_scores[bet_type]
        if score > max_score:
            max_score = score
            best_bet_type = bet_type
        # Se as pontuações são iguais, a ordem de preferência já cuida disso.

    final_suggestion = "Manter observação."
    final_confidence = 50
    final_reason = "Nenhum padrão de 'garantia' forte detectado nos últimos 27 resultados para uma aposta segura no momento."
    final_guarantee = "Nenhum Padrão Forte"
    
    if best_bet_type != 'none' and max_score > 0:
        final_confidence = min(100, max_score) # Limita a confiança a 100%
        
        # REMOÇÃO DOS ÍCONES DE CASA/AVIÃO/APERTO DE MÃO DA SUGESTÃO
        # A sugestão agora mostrará APENAS a bolinha colorida
        if best_bet_type == 'home':
            final_suggestion = f"APOSTAR em **CASA** {get_color_emoji('red')}"
        elif best_bet_type == 'away':
            final_suggestion = f"APOSTAR em **VISITANTE** {get_color_emoji('blue')}"
        elif best_bet_type == 'draw':
            final_suggestion = f"APOSTAR em **EMPATE** {get_color_emoji('yellow')}"
            
        # Constrói as strings de razão e garantia
        final_reason = ". ".join(sorted(list(set(reasons[best_bet_type]))))
        final_guarantee = " | ".join(sorted(list(set(guarantees[best_bet_type]))))
        
        if not final_reason: # Fallback se nenhuma razão específica foi adicionada
            final_reason = "Padrões identificados indicam alta probabilidade."
        if not final_guarantee: # Fallback se nenhuma garantia específica foi adicionada
            final_guarantee = "Padrão de pontuação geral."


    return {
        'suggestion': final_suggestion, 
        'confidence': round(final_confidence), 
        'reason': final_reason,
        'guarantee_pattern': final_guarantee,
        'bet_type': best_bet_type
    }


def update_analysis(results):
    """Coordena todas as análises e retorna os resultados consolidados."""
    
    stats = {'home': results[:NUM_RECENT_RESULTS_FOR_ANALYSIS].count('home'), 
             'away': results[:NUM_RECENT_RESULTS_FOR_ANALYSIS].count('away'), 
             'draw': results[:NUM_RECENT_RESULTS_FOR_ANALYSIS].count('draw'), 
             'total': len(results[:NUM_RECENT_RESULTS_FOR_ANALYSIS])}
    
    surf_analysis = analyze_surf(results) 
    color_analysis = analyze_colors(results)
    break_patterns = find_complex_patterns(results)
    break_probability = analyze_break_probability(results)
    draw_specifics = analyze_draw_specifics(results) 

    suggestion_data = generate_advanced_suggestion(results, surf_analysis, color_analysis, break_patterns, break_probability, draw_specifics)
    
    return {
        'stats': stats,
        'surf_analysis': surf_analysis,
        'color_analysis': color_analysis,
        'break_patterns': break_patterns,
        'break_probability': break_probability,
        'draw_specifics': draw_specifics, 
        'suggestion': suggestion_data
    }

# --- Função de Verificação de Garantia ---
def check_guarantee_status(suggested_bet_type, actual_result, guarantee_pattern):
    """
    Verifica se a aposta sugerida anteriormente (com base no padrão de garantia)
    foi bem-sucedida ou falhou.
    """
    if suggested_bet_type == 'none':
        return True # Não havia sugestão de aposta, então não falhou.

    # Um empate pode ser sugerido, mas o resultado pode ser Casa ou Fora.
    # Se a sugestão foi "draw" e o resultado foi "draw", sucesso.
    if suggested_bet_type == 'draw' and actual_result != 'draw':
        return False
    # Se a sugestão foi "home" e o resultado não foi "home", falha.
    elif suggested_bet_type == 'home' and actual_result != 'home':
        return False
    # Se a sugestão foi "away" e o resultado não foi "away", falha.
    elif suggested_bet_type == 'away' and actual_result != 'away':
        return False
    
    return True # A aposta sugerida foi bem-sucedida.


# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="Football Studio Pro Analyzer")

st.title("⚽ Football Studio Pro Analyzer")
st.write("Sistema Avançado de Análise e Predição (v3.1 - Melhorias de Padrões)") # Versão atualizada

# --- Gerenciamento de Estado (Initialização para garantir persistência) ---
# A chave aqui é inicializar essas variáveis SOMENTE se elas não existirem no st.session_state.
# Isso garante que o estado seja persistido entre as interações.
if 'results' not in st.session_state:
    st.session_state.results = []
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = update_analysis(st.session_state.results) # Inicializa com o estado atual, que pode ser vazio
if 'last_suggested_bet_type' not in st.session_state:
    st.session_state.last_suggested_bet_type = 'none'
if 'last_guarantee_pattern' not in st.session_state:
    st.session_state.last_guarantee_pattern = "N/A"
if 'guarantee_failed' not in st.session_state:
    st.session_state.guarantee_failed = False
if 'last_suggestion_confidence' not in st.session_state:
    st.session_state.last_suggestion_confidence = 0

# --- Função para Adicionar Resultado ---
def add_result(result):
    """Adiciona um resultado ao histórico e atualiza a análise."""
    # Verificar o status da aposta anterior
    if st.session_state.last_suggested_bet_type != 'none':
        st.session_state.guarantee_failed = not check_guarantee_status(
            st.session_state.last_suggested_bet_type,
            result,
            st.session_state.last_guarantee_pattern
        )
    else:
        st.session_state.guarantee_failed = False # Não houve aposta para falhar

    st.session_state.results.insert(0, result) # Adiciona o novo resultado no início da lista
    if len(st.session_state.results) > MAX_HISTORY_TO_STORE:
        st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]
    
    st.session_state.analysis_data = update_analysis(st.session_state.results)
    
    # Atualizar a última sugestão feita ANTES do novo resultado
    st.session_state.last_suggested_bet_type = st.session_state.analysis_data['suggestion']['bet_type']
    st.session_state.last_guarantee_pattern = st.session_state.analysis_data['suggestion']['guarantee_pattern']
    st.session_state.last_suggestion_confidence = st.session_state.analysis_data['suggestion']['confidence']

# --- Layout de Adição de Resultados ---
st.header("Adicionar Novo Resultado")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Casa 🔴"):
        add_result('home')
        st.toast("Resultado: Casa Adicionado!")
with col2:
    if st.button("Empate 🟡"):
        add_result('draw')
        st.toast("Resultado: Empate Adicionado!")
with col3:
    if st.button("Visitante 🔵"):
        add_result('away')
        st.toast("Resultado: Visitante Adicionado!")

st.markdown("---")

# --- Histórico de Resultados ---
st.header("Histórico dos Últimos Resultados")

if st.session_state.results:
    # Exibir os últimos 100 resultados
    display_results = st.session_state.results[:NUM_HISTORY_TO_DISPLAY]
    
    # Exibição horizontal dos emojis
    emoji_line = []
    for i, result in enumerate(display_results):
        emoji_line.append(get_color_emoji(get_color(result)))
        if (i + 1) % EMOJIS_PER_ROW == 0:
            st.markdown(" ".join(emoji_line))
            emoji_line = []
    if emoji_line: # Imprime qualquer emoji restante
        st.markdown(" ".join(emoji_line))
else:
    st.write("Nenhum resultado adicionado ainda.")

if st.button("Limpar Histórico Completo"):
    st.session_state.results = []
    st.session_state.analysis_data = update_analysis([])
    st.session_state.last_suggested_bet_type = 'none'
    st.session_state.last_guarantee_pattern = "N/A"
    st.session_state.guarantee_failed = False
    st.session_state.last_suggestion_confidence = 0
    st.experimental_rerun() # Força a atualização da UI

st.markdown("---")

# --- Análise IA e Sugestão ---
st.header("Análise IA e Sugestão")

analysis_data = st.session_state.analysis_data

st.subheader("Sugestão:")
if analysis_data['suggestion']['confidence'] == 0:
    st.warning(analysis_data['suggestion']['suggestion'])
else:
    st.markdown(f"### {analysis_data['suggestion']['suggestion']}")
    st.metric("Confiança", f"{analysis_data['suggestion']['confidence']}%")
    st.info(f"**Motivo**: {analysis_data['suggestion']['reason']}")
    st.success(f"**Padrão de Garantia**: {analysis_data['suggestion']['guarantee_pattern']}")

# Exibir status da última aposta se houver uma sugestão anterior e um novo resultado foi adicionado
if st.session_state.last_suggested_bet_type != 'none' and st.session_state.results:
    st.subheader("Status da Última Aposta Sugerida:")
    if not st.session_state.guarantee_failed:
        st.success(f"A última aposta sugerida ({st.session_state.last_suggested_bet_type.capitalize()} com {st.session_state.last_suggestion_confidence}% de confiança - Padrão: {st.session_state.last_guarantee_pattern}) FOI BEM-SUCEDIDA! 🎉")
    else:
        st.error(f"A última aposta sugerida ({st.session_state.last_suggested_bet_type.capitalize()} com {st.session_state.last_suggestion_confidence}% de confiança - Padrão: {st.session_state.last_guarantee_pattern}) FALHOU! 😢")

st.markdown("---")

# --- Detalhes da Análise ---
st.header("Detalhes da Análise dos Últimos 27 Resultados")

st.subheader("Estatísticas de Cores:")
col_stats_1, col_stats_2, col_stats_3, col_stats_4 = st.columns(4)
with col_stats_1:
    st.metric("Vermelho (Casa)", analysis_data['stats']['home'])
with col_stats_2:
    st.metric("Azul (Visitante)", analysis_data['stats']['away'])
with col_stats_3:
    st.metric("Amarelo (Empate)", analysis_data['stats']['draw'])
with col_stats_4:
    st.metric("Total", analysis_data['stats']['total'])

st.subheader("Análise de Sequências (Surf):")
st.write(f"Último resultado: **{get_color(st.session_state.results[0]).capitalize()}** (Streak: {analysis_data['color_analysis']['streak']}x)")
st.write(f"Sequência atual de Casa: {analysis_data['surf_analysis']['home_sequence']}x (Máx Histórico: {analysis_data['surf_analysis']['max_home_sequence']}x)")
st.write(f"Sequência atual de Visitante: {analysis_data['surf_analysis']['away_sequence']}x (Máx Histórico: {analysis_data['surf_analysis']['max_away_sequence']}x)")
st.write(f"Sequência atual de Empate: {analysis_data['surf_analysis']['draw_sequence']}x (Máx Histórico: {analysis_data['surf_analysis']['max_draw_sequence']}x)")

st.subheader("Padrão de Cores (Últimos 27):")
st.code(analysis_data['color_analysis']['color_pattern_27'])

st.subheader("Probabilidade de Quebra e Duplas:")
st.write(f"Chance de Quebra Geral (últimos 27): **{analysis_data['break_probability']['break_chance']}%**")
if analysis_data['break_probability']['last_break_type']:
    st.write(f"Última Quebra: {analysis_data['break_probability']['last_break_type']}")

st.subheader("Análise de Empates:")
st.write(f"Frequência de Empates (últimos 27): {analysis_data['draw_specifics']['draw_frequency_27']}%")
if analysis_data['draw_specifics']['time_since_last_draw'] != -1:
    st.write(f"Rodadas desde o Último Empate: {analysis_data['draw_specifics']['time_since_last_draw']}")
else:
    st.write("Nenhum empate nos resultados recentes.")
st.write(f"Empate Recorrente (intervalos curtos): {'Sim' if analysis_data['draw_specifics']['recurrent_draw'] else 'Não'}")
if analysis_data['draw_specifics']['draw_patterns']:
    st.write("Padrões Específicos de Empate Detectados:")
    for pattern, count in analysis_data['draw_specifics']['draw_patterns'].items():
        st.write(f"- {pattern}: {count}x")
else:
    st.write("Nenhum padrão específico de empate detectado.")

st.subheader("Padrões Complexos Detectados:")
if analysis_data['break_patterns']:
    df_patterns = pd.DataFrame(analysis_data['break_patterns'].items(), columns=['Padrão', 'Ocorrências'])
    df_patterns = df_patterns.sort_values(by='Ocorrências', ascending=False)
    st.dataframe(df_patterns, use_container_width=True)
else:
    st.write("Nenhum padrão complexo detectado nos últimos 27 resultados.")

st.markdown("---")
st.write("Desenvolvido por Gabriel V. D.")
