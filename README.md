# このプロジェクトの目的

- fastapi と mongodb を繋ぐ
- scraping プロジェクトから結果を受け取って fastapi に post
- GETmethod を使ったフロントに対して mongodb のデータを返す。

# 図

- source_site -> scraping プロジェクト -> このプロジェクト(fastapi) -> mongodb
- mongodb -> このプロジェクト(fastapi) -> フロント(Next.js)

# endpoint

jwt token を発行する。header にはユーザー名とパスワードを入力。毎回 jwttoken を発行するようにする。 \
ユーザー名とパスワードは mongodb の superuser という collection という環境変数に保存する。 \
post api/jwttoken

データを GET,POST するもの(is many data. not one) \
2 つとも header には jwt-token を入力。 \
get api/todo \
post api/todo

## サーバー起動には...

uvicorn main:app --reload \
すれば良い。
