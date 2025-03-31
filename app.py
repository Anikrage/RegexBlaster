import streamlit as st
import re
import time
from game_state import GameState
from string_maker import StringMaker
from scorer import Scorer

st.set_page_config(
    page_title="Regex Blaster",
    page_icon="🎯",
    layout="wide"
)

# Initialize game state
def get_game_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = GameState()
    return st.session_state.game_state

def reset_game():
    st.session_state.game_state = GameState()
    st.session_state.string_maker = StringMaker(st.session_state.string_length)

# Define callback function to process defense
def process_defense():
    if 'defense_input' in st.session_state and st.session_state.defense_input:
        game_state = st.session_state.game_state
        defense = st.session_state.defense_input
        
        # Prevent using the exact attack string as defense
        if defense == game_state.attack_string:
            game_state.message = "You can't just copy the attack string! Use a proper regex pattern."
            return
        
        try:
            # Validate regex
            regex = re.compile(defense)
            
            # Check if defense matches attack
            if regex.search(game_state.attack_string):
                # Check if it also matches noncombatant
                if regex.search(game_state.noncomb_string):
                    # Calculate penalty for hitting noncombatant
                    penalty = 10
                    game_state.score -= penalty
                    game_state.message = f"You hit a noncombatant! -{penalty} points"
                    game_state.noncomb_history.append({"string": game_state.noncomb_string, "defense": defense})
                    game_state.noncomb_string = None
                else:
                    # Success!
                    points = st.session_state.scorer.calculate_score(defense)
                    game_state.score += points
                    game_state.message = f"Success! +{points} points"
                    game_state.attack_history.append({"string": game_state.attack_string, "defense": defense, "success": True})
                    game_state.attack_string = None
            else:
                # Failure penalty
                penalty = 5
                game_state.score -= penalty
                game_state.message = f"Your defense failed to match the attack! -{penalty} points"
                game_state.attack_history.append({"string": game_state.attack_string, "defense": defense, "success": False})
                game_state.attack_string = None
                
        except re.error:
            # Invalid regex penalty
            penalty = 2
            game_state.score -= penalty
            game_state.message = f"Invalid regular expression! -{penalty} points"
        
        # Clear the defense input
        st.session_state.defense_input = ""

# App title and description
st.title("🎯 Regex Blaster")
st.markdown("""
Match the attack strings with regular expressions while avoiding noncombatants!
Test your regex skills in this arcade-style game.
""")

# Sidebar for game controls
with st.sidebar:
    st.header("Game Controls")
    if 'string_length' not in st.session_state:
        st.session_state.string_length = 5
    
    string_length = st.slider("String Length", 2, 10, st.session_state.string_length)
    if string_length != st.session_state.string_length:
        st.session_state.string_length = string_length
        if 'string_maker' in st.session_state:
            st.session_state.string_maker = StringMaker(string_length)
    
    if st.button("New Game"):
        reset_game()
    
    st.markdown("### How to Play")
    st.markdown("""
    1. Type a regex pattern in the defense input
    2. Click the "Attack!" button to submit your defense
    3. Match attack strings but avoid noncombatants
    4. Score points based on regex complexity
    5. Game ends if score becomes negative
    """)
    
    st.markdown("### Scoring")
    st.markdown("""
    - Basic operators (`.`, `|`, `?`, `^`, `$`): 1 point each
    - Character sets `[...]`, groups `(...)`, `*`, `+`: 2 points each
    - Backreferences `\\1`, repetition `{2}`: 5 points each
    - Lookaheads/lookbehinds: 10 points each
    - Hitting noncombatant: -10 points
    - Failed defense: -5 points
    - Invalid regex: -2 points
    """)

# Initialize game components
game_state = get_game_state()
if 'string_maker' not in st.session_state:
    st.session_state.string_maker = StringMaker(st.session_state.string_length)
if 'scorer' not in st.session_state:
    st.session_state.scorer = Scorer()

# Generate strings if needed
if game_state.attack_string is None:
    game_state.attack_string = st.session_state.string_maker.make_string()
if game_state.noncomb_string is None:
    game_state.noncomb_string = st.session_state.string_maker.make_string(game_state.attack_string)

# Check for negative score game over
if game_state.score < 0 and not game_state.game_over:
    game_state.game_over = True
    game_state.message = "GAME OVER! Your score went negative."

# Game layout
col1, col2 = st.columns(2)

