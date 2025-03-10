# :bookmark_tabs:数据库说明
数据库在本地创建后使用 ***mysqldump*** 导出数据形成***sql***文件，输入本地MySQL服务器的凭据即可使用。

## :file_folder: 文件说明
- schedule.sql为MySQL根据数据库结构自动导出的文件
- src.sql为输入的源代码

---
##  :tent: 导出方式
使用 mysqldump 命令将数据库导出为 SQL 文件。
```bash
mysqldump -u [username] -p [database_name] > [database_name.sql]
```

*方括号内为变量，根据实际情况填写。[username] 是本地 MySQL 的用户名，[database_name] 是要导出的数据库名称，[database_name.sql] 是导出的 SQL 文件名。下同*
## :sparkler: 使用方式
使用 mysql 命令将 SQL 文件导入到本地 MySQL 服务器，即可在本地使用该数据库。
```bash
mysql -u [username] -p [database_name] < [database_name.sql]
```
