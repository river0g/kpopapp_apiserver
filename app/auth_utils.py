import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

from datetime import datetime, timedelta
from decouple import config

JWT_KEY = config("JWT_KEY")


class AuthJwt():
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret_key = JWT_KEY

    # パスワードのハッシュ化
    # lambda上で動かないので使わない。
    def generate_hashed_pw(self, password) -> str:
        return self.pwd_ctx.hash(password)

    # lambda上で動かないので使わない。
    def verify_pw(self, plain_pw, hashed_pw) -> bool:

        try:
            self.pwd_ctx.verify(plain_pw, hashed_pw)
            return True
        except:
            return False

    def encode_jwt(self, username):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=20),
            'iat': datetime.utcnow(),
            'sub': username
        }

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'
        )

    def decode_jwt(self, token) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload['sub']

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail='JWT is not valid'
            )

    def verify_jwt(self, request, username) -> str:
        token: str = request.headers.get("authorization")
        if not token:
            raise HTTPException(
                status_code=401, detail='No JWT exist: may not set yet or deleted'
            )

        _, _, value = token.partition(" ")

        # ここでトークンのが存在するか、有効かの確認をする。
        subject = self.decode_jwt(value)
        if subject == username:
            return True
        else:
            return False