# Attack strings column
with col1:
    st.subheader("Attacks")
    attack_container = st.container(height=300, border=True)
    with attack_container:
        # Display previous attacks
        for attack in game_state.attack_history:
            if attack["success"]:
                st.markdown(f"✅ `{attack['string']}` - matched with `{attack['defense']}`")
            else:
                st.markdown(f"❌ `{attack['string']}` - failed with `{attack['defense']}`")
        
        # Display current attack
        if not game_state.game_over:
            st.markdown("### Current Attack:")
            st.markdown(f"<h2 style='color:red;'>{game_state.attack_string}</h2>", unsafe_allow_html=True)
        
        # Check if game over
        if len([a for a in game_state.attack_history if not a["success"]]) >= game_state.attack_limit:
            game_state.game_over = True
            st.error("GAME OVER! Too many attacks got through!")

# Noncombatant strings column
with col2:
    st.subheader("Noncombatants")
    noncomb_container = st.container(height=300, border=True)
    with noncomb_container:
        # Display previous noncombatants
        for noncomb in game_state.noncomb_history:
            st.markdown(f"❌ `{noncomb['string']}` - hit by `{noncomb['defense']}`")
        
        # Display current noncombatant
        if not game_state.game_over:
            st.markdown("### Current Noncombatant:")
            st.markdown(f"<h2 style='color:orange;'>{game_state.noncomb_string}</h2>", unsafe_allow_html=True)
        
        # Check if game over
        if len(game_state.noncomb_history) >= game_state.noncomb_limit:
            game_state.game_over = True
            st.error("GAME OVER! Too many noncombatants hit!")

# Defense input and score display
st.subheader("Defense (Regex)")
defense_col, button_col, score_col = st.columns([3, 1, 1])

with defense_col:
    # Defense input
    if game_state.game_over:
        st.text_input("Enter your regex pattern:", disabled=True, 
                     placeholder="Game Over - Start a new game")
    else:
        defense = st.text_input("Enter your regex pattern:", key="defense_input", 
                               placeholder="Type regex pattern here")

with button_col:
    # Attack button
    st.write("")  # Add some spacing
    st.write("")  # Add some spacing
    if game_state.game_over:
        if st.button("Start New Game", type="primary"):
            reset_game()
    else:
        if st.button("Attack!", type="primary", on_click=process_defense):
            pass  # The on_click callback handles the logic

with score_col:
    # Show score with color based on value
    st.write("")  # Add some spacing
    st.write("")  # Add some spacing
    score_color = "green" if game_state.score >= 0 else "red"
    st.markdown(f"<h2 style='color:{score_color};'>Score: {game_state.score}</h2>", unsafe_allow_html=True)

# Message display
if game_state.message:
    if "GAME OVER" in game_state.message:
        st.error(game_state.message)
    elif "Success" in game_state.message:
        st.success(game_state.message)
    elif "hit a noncombatant" in game_state.message or "failed" in game_state.message or "Invalid" in game_state.message:
        st.warning(game_state.message)
    else:
        st.info(game_state.message)

# Add a regex cheat sheet at the bottom
with st.expander("Regex Cheat Sheet"):
    st.markdown("""
    | Pattern | Description | Example |
    | ------- | ----------- | ------- |
    | `.` | Matches any character except newline | `a.c` matches "abc", "adc", etc. |
    | `^` | Matches start of string | `^abc` matches "abc" at the start of a string |
    | `$` | Matches end of string | `abc$` matches "abc" at the end of a string |
    | `*` | Matches 0 or more repetitions | `ab*c` matches "ac", "abc", "abbc", etc. |
    | `+` | Matches 1 or more repetitions | `ab+c` matches "abc", "abbc", but not "ac" |
    | `?` | Matches 0 or 1 repetition | `ab?c` matches "ac" and "abc" |
    | `{n}` | Matches exactly n repetitions | `ab{2}c` matches "abbc" |
    | `{n,}` | Matches n or more repetitions | `ab{2,}c` matches "abbc", "abbbc", etc. |
    | `{n,m}` | Matches between n and m repetitions | `ab{1,2}c` matches "abc" and "abbc" |
    | `\\` | Escapes special characters | `\\.` matches "." |
    | `[]` | Matches a set of characters | `[abc]` matches "a", "b", or "c" |
    | `[^]` | Matches characters NOT in the set | `[^abc]` matches any character except "a", "b", or "c" |
    | `\|` | Alternation (OR) | `a\|b` matches "a" or "b" |
    | `()` | Creates a group | `(abc)+` matches "abc", "abcabc", etc. |
    | `(?:)` | Non-capturing group | `(?:abc)+` same as above but doesn't capture |
    | `(?=)` | Positive lookahead | `a(?=b)` matches "a" only if followed by "b" |
    | `(?!)` | Negative lookahead | `a(?!b)` matches "a" only if not followed by "b" |
    """)
