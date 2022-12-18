from builtins import open
from sources.models import Source

with open('datalist.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        source = Source(link=line.strip(), type="html")
        source.save()
