import os

import certifi
from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient

from app.schemas import WordInfo
from app.utils import fetch_and_parse_google_translate, parse_words_extraction

app = FastAPI(
    title="Translator API",
    summary="A microservice providing an API to work with word definitions/translations taken from Google Translate.",
)

client = AsyncIOMotorClient(os.environ["MONGODB_URL"], tlsCAFile=certifi.where())
db = client.words
word_collection = db.get_collection("words")


@app.get(
    "/words/{word}",
    response_description="Get a word translations, definitions, synonyms and examples",
    response_model=WordInfo,
    response_model_by_alias=False,
    )
async def get_word_details(word: str, target: str = "es", src: str = "en") -> WordInfo:
    """
    Get the record for a specific word, looked up by 'word'.
    """
    word = word.lower()
    word_info = await word_collection.find_one({"word": word})
    if word_info:
        return WordInfo(**word_info)

    translated_data = fetch_and_parse_google_translate(word, target_language=target, source_language=src)
    await word_collection.insert_one(translated_data.model_dump(by_alias=True, exclude={"name"}))
    return await word_collection.find_one({"word": word})


@app.get(
    "/words/",
    response_description="List all words in DB",
    response_model=list[dict],
    response_model_by_alias=False,
    )
async def get_word_list(
        page: int = Query(1, ge=1, description="Page number, starting from 1"),
        limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
        query: str = Query(None, min_length=1, description="Filter words by partial match"),
        include_definitions: bool = Query(False, description="Include definitions in the response"),
        include_synonyms: bool = Query(False, description="Include synonyms in the response"),
        include_examples: bool = Query(False, description="Include examples in the response"),
) -> list[dict]:
    """
    List all words records in the database.
    """
    skip = (page - 1) * limit

    projection = {"word": 1}
    if include_definitions:
        projection["definitions"] = 1
    if include_synonyms:
        projection["synonyms"] = 1
    if include_examples:
        projection["examples"] = 1

    filter_condition = {}
    if query:
        filter_condition["word"] = {"$regex": query, "$options": "i"}

    words_cursor = word_collection.find(filter_condition, projection).skip(skip).limit(limit)
    words = await words_cursor.to_list(length=limit)
    return parse_words_extraction(words, include_definitions, include_synonyms, include_examples)


@app.delete(
    "/words/{word}",
    response_description="Delete a word from DB",
)
async def delete_word(word: str) -> dict:
    """
    Remove a single word record from the database.
    """
    word = word.lower()
    delete_result = await word_collection.delete_one({"word": word})
    if delete_result.deleted_count:
        return {"status": "word deleted"}
    else:
        raise HTTPException(status_code=404, detail="Word not found")
