import re

def minimal_maat_to_llama_input(maat_text: str, to_fill_gap_index: int) -> str:
    # remove newlines
    # maat_text = maat_text.replace('\n', '')
    maat_text = initial_cleanup(maat_text)
    maat_text = strip_accents_and_breathing(maat_text)
    maat_text = mask_emendations(maat_text)
    maat_text = convert_dot_gaps_to_lines(maat_text, to_fill_gap_index)
    maat_text = convert_unbracketed_gaps_to_lines(maat_text)
    maat_text = simplify_punctuation(maat_text)
    
    return maat_text



# https://github.com/ericu9500/PapyriAndInscriptions/blob/9b90f2133975dc57b34f56aefe734fd986cb1eb6/train_data/02_clean%20papyri_with_emendations.py
def initial_cleanup(text: str) -> str:
    text = text.replace("€€ ", "").replace(" €€", "").replace("€€", "").replace(" ,", ",").replace("\"", "").replace("#", "")
    
    replacements = [
        (r'[\n ]+', ' '),
#        (r'[ﬂⲁⲂⲃⲅⲇⲉⲋⲍⲏⲑ\?ⲓⲕⲗöﬁ\／ⲙⲛⲝⲟⲡⲣⲥⲧⲩⲫⲭⲯⲱⲻⳉⳓ⳨⳿⸌⸍⸗ꜢꜣꜤꜥ⟦⤚⦿⟧●⎛⎜⎝⎞⎟⎠⎧⎨⎩⎫⎬⎭بةتث!"#$&<=>ß@ABC῎῾῏῞῟DEF‘’‚“”„GHIJKLMNOPQRSTUVWXYZ§¨±_abcdefghijklmnopqrstuvwxyz\{\|\}\~áâäçéìíîïòóôõúüıšʹʼʽˉ˙̱̀́̃̅̇̈̉̒̓̔͂͗ͅ]', ''),  # Remove special characters
        (r'[›※‾⁓⁢⁩­ ‪–—―‖]', ' '),
        (r'[-]', '-'),
        (r'[0-9]', ''),
        (r'[]', 'ε'),
        (r'[]', 'η'),
        (r'[∂θϑ]', 'θ'),
        (r'[􏰂]', 'ι'),
        (r'[]', 'ο'),
        (r'[὘]', 'υ'),
        (r'[µ]', 'μ'),
        (r'[ϕ]', 'φ'),
        (r'[]', 'ω'),
        (r'[\n]', ' '),
        (r'[ϢϣϥϨϩ⁦ϪϫϬϭ𐅵ϮϯϲϹׂء􏰁أؤإئابةتثجحخدذرزسشصضطعغـفقكụلمنهوىيٍّپᐧḍḎḏḤḥḪḫṃṭṯṱẖẠẹỈỉ]', '')
    ]
    
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    
    return text

# https://github.com/ericu9500/PapyriAndInscriptions/blob/9b90f2133975dc57b34f56aefe734fd986cb1eb6/train_data/05_normalize.py
def strip_accents_and_breathing(text: str) -> str:
    # remove accents and breathing
    # remove trailing sigma
    # remove capitalisation
    replacement_map = {
        'ἋΆΑάαἀἁἂἃἄἅἆἈἉἊἌἍἎἏὰᾁᾈᾲᾳᾴᾶᾷᾼ': 'α',
        'Ββ': 'β',
        'Γγ': 'γ',
        'Δδ∆': 'δ',
        'ΈΕὲέέέεἐἑἒἓἔἕἘἙἛἜἝ\u1F73': 'ε',
        'Ζζ': 'ζ',
        'ΗήηἠἡἢἣἤἥἦἧἨἩἫἬἭἮὴᾐᾑᾒᾓᾔᾕᾖᾗῂῃῄῆῇ': 'η',
        'Θθ': 'θ',
        'ΙΊΐίιϊἰἱἲἳἴἵἶἷἸἹἼἽἾὶῑῒῖῗ': 'ι',
        'Κκ': 'κ',
        'Λλ': 'λ',
        'Μμ': 'μ',
        'Νν': 'ν',
        'Ξξ': 'ξ',
        'ΟοόὀὁὂὃὄὅὈὉὊὋὌὍὸόό\u1F79': 'ο',
        'Ππ': 'π',
        'ΡρῤῥῬ': 'ρ',
        'Σςσ': 'σ',
        'Ττ': 'τ',
        'ΥΰυϋύὐὑὓὔὕὖὗὙὝὺῢῦῧ': 'υ',
        'Φφ': 'φ',
        'Χχ': 'χ',
        'Ψψ': 'ψ',
        'ΩΏώῲῳῴῶῷωώὠὡὢὣὤὥὦὧὨὩὪὫὬὭὮὯὼώᾠᾡᾤᾥᾦᾧ\u1F7D': 'ω',
        'Ϙϙ': 'ϙ',
        'Ϛϛ': 'ϛ',
        'ṇ\'`´΄̣‵′᾿᾽᾽': '',
        ';····\u00B7\u0387': '·',
        'Ϡϡ': 'ϡ',
        '†‡': '†'
    }
    replacement_char_map = {}
    for chars, repl in replacement_map.items():
        for char in chars:
            replacement_char_map[char] = repl

    return ''.join(replacement_char_map.get(char,char) for char in text)
   

def mask_emendations(text: str) -> str:
    # [αβγ] -> [...]
    number_of_subs_made = 999 # bogus value to start loop
    while number_of_subs_made != 0:
        # match [ following any number of dots, a single character and then any number of Greek characters, finally followed by ]
        # repeatedly call it:
        # [αβγ] -> [.βγ] -> [..γ] -> [...]
        text, number_of_subs_made = re.subn(r"(\[\.*)([\sα-ωΑ-Ω])([\sα-ωΑ-Ω]*\])", r"\1.\3", text)
    
    return text

def convert_dot_gaps_to_lines(text: str, to_fill_gap_index: int) -> str:
    # [...] -> [7 missing letters]
    # [...] -> ----
    # TODO converting dots to dashes can be done in a single call (see convert_unbracketed_gaps_to_lines)
    gap_index = 0
    while (match := re.search(r"\[(\.*)\]", text)) is not None:
        matched_gap = match.group(1)
        gap_length = len(matched_gap) 
        gap_start, gap_end = match.span(0)
        repl = ""
        if gap_index == to_fill_gap_index:
            repl = f"[{gap_length} missing letters]"
        else:
            repl = "-" * gap_length
        text = text[:gap_start] + repl + text[gap_end:]
        gap_index += 1

    return text
    

def convert_unbracketed_gaps_to_lines(text: str) -> str:
    # . -> .
    # ... -> ---

 
    # MAAT contains both single dots as a period and multiple dots to indicate a gap with unknown infilling
    # For now, we don't allow these gaps to be selected by to_fill_gap_index.
    # MAAT contains . as a single-character unknown gap and . as a period. This is unfortunate. I treat both as a punctuation mark for now

    # TODO: Cullhed's LLaMa isn't used to 20+-character gaps
    text = re.sub(r"\.{2,}", lambda match: '-' * len(match.group(0)), text) 

    # <gap/> -> ----------
    # 10 dashes for gap of unknown length
    text = re.sub(r"<gap/>", '----------', text)

    # TODO consolidate consecutive gaps

    return text

def simplify_punctuation(text: str) -> str:
    text = text.replace(" .", ".")
    return re.sub(r"[∶⋮‧•\··\,\.\:]", '·', text)
