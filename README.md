This is an example of openai embedding based answering API. It can consume knowledge from youtube, website links, pdf and epub books and answer any questions.  


## Currently supported sources include pdf, epub, youtube link (Using assembly AI), html link

## Instructions to run it.  (Basic DJANGO framework commands)
 
Install dependencies using

<code>pip install -r requirements.txt</code>


## Do migrations 
<code>python manage.py makemigrations</code> 

<code>python manage.py migrate</code>

## Create a superuser 

<code>python manage.py createsuperuser</code>

### Set your username, password

## Copy following in .env files
<code>

    OPEN_AI_KEY=""
    COHERE_API_KEY=""    
    ASSEMBLY_API_KEY=""
    MAX_EMBEDDING_LENGTH="800"
    EMBEDDING_MODEL="openai" or "cohere"

</code>

## Runserver

<code>python manage.py runserver</code>

## How to use 

Open "http://127.0.0.1:8000/admin/sources/source/"

Add a new source. As an example: copy http://paulgraham.com/startupideas.html in link and click submit. 

Now use following endpoint to search 

https://127.0.0.1:8000/search/answer?search_query=Hello

Currently frontend does not exist for the same. 
