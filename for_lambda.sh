echo '環境を本番環境に切り替えています。'
python3 switch_env.py prod
echo '環境の切り替えが終わりました。'

cd apienv/lib/python3.8/site-packages
sudo zip -r9 ../../../../function.zip .
cd ../../../../
sudo zip -g function.zip -r app
sudo zip -g function.zip -r routes
# aws --region us-east-1 lambda update-function-code --function-name testapi --zip-file fileb://function.zip
aws --region us-east-1 lambda update-function-code --function-name fastApiLambda --zip-file fileb://function.zip

# git 関連
# git add .
# git commit -m ''
# git push origin main