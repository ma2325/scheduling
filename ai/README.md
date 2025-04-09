# 运行
- 1.mysql中准备好数据
- 2.在sql.connect.py中，将def connect() 的zq换成自己mysql的用户名，并更换密码，数据库名
- 3.main.py中，get_session() 中的
  '''
engine = create_engine("mysql+pymysql://zq:123456@localhost/myAI?charset=utf8mb4")
  '''
  也做如步骤1的替换
- 4.运行
- ---
（1）切换到文件路径

（2）安装依赖
- 如果没有sqlalchemy，进行安装
  pip install sqlalchemy -i https://pypi.tuna.tsinghua.edu.cn/simple
- 如果没有numpy，安装pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
- 如果没有pymysql，安装pip install pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple

（3）运行：
python scheduler_cli.py --soft_constraints "约束列表"，如：

python scheduler_cli.py --soft_constraints "(2,5),(4,3)"
# 注意
- 与前端的软约束交互
软约束映射：【编号，优先级】
  1： 同一课程教室相同
  2： 班级排课集中             
  3： 教师排课集中             
  4： 体育课安排在下午    
  5： 体育课后是否上课
  6： 晚上是否上课
- 软约束参数形式应为：
soft_constraints = [(2, 5),(3, 3),(4, 8),(5, 10),(6, 2)]
-  start_time 和 end_time 无意义，写入数据库的值为默认值0
