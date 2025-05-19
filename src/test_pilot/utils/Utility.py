from src.test_pilot.state.sdlc_state import SDLCState

class Utility:
    
    def __init__(self):
        pass
    
    def format_list(self, items):
        """Format list items nicely for prompt"""
        return '\n'.join([f"- {item}" for item in items])
    
    def format_user_stories(self, stories):
        """Format user stories nicely for prompt"""
        formatted_stories = []
        for story in stories:
            if hasattr(story, 'id') and hasattr(story, 'title') and hasattr(story, 'description'):
                # Handle class instance
                formatted_stories.append(f"- ID: {story.id}\n  Title: {story.title}\n  Description: {story.description}")
            elif isinstance(story, dict):
                # Handle dictionary
                formatted_stories.append(f"- ID: {story.get('id', 'N/A')}\n  Title: {story.get('title', 'N/A')}\n  Description: {story.get('description', 'N/A')}")
        return '\n'.join(formatted_stories)
    
    