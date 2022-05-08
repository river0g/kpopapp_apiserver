from fastapi import APIRouter
from fastapi import Request, Response, HTTPException
from fastapi.encoders import jsonable_encoder
# from schemas import UserBody
from app.auth_utils import AuthJwt

from typing import List, Union
from starlette.status import HTTP_201_CREATED
from app.schemas import Articles, Status
from app.database import db_get_articles, db_create_articles, db_get_one_week_articles, db_get_groups_articles, db_get_group_articles

from decouple import config

root_user = config('ROOT_USER')

router = APIRouter()
auth = AuthJwt()


# @router.get('/api/article', response_model=Union[List[Articles], dict])
@router.get('/api/article')
async def get_articles(request: Request):
    # auth.verify_jwt(request) # GETでは実装しない方向
    res = await db_get_articles()
    return res


@router.get('/api/article/{group_name}')
async def get_articles_group(group_name: str, request: Request):
    res = await db_get_group_articles(group_name)
    return res


@router.get('/api/articles')
async def get_new_articles(request: Request):
    # auth.verify_jwt(request, root_user)  # GETでは実装しない方向
    res = await db_get_groups_articles()
    return res


@router.get('/api/oneweek', response_model=Union[List[Articles], dict])
async def get_one_week_article():
    res = await db_get_one_week_articles()
    return res


@router.post('/api/article', response_model=Status)
async def create_articles(request: Request, response: Response, data: List[Articles]):
    try:
        if not auth.verify_jwt(request, root_user):
            raise 'verify error'

        article = jsonable_encoder(data)
        res = await db_create_articles(article)
        response.status_code = HTTP_201_CREATED
        return {'status': 'true', 'message': 'post success'}
    except Exception as e:
        return {'status': 'false', 'message': str(e)}
