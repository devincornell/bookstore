class ResearchTaskDoesNotExist(Exception):
    """Custom exception for when a research task is not found in the database."""
    pass

class ResearchTaskAlreadyExists(Exception):
    """Custom exception for when a research task with the same title already exists in the database."""
    pass