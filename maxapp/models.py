from django.db import models
from django.contrib.auth.models import User # Import Django's built-in User model

class SearchHistory(models.Model):
    # This creates a "link" or "relationship" to the User table.
    # Each search MUST belong to one user.
    # on_delete=models.CASCADE means: "If a user is deleted, delete all their search history too."
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # This creates a text column in your table with a max length of 500 characters.
    query = models.CharField(max_length=500)
    
    # This creates a date/time column.
    # auto_now_add=True means: "Automatically set this to the current time when a search is first created."
    timestamp = models.DateTimeField(auto_now_add=True) 

    def _str_(self):
        # This is an optional helper. It's what you see in the admin panel.
        # It will show "username: the search query"
        return f"{self.user.username}: {self.query}"