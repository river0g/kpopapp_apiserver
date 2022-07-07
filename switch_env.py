# python3 switch_env.py {環境名}
# 環境名={local, prod}

import sys


class EnvSelectError(Exception):
    pass


def write_env_file(env):
    with open(f'./.env.{env}') as rf:
        env_text = rf.read()
        with open('./.env', 'w') as wf:
            wf.write(env_text)


# 第一引数の環境名以外は無視
env = sys.argv[1]
if env == 'dev':
    write_env_file(env)

elif env == 'prod':
    write_env_file(env)

else:
    raise EnvSelectError("入力された環境名に対応していません。")
