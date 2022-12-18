from django.contrib import admin

from .models import Source, Embedding
# Register source and embedding models

admin.site.register(Source)

admin.site.register(Embedding)
