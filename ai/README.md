# 运行
- 1.mysql中准备好数据
- 2.在sql.connect.py中，将def connect() 的zq换成自己mysql的用户名，并更换密码，数据库名
- 3.main.py中，get_session() 中的
  '''
engine = create_engine("mysql+pymysql://zq:123456@localhost/myAI?charset=utf8mb4")
  '''
  也做如步骤1的替换
- 4.运行main，生成的课表数据会存入数据库中

  # 注意
  - 与前端的软约束交互暂时还不能传参，马上会改
