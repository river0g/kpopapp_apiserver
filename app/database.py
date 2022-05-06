from decouple import config
import motor.motor_asyncio
from typing import Union
from app.auth_utils import AuthJwt
from fastapi import HTTPException
from typing import List

MONGO_API_KEY = config('MONGO_API_KEY')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
database = client.kpopsite_dev
collection_articles = database.articles
collection_superuser = database.superuser

auth = AuthJwt()


# mongodbが自動的に付与する_idをstrに変換するもの。
def article_serializer(article: dict) -> dict:
    article['id'] = str(article['_id'])
    del article['_id']
    return article


def superuser_serializer(superuser: dict) -> dict:
    return {
        "id": str(superuser["_id"]),
        "username": superuser["superuser"]
    }


async def db_create_articles(data: List[dict]) -> Union[dict, bool]:
    articles = await collection_articles.insert_many(data)


# 最新記事10件を取得する。
async def db_get_new_articles() -> List[dict]:
    articles = []
    db_articles = await collection_articles.find().sort("datetime", -1).to_list(10)
    for article in db_articles:
        articles.append(article_serializer(article))

    return articles


# 記事を取得する。
async def db_get_articles() -> List[dict]:
    articles = []
    for article in await collection_articles.find().to_list(None):
        articles.append(article_serializer(article))

    return articles


async def db_create_superuser(data: dict) -> str:
    username = data.get("username")
    password = data.get("password")
    masteruser = data.get("master")

    # superuserを作成するためのmasteruserが正しく無い場合作成できなくする。
    master = await collection_superuser.find_one({"master": masteruser})
    if not master:
        raise HTTPException(
            status_code=400, detail="master user is not found"
        )

    overlap_user = await collection_superuser.find_one({"superuser": username})
    # データベースにユーザーが存在していたらエラーを出す
    if overlap_user:
        raise HTTPException(
            status_code=400, detail='Username is already token')
    if not password:
        raise HTTPException(status_code=400, detail='Password is None')

    password = auth.generate_hashed_pw(password)
    data = {"superuser": username, "password": password}
    superuser = await collection_superuser.insert_one(data)
    new_superuser = await collection_superuser.find_one({"_id": superuser.inserted_id})
    return superuser_serializer(new_superuser)


async def db_create_jwt_token(data: dict) -> str:
    username = data.get("username")
    password = data.get("password")
    user = await collection_superuser.find_one({"superuser": username})

    # ユーザーがいないか、データベースのパスワードと合致しなかったらエラー
    # Lambda上で動かないので使わない。
    # hashed_pw = user['password']
    # is_verify = auth.verify_pw(str(password), str(hashed_pw))
    # if (not user) or (not auth.verify_pw(password, user["password"])):

    if not user:
        raise HTTPException(
            status_code=400, detail=f"{username}, Invalid username or password")

    # token = auth.encode_jwt(username)
    token = auth.encode_jwt(user['superuser'])
    t = {
        'token': token
    }
    # return token
    return t
