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
    current_home_sequence = 0
    current_away_sequence = 0
    current_draw_sequence = 0
    
    if results:
        # Pega o primeiro resultado para determinar a cor da sequência atual
        first_result_current_analysis = results[0] 
        for r in results: 
            if r == first_result_current_analysis:
                if first_result_current_analysis == 'home': 
                    current_home_sequence += 1
                elif first_result_current_analysis == 'away': 
                    current_away_sequence += 1
                else: # draw
                    current_draw_sequence += 1
            else:
                break # A sequência atual foi interrompida
    
    max_home_sequence = 0
    max_away_sequence = 0
    max_draw_sequence = 0
    
    temp_home_seq = 0
    temp_away_seq = 0
    temp_draw_seq = 0

    # Itera sobre todos os resultados para encontrar as sequências máximas históricas
    for res in results: 
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
        'current_home_sequence': current_home_sequence, 
        'current_away_sequence': current_away_sequence, 
        'current_draw_sequence': current_draw_sequence, 
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
    for result in results: 
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
    nos últimos N resultados, incluindo o Padrão Escada.
    """
    patterns = collections.defaultdict(int)
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]

    colors = [get_color(r) for r in relevant_results]

    for i in range(len(colors) - 1):
        color1 = colors[i]
        color2 = colors[i+1]

        if color1 != color2:
            patterns[f"Quebra Simples ({color1.capitalize()} para {color2.capitalize()})"] += 1

        if i < len(colors) - 2:
            color3 = colors[i+2]
            
            if color1 == color2 and color1 != color3:
                patterns[f"2x1 ({color1.capitalize()} para {color3.capitalize()})"] += 1
            
            if color1 != color2 and color2 != color3 and color1 == color3:
                patterns[f"Zig-Zag / Alternado ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()})"] += 1
            
            if color2 == 'yellow' and color1 != 'yellow' and color3 != 'yellow' and color1 != color3:
                patterns[f"Alternância c/ Empate no Meio ({color1.capitalize()}-Empate-{color3.capitalize()})"] += 1

        if i < len(colors) - 3:
            color3 = colors[i+2]
            color4 = colors[i+3]

            if color1 == color2 and color2 == color3 and color1 != color4:
                patterns[f"3x1 ({color1.capitalize()} para {color4.capitalize()})"] += 1
            
            if color1 == color2 and color3 == color4 and color1 != color3:
                patterns[f"2x2 ({color1.capitalize()} para {color3.capitalize()})"] += 1
            
            if color1 != color2 and color2 == color3 and color1 == color4:
                patterns[f"Padrão Espelho ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()}-{color4.capitalize()})"] += 1
            
            if color1 != color2 and color2 == color3 and color3 != color4 and color1 == color4:
                patterns[f"Padrão Onda 1-2-1 ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()}-{color4.capitalize()})"] += 1

        if i < len(colors) - 5:
            color3 = colors[i+2]
            color4 = colors[i+3]
            color5 = colors[i+4]
            color6 = colors[i+5]

            if color1 == color2 and color2 == color3 and color4 == color5 and color5 == color6 and color1 != color4:
                patterns[f"3x3 ({color1.capitalize()} para {color4.capitalize()})"] += 1

    for i in range(len(colors) - 1):
        if colors[i] == colors[i+1]:
            patterns[f"Dupla Repetida ({colors[i].capitalize()})"] += 1
            
    if len(colors) >= 4:
        for block_size in [2, 3]: 
            if len(colors) >= 2 * block_size:
                block1 = colors[0:block_size]
                block2 = colors[block_size:2*block_size]
                
                if all(c == block1[0] for c in block1) and \
                   all(c == block2[0] for c in block2) and \
                   block1[0] != block2[0]:
                    
                    if len(colors) >= 4 * block_size: 
                        block3 = colors[2*block_size:3*block_size]
                        block4 = colors[3*block_size:4*block_size]
                        if all(c == block3[0] for c in block3) and \
                           all(c == block4[0] for c in block4) and \
                           block1[0] == block3[0] and \
                           block2[0] == block4[0]:
                            patterns[f"Padrão Bloco Alternado {block_size}x{block_size} ({block1[0].capitalize()}-{block2[0].capitalize()})"] += 1
                    else: 
                        patterns[f"Padrão Bloco {block_size}x{block_size} ({block1[0].capitalize()}-{block2[0].capitalize()})"] += 1
    
    # Padrão Escada Crescente 1-2-3
    if len(colors) >= 6: 
        if (colors[0] == colors[2] and colors[2] == colors[3] and colors[3] == colors[4] and 
            colors[1] != colors[0] and colors[1] != colors[5] and colors[5] != colors[0] and 
            colors[0] == colors[5]): 
            patterns[f"Padrão Escada Crescente 1-2-3 ({colors[0].capitalize()}-{colors[1].capitalize()}-{colors[0].capitalize()})"] += 1

    # Padrão Escada Decrescente 3-2-1
    if len(colors) >= 6: 
        if (colors[0] == colors[1] and colors[1] == colors[2] and 
            colors[3] == colors[4] and colors[3] != colors[0] and 
            colors[5] != colors[3] and colors[5] == colors[0]): 
            patterns[f"Padrão Escada Decrescente 3-2-1 ({colors[0].capitalize()}-{colors[3].capitalize()}-{colors[5].capitalize()})"] += 1

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
        total_sequences_considered += 1 # Conta cada transição como uma sequência considerada
            
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
    for i, result in enumerate(results): 
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

    recurrent_draw = False
    if draw_count_27 > 1: 
        draw_indices = [i for i, r in enumerate(relevant_results) if r == 'draw']
        
        if len(draw_indices) >= 2:
            intervals = []
            for i in range(1, len(draw_indices)):
                intervals.append(abs(draw_indices[i-1] - draw_indices[i])) 
            
            # Se a maioria dos intervalos entre empates for 5 ou menos
            if intervals and sum(1 for x in intervals if x <= 5) / len(intervals) >= 0.6: 
                recurrent_draw = True

    return {
        'draw_frequency_27': round(draw_frequency_27, 2),
        'time_since_last_draw': time_since_last_draw,
        'draw_patterns': dict(draw_patterns_found),
        'recurrent_draw': recurrent_draw
    }

def generate_advanced_suggestion(results, surf_analysis, color_analysis, complex_patterns, break_probability, draw_specifics):
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

    # --- Definição do Limiar de "Surf Longo/Crítico" ---
    MIN_CRITICAL_SURF_THRESHOLD = 7 

    # --- Pontuação para Continuação de Surf (a partir de 4x até o limiar crítico) ---
    # Prioriza continuar o surf se ele não atingiu o ponto de "alto risco de quebra"
    if current_streak >= 4 and current_streak < MIN_CRITICAL_SURF_THRESHOLD:
        score_for_continuation = 60 # Pontos base para seguir o surf
        # Aumenta a pontuação progressivamente: 4x=60, 5x=70, 6x=80
        score_for_continuation += (current_streak - 4) * 10 

        if last_result_color == 'red':
            bet_scores['home'] += score_for_continuation
            reasons['home'].append(f"Continuação de Surf: Vermelho em sequência de {current_streak}x. Seguir a tendência observada.")
            guarantees['home'].append(f"Continuação de Surf ({last_result_color.capitalize()})")
        elif last_result_color == 'blue':
            bet_scores['away'] += score_for_continuation
            reasons['away'].append(f"Continuação de Surf: Azul em sequência de {current_streak}x. Seguir a tendência observada.")
            guarantees['away'].append(f"Continuação de Surf ({last_result_color.capitalize()})")
        # Para Empate, não "surfamos" ativamente, pois aposta é mais específica.

    # --- Pontuação para Quebra de Surf (Surf Longo/Crítico ou Recorde Histórico) ---
    # Só adicionamos pontos para quebra se a sequência atingiu o limiar crítico OU o máximo histórico
    if last_result_color == 'red':
        if current_streak >= MIN_CRITICAL_SURF_THRESHOLD: 
            # Verifica se já há uma pontuação alta para quebra para não somar desnecessariamente
            if bet_scores['away'] < 130: 
                bet_scores['away'] = max(bet_scores['away'], 130) # Garante que seja pelo menos 130
            reasons['away'].append(f"ALERTA DE QUEBRA: Sequência de Vermelho excepcionalmente longa ({current_streak}x). Forte sugestão de quebra para Azul.")
            guarantees['away'].append(f"Quebra de Surf Longo ({last_result_color.capitalize()})")
        if surf_analysis['max_home_sequence'] > 0 and current_streak >= surf_analysis['max_home_sequence'] and current_streak >= 4: 
            # Garante que essa pontuação (150) sobrescreva ou seja adicionada corretamente
            if bet_scores['away'] < 150: # Se já pontuou 130, garante que a nova pontuação seja 150
                bet_scores['away'] = max(bet_scores['away'], 150)
            reasons['away'].append(f"ALERTA MÁXIMO DE QUEBRA: Sequência de Vermelho ({current_streak}x) atingiu/superou o máximo histórico ({surf_analysis['max_home_sequence']}x).")
            guarantees['away'].append(f"Quebra de Surf Recorde ({last_result_color.capitalize()})")

    elif last_result_color == 'blue':
        if current_streak >= MIN_CRITICAL_SURF_THRESHOLD: 
            if bet_scores['home'] < 130:
                bet_scores['home'] = max(bet_scores['home'], 130)
            reasons['home'].append(f"ALERTA DE QUEBRA: Sequência de Azul excepcionalmente longa ({current_streak}x). Forte sugestão de quebra para Vermelho.")
            guarantees['home'].append(f"Quebra de Surf Longo ({last_result_color.capitalize()})")
        if surf_analysis['max_away_sequence'] > 0 and current_streak >= surf_analysis['max_away_sequence'] and current_streak >= 4: 
            if bet_scores['home'] < 150:
                bet_scores['home'] = max(bet_scores['home'], 150)
            reasons['home'].append(f"ALERTA MÁXIMO DE QUEBRA: Sequência de Azul ({current_streak}x) atingiu/superou o máximo histórico ({surf_analysis['max_away_sequence']}x).")
            guarantees['home'].append(f"Quebra de Surf Recorde ({last_result_color.capitalize()})")

    # Para Empate, a lógica de quebra é a mesma, mas não temos uma aposta "seguir empate" primária forte aqui
    elif last_result_color == 'yellow' and surf_analysis['max_draw_sequence'] > 0 and current_streak >= surf_analysis['max_draw_sequence'] and current_streak >= 2:
        # A pontuação para quebra de empate é distribuída, não diretamente para uma cor.
        bet_scores['home'] += 80 
        bet_scores['away'] += 80
        reasons['home'].append(f"Quebra de Surf: Sequência atual de Empate ({current_streak}x) atingiu ou superou o máximo histórico.")
        reasons['away'].append(f"Quebra de Surf: Sequência atual de Empate ({current_streak}x) atingiu ou superou o máximo histórico.")
        guarantees['home'].append(f"Quebra de Surf Max (Empate)")
        guarantees['away'].append(f"Quebra de Surf Max (Empate)")

    # --- Nível 2: Padrões Recorrentes e Fortes (Pontuação 70-130) ---
    # 2. Reação a Quebra Recente (Se houve quebra, e o próximo resultado é o esperado pela quebra)
    if break_probability['last_break_type'] and len(results) >= 2:
        if "Quebrou de " in break_probability['last_break_type']:
            parts = break_probability['last_break_type'].split(' para ')
            if len(parts) == 2:
                to_color = parts[1].lower()
                
                if to_color == 'red':
                    bet_scores['home'] += 50
                    reasons['home'].append(f"Aposta a favor da recente quebra de tendência: {break_probability['last_break_type']}.")
                elif to_color == 'blue':
                    bet_scores['away'] += 50
                    reasons['away'].append(f"Aposta a favor da recente quebra de tendência: {break_probability['last_break_type']}.")

    # 3. Padrões de Quebra Específicos (2x1, 3x1, 2x2, 3x3) - Se há 3+ ocorrências e o cenário é o esperado
    for pattern, count in complex_patterns.items():
        if count >= 3: 
            # Padrões Xx1
            if "2x1 (Red para Blue)" in pattern and last_result_color == 'red' and current_streak == 2:
                bet_scores['away'] += 100
                reasons['away'].append(f"Padrão '{pattern}' (2x1) recorrente ({count}x). Sugere quebra para Azul.")
                guarantees['away'].append(pattern)
            elif "2x1 (Blue para Red)" in pattern and last_result_color == 'blue' and current_streak == 2:
                bet_scores['home'] += 100
                reasons['home'].append(f"Padrão '{pattern}' (2x1) recorrente ({count}x). Sugere quebra para Vermelho.")
                guarantees['home'].append(pattern)
            
            elif "3x1 (Red para Blue)" in pattern and last_result_color == 'red' and current_streak == 3:
                bet_scores['away'] += 120
                reasons['away'].append(f"Padrão '{pattern}' (3x1) altamente recorrente ({count}x). Forte sugestão de quebra para Azul.")
                guarantees['away'].append(pattern)
            elif "3x1 (Blue para Red)" in pattern and last_result_color == 'blue' and current_streak == 3:
                bet_scores['home'] += 120
                reasons['home'].append(f"Padrão '{pattern}' (3x1) altamente recorrente ({count}x). Forte sugestão de quebra para Vermelho.")
                guarantees['home'].append(pattern)
            
            # Padrões XxX (Aposta na Continuação ou Quebra do Padrão)
            if len(results) >= 4: 
                r0, r1, r2, r3 = [get_color(x) for x in results[:4]]
                if pattern == "2x2 (Red para Blue)" and r0 == 'red' and r1 == 'red' and r2 == 'blue' and r3 == 'blue':
                    bet_scores['red'] += 90 
                    reasons['red'].append(f"Padrão '{pattern}' (2x2) recorrente ({count}x). Pode repetir a sequência 'Red Red'.")
                    guarantees['red'].append(pattern)
                elif pattern == "2x2 (Blue para Red)" and r0 == 'blue' and r1 == 'blue' and r2 == 'red' and r3 == 'red':
                    bet_scores['blue'] += 90 
                    reasons['blue'].append(f"Padrão '{pattern}' (2x2) recorrente ({count}x). Pode repetir a sequência 'Blue Blue'.")
                    guarantees['blue'].append(pattern)
            
            if len(results) >= 6: 
                r0, r1, r2, r3, r4, r5 = [get_color(x) for x in results[:6]]
                if pattern == "3x3 (Red para Blue)" and r0 == 'red' and r1 == 'red' and r2 == 'red' and r3 == 'blue' and r4 == 'blue':
                    bet_scores['blue'] += 110 
                    reasons['blue'].append(f"Padrão '{pattern}' (3x3) recorrente ({count}x). Pode continuar a sequência 'Blue Blue Blue'.")
                    guarantees['blue'].append(pattern)
                elif pattern == "3x3 (Blue para Red)" in pattern and r0 == 'blue' and r1 == 'blue' and r2 == 'blue' and r3 == 'red' and r4 == 'red':
                    bet_scores['red'] += 110
                    reasons['red'].append(f"Padrão '{pattern}' (3x3) recorrente ({count}x). Pode continuar a sequência 'Red Red Red'.")
                    guarantees['red'].append(pattern)

            if "Padrão Bloco Alternado" in pattern:
                parts = pattern.split('(')[1].replace(')', '').split('-')
                color_block1 = parts[0].lower()
                color_block2 = parts[1].lower()
                block_size = int(pattern.split('x')[0].split(' ')[-1])

                if len(results) >= block_size:
                    current_block = [get_color(r) for r in results[0:block_size]]
                    if all(c == color_block1 for c in current_block) and current_streak == block_size:
                        if color_block2 == 'red': bet_scores['home'] += 100
                        elif color_block2 == 'blue': bet_scores['away'] += 100
                        reasons[color_block2].append(f"Padrão '{pattern}' detectado. Espera-se a continuação do ciclo com {color_block2.capitalize()}.")
                        guarantees[color_block2].append(pattern)
                    elif all(c == color_block2 for c in current_block) and current_streak == block_size:
                        if color_block1 == 'red': bet_scores['home'] += 100
                        elif color_block1 == 'blue': bet_scores['away'] += 100
                        reasons[color_block1].append(f"Padrão '{pattern}' detectado. Espera-se a continuação do ciclo com {color_block1.capitalize()}.")
                        guarantees[color_block1].append(pattern)

    # 4. Zig-Zag / Padrão Alternado (Quando o último resultado sugere continuação do Zig-Zag)
    if "Zig-Zag / Alternado" in complex_patterns: 
        if len(results) >= 2:
            r0_color = get_color(results[0])
            r1_color = get_color(results[1])
            if r0_color != r1_color: 
                expected_next_color = r1_color 
                if expected_next_color == 'red':
                    bet_scores['home'] += 90
                    reasons['home'].append(f"Padrão Zig-Zag / Alternado detectado. Espera-se Vermelho para continuar o padrão.")
                    guarantees['home'].append("Zig-Zag Continuação")
                elif expected_next_color == 'blue':
                    bet_scores['away'] += 90
                    reasons['away'].append(f"Padrão Zig-Zag / Alternado detectado. Espera-se Azul para continuar o padrão.")
                    guarantees['away'].append("Zig-Zag Continuação")

    # 5. Padrão Espelho / Onda 1-2-1 (Se o padrão está incompleto e sugere uma aposta clara)
    for pattern in ["Padrão Espelho", "Padrão Onda 1-2-1"]:
        if pattern in complex_patterns:
            if len(results) >= 3: 
                r0_color = get_color(results[0])
                r1_color = get_color(results[1])
                r2_color = get_color(results[2])
                
                if r0_color == r1_color and r0_color != r2_color: 
                    if r0_color == 'blue':
                        bet_scores['blue'] += 80
                        reasons['blue'].append(f"Padrão '{pattern}' incompleto. Espera-se Azul para completar a simetria.")
                        guarantees['blue'].append(pattern + " Incompleto")
                    elif r0_color == 'red':
                        bet_scores['red'] += 80
                        reasons['red'].append(f"Padrão '{pattern}' incompleto. Espera-se Vermelho para completar a simetria.")
                        guarantees['red'].append(pattern + " Incompleto")

    # Padrão Escada
    if "Padrão Escada Crescente 1-2-3" in complex_patterns and len(results) >= 5: 
        r0, r1, r2, r3, r4 = [get_color(x) for x in results[:5]]
        if r0 == r1 and r1 != r2 and r2 == r3 and r3 == r4: 
             if r0 == 'red':
                 bet_scores['red'] += 100
                 reasons['red'].append(f"Padrão Escada Crescente 1-2-3 detectado. Forte sugestão de Vermelho para completar o bloco de 3.")
                 guarantees['red'].append("Padrão Escada 1-2-3")
             elif r0 == 'blue':
                 bet_scores['blue'] += 100
                 reasons['blue'].append(f"Padrão Escada Crescente 1-2-3 detectado. Forte sugestão de Azul para completar o bloco de 3.")
                 guarantees['blue'].append("Padrão Escada 1-2-3")
    
    if "Padrão Escada Decrescente 3-2-1" in complex_patterns and len(results) >= 5: 
        r0, r1, r2, r3, r4 = [get_color(x) for x in results[:5]]
        if r0 == r1 and r1 == r2 and r2 != r3 and r3 == r4: 
            if r3 == 'red':
                bet_scores['red'] += 100
                reasons['red'].append(f"Padrão Escada Decrescente 3-2-1 detectado. Forte sugestão de Vermelho para completar o bloco de 2.")
                guarantees['red'].append("Padrão Escada 3-2-1")
            elif r3 == 'blue':
                bet_scores['blue'] += 100
                reasons['blue'].append(f"Padrão Escada Decrescente 3-2-1 detectado. Forte sugestão de Azul para completar o bloco de 2.")
                guarantees['blue'].append("Padrão Escada 3-2-1")


    # --- Nível 3: Análise de Frequência e Probabilidade (Pontuação 30-70) ---

    # 6. Frequência de Cores Recentes (Desequilíbrio de curto prazo)
    total_relevant = color_analysis['red'] + color_analysis['blue'] + color_analysis['yellow']
    if total_relevant > 0:
        red_pct = (color_analysis['red'] / total_relevant) * 100
        blue_pct = (color_analysis['blue'] / total_relevant) * 100

        if red_pct < 40 and blue_pct > 55: 
            bet_scores['home'] += 40
            reasons['home'].append(f"Desequilíbrio recente: Vermelho ({red_pct:.1f}%) está sub-representado nos últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS} resultados.")
        elif blue_pct < 40 and red_pct > 55: 
            bet_scores['away'] += 40
            reasons['away'].append(f"Desequilíbrio recente: Azul ({blue_pct:.1f}%) está sub-representado nos últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS} resultados.")
    
    # 7. Empate Recorrente / Empate "Atrasado"
    if draw_specifics['recurrent_draw']:
        # Pontuação ligeiramente reduzida para 60 para não dominar outras sugestões fortes.
        bet_scores['draw'] += 60 
        reasons['draw'].append(f"Empate Recorrente: Padrão de empates em intervalos curtos detectado.")
        guarantees['draw'].append("Empate Recorrente")
    
    if draw_specifics['time_since_last_draw'] != -1 and draw_specifics['time_since_last_draw'] >= 15:
        bet_scores['draw'] += 50
        reasons['draw'].append(f"Empate 'Atrasado': {draw_specifics['time_since_last_draw']} rodadas sem empate. Probabilidade crescente.")
        guarantees['draw'].append("Empate Atrasado")

    # --- Determinar a Sugestão Final ---
    
    max_score = 0
    suggested_bet_type = 'none'
    
    for bet_type, score in bet_scores.items():
        if score > max_score:
            max_score = score
            suggested_bet_type = bet_type
        # Em caso de empate de pontuação, prioriza Casa/Visitante sobre Empate, e Casa sobre Visitante (arbitrário, pode ser ajustado)
        elif score == max_score:
            if suggested_bet_type == 'draw' and bet_type != 'draw': 
                max_score = score
                suggested_bet_type = bet_type
            elif suggested_bet_type == 'away' and bet_type == 'home': 
                max_score = score
                suggested_bet_type = bet_type

    if suggested_bet_type == 'none' or max_score < 30: 
        return {'suggestion': 'Manter Observação', 'confidence': 0, 'reason': 'Nenhum padrão forte ou combinação de padrões detectada.', 'guarantee_pattern': 'N/A', 'bet_type': 'none'}

    # Concatena todas as razões para a sugestão final
    final_reason = " ".join(reasons[suggested_bet_type])
    final_guarantee = ", ".join(guarantees[suggested_bet_type])

    confidence = min(95, max(0, int(max_score * 0.6))) # Ajusta a confiança para ser entre 0-95%

    return {
        'suggestion': suggested_bet_type.upper(),
        'confidence': confidence,
        'reason': final_reason,
        'guarantee_pattern': final_guarantee if final_guarantee else 'N/A',
        'bet_type': suggested_bet_type
    }

def check_guarantee_status(latest_result, suggested_bet_type, guarantee_pattern):
    """Verifica se a aposta sugerida pelo 'guarantee_pattern' foi bem-sucedida."""
    if suggested_bet_type == 'none' or guarantee_pattern == 'N/A' or not latest_result:
        return {'status': 'N/A', 'message': ''}

    latest_result_color = get_color(latest_result)
    
    if suggested_bet_type == latest_result_color:
        return {'status': 'SUCESSO', 'message': f"Aposta em {suggested_bet_type.upper()} foi bem-sucedida!"}
    else:
        return {'status': 'FALHA', 'message': f"Aposta em {suggested_bet_type.upper()} falhou. Resultado foi {latest_result.upper()}."}

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="Analisador de Football Studio IA")

st.title("⚽ Football Studio Analisador Inteligente 🃏")

# Inicialização do estado da sessão
if 'results' not in st.session_state:
    st.session_state.results = []
if 'last_suggestion' not in st.session_state:
    st.session_state.last_suggestion = {'suggestion': 'N/A', 'bet_type': 'none', 'guarantee_pattern': 'N/A'}
if 'guarantee_status' not in st.session_state:
    st.session_state.guarantee_status = {'status': 'N/A', 'message': ''}

st.sidebar.header("Adicionar Novo Resultado")
col1, col2, col3 = st.sidebar.columns(3)
if col1.button("Casa 🔴"):
    st.session_state.results.insert(0, 'home')
    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]
    if st.session_state.last_suggestion['bet_type'] != 'none':
        st.session_state.guarantee_status = check_guarantee_status('home', st.session_state.last_suggestion['bet_type'], st.session_state.last_suggestion['guarantee_pattern'])
    st.rerun()
if col2.button("Visitante 🔵"):
    st.session_state.results.insert(0, 'away')
    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]
    if st.session_state.last_suggestion['bet_type'] != 'none':
        st.session_state.guarantee_status = check_guarantee_status('away', st.session_state.last_suggestion['bet_type'], st.session_state.last_suggestion['guarantee_pattern'])
    st.rerun()
if col3.button("Empate 🟡"):
    st.session_state.results.insert(0, 'draw')
    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]
    if st.session_state.last_suggestion['bet_type'] != 'none':
        st.session_state.guarantee_status = check_guarantee_status('draw', st.session_state.last_suggestion['bet_type'], st.session_state.last_suggestion['guarantee_pattern'])
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("Limpar Histórico"):
    st.session_state.results = []
    st.session_state.last_suggestion = {'suggestion': 'N/A', 'bet_type': 'none', 'guarantee_pattern': 'N/A'}
    st.session_state.guarantee_status = {'status': 'N/A', 'message': ''}
    st.rerun()

# Exibe o status da última aposta no sidebar
if st.session_state.guarantee_status['status'] == 'SUCESSO':
    st.sidebar.success(f"✅ Última Aposta: {st.session_state.guarantee_status['message']}")
elif st.session_state.guarantee_status['status'] == 'FALHA':
    st.sidebar.error(f"❌ Última Aposta: {st.session_state.guarantee_status['message']}")
else:
    st.sidebar.info("Aguardando sugestão para verificar status da garantia.")


st.header("Histórico dos Últimos Resultados")
if st.session_state.results:
    displayed_results = st.session_state.results[:NUM_HISTORY_TO_DISPLAY]
    
    emoji_lines = []
    current_line = ""
    for i, result in enumerate(displayed_results):
        color = get_color(result)
        emoji = get_color_emoji(color)
        current_line += emoji
        if (i + 1) % EMOJIS_PER_ROW == 0:
            emoji_lines.append(current_line)
            current_line = ""
    if current_line: # Adiciona a última linha se não estiver completa
        emoji_lines.append(current_line)
    
    for line in emoji_lines:
        st.markdown(f"#### {line}") 
else:
    st.info("Nenhum resultado adicionado ainda.")

st.header("Análise IA e Sugestão")

if len(st.session_state.results) >= MIN_RESULTS_FOR_SUGGESTION:
    # Executa todas as análises
    surf_analysis_data = analyze_surf(st.session_state.results)
    color_analysis_data = analyze_colors(st.session_state.results)
    complex_patterns_data = find_complex_patterns(st.session_state.results)
    break_probability_data = analyze_break_probability(st.session_state.results)
    draw_specifics_data = analyze_draw_specifics(st.session_state.results)

    # Gera a sugestão avançada com base em TODAS as análises
    suggestion_output = generate_advanced_suggestion(
        st.session_state.results,
        surf_analysis_data,
        color_analysis_data,
        complex_patterns_data,
        break_probability_data,
        draw_specifics_data
    )

    # Armazena a última sugestão para verificar a garantia
    st.session_state.last_suggestion = {
        'suggestion': suggestion_output['suggestion'],
        'bet_type': suggestion_output['bet_type'],
        'guarantee_pattern': suggestion_output['guarantee_pattern']
    }

    # Exibe a sugestão e seus detalhes
    if suggestion_output['bet_type'] == 'home':
        st.success(f"**Sugestão:** Apostar em CASA {get_color_emoji('red')} (Confiança: {suggestion_output['confidence']}%)")
    elif suggestion_output['bet_type'] == 'away':
        st.success(f"**Sugestão:** Apostar em VISITANTE {get_color_emoji('blue')} (Confiança: {suggestion_output['confidence']}%)")
    elif suggestion_output['bet_type'] == 'draw':
        st.warning(f"**Sugestão:** Apostar em EMPATE {get_color_emoji('yellow')} (Confiança: {suggestion_output['confidence']}%)")
    else:
        st.info(f"**Sugestão:** {suggestion_output['suggestion']}")
    
    st.markdown(f"**Motivo:** {suggestion_output['reason']}")
    st.markdown(f"**Padrão de Garantia:** {suggestion_output['guarantee_pattern']}")

    st.subheader("Detalhes da Análise:")
    
    # Exibe detalhes de cada análise para depuração e informação
    st.write("---")
    st.markdown("##### Análise de Surf (Sequências):")
    st.write(f"- Sequência Atual Home: {surf_analysis_data['current_home_sequence']} (Max: {surf_analysis_data['max_home_sequence']})")
    st.write(f"- Sequência Atual Away: {surf_analysis_data['current_away_sequence']} (Max: {surf_analysis_data['max_away_sequence']})")
    st.write(f"- Sequência Atual Draw: {surf_analysis_data['current_draw_sequence']} (Max: {surf_analysis_data['max_draw_sequence']})")

    st.write("---")
    st.markdown("##### Contagem de Cores (Últimos 27):")
    st.write(f"- Vermelho (Casa): {color_analysis_data['red']} ({color_analysis_data['red']/NUM_RECENT_RESULTS_FOR_ANALYSIS*100:.1f}%)")
    st.write(f"- Azul (Visitante): {color_analysis_data['blue']} ({color_analysis_data['blue']/NUM_RECENT_RESULTS_FOR_ANALYSIS*100:.1f}%)")
    st.write(f"- Amarelo (Empate): {color_analysis_data['yellow']} ({color_analysis_data['yellow']/NUM_RECENT_RESULTS_FOR_ANALYSIS*100:.1f}%)")
    st.write(f"- Padrão de Cores Recentes: {color_analysis_data['color_pattern_27']}")

    st.write("---")
    st.markdown("##### Padrões Complexos Detectados:")
    if complex_patterns_data:
        for pattern, count in complex_patterns_data.items():
            st.write(f"- {pattern}: {count} ocorrências")
    else:
        st.write("Nenhum padrão complexo detectado recentemente.")

    st.write("---")
    st.markdown("##### Probabilidade de Quebra:")
    st.write(f"- Chance de Quebra (últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS} resultados): {break_probability_data['break_chance']}%")
    st.write(f"- Último Tipo de Quebra: {break_probability_data['last_break_type']}")

    st.write("---")
    st.markdown("##### Análise de Empates:")
    st.write(f"- Frequência de Empates (últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS} resultados): {draw_specifics_data['draw_frequency_27']}%")
    st.write(f"- Tempo desde o Último Empate: {draw_specifics_data['time_since_last_draw']} rodadas")
    st.write(f"- Empate Recorrente Detectado: {'Sim' if draw_specifics_data['recurrent_draw'] else 'Não'}")
    if draw_specifics_data['draw_patterns']:
        st.write("- Padrões de Empate Específicos:")
        for pattern, count in draw_specifics_data['draw_patterns'].items():
            st.write(f"  - {pattern}: {count} ocorrências")
else:
    st.info(f"Adicione mais {MIN_RESULTS_FOR_SUGGESTION - len(st.session_state.results)} resultados para iniciar a análise.")

