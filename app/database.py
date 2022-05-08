from decouple import config
import motor.motor_asyncio
from typing import Union
from app.auth_utils import AuthJwt
from fastapi import HTTPException
from typing import List
from datetime import datetime, timedelta

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


# 指定されたグループの記事の最新100件を取得する。
async def db_get_group_articles(group_name) -> List[dict]:
    articles = []
    db_articles = await collection_articles.find({"group": group_name}).sort("datetime", -1).to_list(100)
    for article in db_articles:
        articles.append(article_serializer(article))

    return articles


# 各グループ30件の新着記事を取得(取得数=len(group_list)*30)
async def db_get_groups_articles() -> List[dict]:
    group_list = ['blackpink', 'aespa', 'ive', 'gi-dle', 'nmixx', 'kep1er']
    articles = []

    def remove_duplicated_article(articles):
        filtered_articles = []
        for article in articles:
            if not article in filtered_articles:
                filtered_articles.append(article)

        return filtered_articles

    for group in group_list:
        article_list = await collection_articles.find({"group": group}).sort("datetime", -1).to_list(30)
        for article in article_list:
            articles.append(article_serializer(article))

    # return articles
    return remove_duplicated_article(articles)


# 現在~1週間前(計8日間)記事を取得する。
async def db_get_one_week_articles() -> List[dict]:
    one_week = []
    for day in range(8):
        tokyo_day = datetime.utcnow() - timedelta(days=7-day) + timedelta(hours=9)
        one_week.append({"date": tokyo_day.strftime("%Y.%m.%d")})

    articles = []
    db_articles = await collection_articles.find({"$or": one_week}).sort("datetime", -1).to_list(None)
    for article in db_articles:
        articles.append(article_serializer(article))

    return articles


# 200件の記事を取得する。databaseの新しい(not 新着記事)順に取ってくるのでtest用。
async def db_get_articles() -> List[dict]:
    articles = []
    for article in await collection_articles.find().to_list(200):
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
    token: str = auth.encode_jwt(user['superuser'])
    return {
        "token": token
    }
