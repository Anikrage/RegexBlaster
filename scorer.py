class Scorer:
    """Handle scoring and defense validation."""
    
    def __init__(self):
        """Initialize scorer."""
        self.last_score = 0
    
    def calculate_score(self, defense):
        """Calculate score based on the complexity of the regex."""
        # Base score
        points = 0
        
        # One point for each basic operator
        basic_ops = ['.', '|', '?', '^', '$']
        for op in basic_ops:
            points += defense.count(op)
        
        # Two points for character sets, groups, and Kleene star/plus
        points += 2 * defense.count('[')  # Character sets
        points += 2 * defense.count('(')  # Groups
        points += 2 * (defense.count('*') + defense.count('+'))  # Kleene star/plus
        
        # Five points for backreferences and repetition
        backrefs = sum(1 for i in range(1, 10) if f'\\{i}' in defense)
        points += 5 * backrefs
        points += 5 * defense.count('{')  # Repetition
        
        # Ten points for lookaheads and lookbehinds
        lookaround = (defense.count('(?=') + defense.count('(?!') + 
                      defense.count('(?<=') + defense.count('(?<!'))
        points += 10 * lookaround
        
        # Minimum score of 1 for a successful match
        if points == 0:
            points = 1
            
        # Update last score
        self.last_score = points
        return points
