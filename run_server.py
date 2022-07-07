import subprocess as sp

try:
    sp.run(['uvicorn', 'app.main:app', '--reload'])
except KeyboardInterrupt:
    print('processの終了が完了しました。')
