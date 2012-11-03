

def start_case(s):
    s = s.replace(' ', '_')
    tokens = s.split('_')
    sc_tokens = []
    for token in tokens:
        sc_tokens.append(token[0].upper() + token[1:].lower())
    return ' '.join(sc_tokens)

