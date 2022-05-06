from fastapi import FastAPI, Request
from mangum import Mangum
from routes import route_article, route_auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(route_article.router)
app.include_router(route_auth.router)

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get('/')
def root():
    return {"message": "Welcome to Fast API!"}


@app.post('/')
def root_post(request: Request, data: dict):  # test用
    print(request.headers)
    return {
        "message": "POSTED DATA",
        "data": data
    }


handler = Mangum(app)
