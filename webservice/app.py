import boto3
import os
from dotenv import load_dotenv
from typing import Union
import logging
from fastapi import FastAPI, Request, status, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import uuid

from getSignedUrl import getSignedUrl

load_dotenv()

app = FastAPI()
logger = logging.getLogger("uvicorn")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logger.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class Post(BaseModel):
    title: str
    body: str


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv("DYNAMO_TABLE"))


@app.post("/posts")
async def post_a_post(post: Post, authorization: str | None = Header(default=None)):

    logger.info(f"title : {post.title}")
    logger.info(f"body : {post.body}")
    logger.info(f"user : {authorization}")

    # Doit retourner le résultat de la requête la table dynamodb

    post_id = uuid.uuid4()

    post_json = {"id": f"ID#{post_id}",
                 "title": f"{post.title}",
                 "user": f"USER#{authorization}",
                 "body": f"{post.body}",
                 "image": "https://blog.fr.playstation.com/tachyon/sites/10/2023/09/adc58ff171d20c05b16033b101b3ada9f6d16c85.jpeg"}

    data = table.put_item(Item=post_json)

    return data

@app.get("/posts")
async def get_all_posts(user: Union[str, None] = None):

    if not user:
        resp = table.scan(
            Select='ALL_ATTRIBUTES',
            ReturnConsumedCapacity='TOTAL',
        )

        all_posts = resp["Items"]
    else:
        resp = table.query(
            Select='ALL_ATTRIBUTES',
            KeyConditionExpression="#user = :user",
            ExpressionAttributeValues={
                ":user": f"USER#{user}",
            },
            ExpressionAttributeNames={ "#user": "user" },
        )

        all_posts = resp["Items"]
    
    # image_url = get_signed_url_put(filename=,filetype=, postId=,authorization=)

    # post_returned = {
    #     "id": f"{post_id}",
    #     "title": f"{post.title}",
    #     "image": "url_image",
    #     "body":"string",
    #     "labels":["string", "string"]
    # }

    # Doit retourner une liste de post
    return all_posts

    
@app.delete("/posts/{post_id}")
async def get_post_user_id(post_id: str):
    # Doit retourner le résultat de la requête la table dynamodb
    return []

@app.get("/signedUrlPut")
async def get_signed_url_put(filename: str,filetype: str, postId: str,authorization: str | None = Header(default=None)):
    return getSignedUrl(filename, filetype, postId, authorization)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")

