from django.shortcuts import HttpResponse
from .models import Source
# Create your views here.

# create a view to list all sources 

def list_sources(request):
    # Get this list of sources 
    authors = Source.objects.values("author").distinct()
    # Return the list of sources to the template
    return HttpResponse(list(authors))