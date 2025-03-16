import sql.connect

#连接数据库
conn=sql.connect.connect()
cursor=conn.cursor()

#关闭
cursor.close()
print("exit to mysql")
conn.close()