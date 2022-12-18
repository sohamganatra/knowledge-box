import re
from struct import *
from django.shortcuts import render
# Create your views here.
from sources.models import Embedding
from searchresolver.models import Search
from django.http import HttpResponse
# expose an API endpoint for the search resolver
from common.util.utils import vector_similarity, get_answer, binary_to_list
from django.conf import settings
from common.util.utils import doc_embed, query_embed
max_context_length = settings.MAX_CONTEXT_LENGTH

# get the list of sources matching the search query


def get_answer(request):
    # get the search query from the request
    search_query = request.GET.get('search_query')
    author = request.GET.get('author')
    tags = request.GET.get('tags')

    # return an error if no search query is found
    if search_query is None:
        return HttpResponse("No search query found")

    # check if the search query is already in the database
    if Search.objects.filter(query=search_query).filter(type="answer").exists():
        return HttpResponse(Search.objects.filter(query=search_query).filter(type="answer").first().response)

    if author is None:
        author = ""
    if tags is None:
        tags = ""

    embedding_model = settings.EMBEDDING_MODEL

    # get the list of sources matching the search query
    embeddings = Embedding.objects.filter(
        source__author__icontains=author, source__tags__icontains=tags)

    # return an error if no sources are found
    if embeddings is None or len(embeddings) == 0:
        return HttpResponse("No results found")
        # calculate text embeddings for the query

    # calculate text embeddings for the query
    query_embedding = query_embed(search_query, embedding_model)

    # filter the embeddings based on the embedding model
    model_embeddings = embeddings.filter(
        embedding_type=embedding_model)

    # calculate the similarity between the query and the embeddings
    # sort the embeddings based on the similarity
    doc_contents = sorted([
        (vector_similarity(query_embedding, binary_to_list(doc_embedding.embedding)), doc_embedding.content, doc_embedding.id) for doc_embedding in model_embeddings
    ], reverse=True)

    # now create the context using top results
    total_context = ""
    content_seen = []

    # get the context from the top results
    for index, doc_content, doc_id in doc_contents:
        # skip if the content is already seen
        if doc_content in content_seen:
            continue

        # add the content to the context
        total_context = total_context + "\n" + "Context" + ": " + doc_content + "\n"

        # add the content to the already seen list
        content_seen.append(doc_content)

        if len(total_context) > max_context_length:
            break

    # get the answer from the openai GPT3 model
    answer = get_answer(search_query, total_context)

    # save the answer in the database
    Search.objects.create(query=search_query, response=answer, type="answer")
    # return the answer
    return HttpResponse(answer)
