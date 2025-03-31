import random
import string

class StringMaker:
    """Generate random strings for the game."""
    
    def __init__(self, length=5):
        """Initialize with the desired string length."""
        self.length = length
        self.chars = string.ascii_letters + string.digits + string.punctuation
    
    def make_string(self, avoid_string=None):
        """
        Generate a random string.
        If avoid_string is provided, ensure the new string is different.
        """
        new_string = ''.join(random.choice(self.chars) for _ in range(self.length))
        
        # Make sure the new string is different from avoid_string
        if avoid_string and new_string == avoid_string:
            return self.make_string(avoid_string)
        
        return new_string
