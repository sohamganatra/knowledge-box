from struct import unpack_from, pack
from django.conf import settings
from transformers import GPT2TokenizerFast
import numpy as np
import openai
from bs4 import BeautifulSoup
import requests
import os
import re


def html_to_text(htmlContent):
    soup = BeautifulSoup(htmlContent, "html.parser")
    # get all text from p tags
    p_text = [para.get_text() for para in soup.find_all("p")]
    l_text = [li.get_text() for li in soup.find_all("li")]
    p_text_combined = ". ".join(p_text)
    l_text_combined = ". ".join(l_text)

    text = p_text_combined + l_text_combined

    # return " ".join(text)
    text = text.replace("(link)", "")
    return text


def div_txt_in_chunk(text, chunk_size):
    chunked_texts = []
    # // Remove
    if len(text) > chunk_size:
        # break text into chunks of size chunk_size
        # create embeddings for each chunk
        sentences = text.split(". ")
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 30:
                print("Sentence too short")  # throw away useless small strings
                continue
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "  # add sentence to current chunk
            else:
                # create embedding for current chunk
                chunked_texts.append(current_chunk)
                current_chunk = sentence + "."
        if len(current_chunk) > 0:
            # create embedding for current chunk
            chunked_texts.append(current_chunk)
    else:
        chunked_texts.append(text)
    return chunked_texts


completion_model = settings.COMPLETIONS_MODEL
openai.api_key = settings.OPEN_AI_KEY
prompt = settings.PROMPT
max_completion_length = settings.MAX_COMPLETION_LENGTH


def get_answer(query, context):
    if context == "":
        return "I don't know."
    new_prompt = prompt.replace(
        "$CONTEXT", context).replace("$query", query)

    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    prompt_len = len(tokenizer.tokenize(new_prompt))
    print(new_prompt)
    response = openai.Completion.create(
        prompt=new_prompt.replace(
            "$CONTEXT", context).replace("$query", query),
        temperature=0.2,
        max_tokens=max_completion_length-prompt_len,
        top_p=1,
        frequency_penalty=0.1,
        presence_penalty=0.1,
        model=completion_model
    )["choices"][0]["text"].strip(" \n")
    print("Got response:", response)
    print("Response length:", len(response))
    return response


def binary_to_list(binary):
    binary_data_string = unpack_from('f' * (len(binary) // 4), binary)
    return binary_data_string


def vector_similarity(x: list[float], y: list[float]) -> float:
    """
    We could use cosine similarity or dot product to calculate the similarity between vectors.
    In practice, we have found it makes little difference.
    """
    return np.dot(np.array(x), np.array(y))


def doc_embed(text, embedding_type):
    text = delete_links(text)
    # using openai
    if embedding_type == "openai":
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        floatlist = response["data"][0]["embedding"]
        return pack('%sf' % len(floatlist), *floatlist)
    else:
        texts = []
        texts.append(text)
        response = settings.COHERE_CLIENT.embed(texts)
        floatlist = response.embeddings[0]
        return pack('%sf' % len(floatlist), *floatlist)


def query_embed(text, embedding_type):
    if embedding_type == "openai":
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        floatlist = response["data"][0]["embedding"]
        return floatlist
    else:
        texts = []
        texts.append(text)
        response = settings.COHERE_CLIENT.embed(texts)
        floatlist = response.embeddings[0]
        return floatlist


def read_file(filename, chunk_size=5242880):
    with open(filename, 'rb') as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data


def start_assembly_session(filename):
    headers = {'authorization': settings.ASSEMBLY_API_KEY}
    response = requests.post('https://api.assemblyai.com/v2/upload',
                             headers=headers,
                             data=read_file(filename))
    json = response.json()
    print(json)
    upload_url = json['upload_url']
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {"audio_url": upload_url}
    response = requests.post(endpoint, json=json, headers=headers)
    os.remove(filename)
    return response.json()


def get_transcription_results(job_id):
    headers = {'authorization': settings.ASSEMBLY_API_KEY}
    response = requests.get(
        f'https://api.assemblyai.com/v2/transcript/{job_id}', headers=headers)
    json = response.json()
    if json['status'] == 'error':
        return None
    if json['status'] != 'completed':
        return None
    json_txt = json['text']
    return json_txt
