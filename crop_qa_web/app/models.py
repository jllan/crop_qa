from django.db import models

# Create your models here.
from mongoengine import *
from crop_qa_web.settings import DBNAME

connect(DBNAME)

class Farming(Document):
    url = URLField()
    title = StringField()
    content = ListField()
    crop = StringField()
    source = URLField()
    pub_date = DateTimeField()

    meta = {'collection': 'agri_qa'}  # 指明连接数据库的哪张表

# for i in Farming.objects[:10]:  # 测试是否连接成功
#     print(i._id)
