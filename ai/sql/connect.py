import pymysql

#连接数据库函数
def connect():
    try:
        conn = pymysql.connect(#我的本地数据库
            host='localhost',
            user='zq',
            passwd='123456',
            database='myAI',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor  # 返回字典格式结果
        )
        print("Connected to MySQL!")
        return conn
    except Exception as e:
        print(e)
        print("Failed to connect to MySQL!")
        return None


