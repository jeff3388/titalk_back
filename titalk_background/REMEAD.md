# 啟動指令

gunicorn -b 0.0.0.0:8080 -w 4 backgroud_service:app --threads=30 --worker-class=gthread --worker-connections=2000 --timeout 30 --daemo