from fastapi import APIRouter
from fastapi import Response, Request, Depends
from fastapi.encoders import jsonable_encoder
from app.schemas import UserBody, SuperUserBody, JwtToken, Status
from app.auth_utils import AuthJwt
from app.database import db_create_jwt_token, db_create_superuser
import requests

router = APIRouter()
auth = AuthJwt()


# @router.post('/api/jwttoken', response_model=JwtToken)
@router.post('/api/jwttoken')
async def get_jwt_token(request: Request, user: UserBody):
    user = jsonable_encoder(user)
    token = await db_create_jwt_token(user)
    return token


@router.post('/api/createsuperuser', response_model=Status)
async def create_superuser(request: Request, user: SuperUserBody):
    user = jsonable_encoder(user)

    try:
        await db_create_superuser(user)
        return {'status': 'true', 'message': 'success'}

    except Exception as e:
        return {'status': 'false', 'message': str(e)}
