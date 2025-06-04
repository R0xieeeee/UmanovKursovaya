import os

class Config:
    SECRET_KEY = os.urandom(24)
    DATABASE = 'instance/database.db'
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    STATUS_LIST = [
        "Курьер забрал заказ и направляется к вам",
        "Заказ доставлен"
    ]
