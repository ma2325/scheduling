## 一、使用说明
### 1.运行
在scheduling目录打开cmd。
```bash 
cd backendjs
node app.js
```
之后在浏览器打开`localhost:8080`即可。

### 2.改变后端端口
默认为8080端口，如果需要改动，在`app.js`中有如下语句决定启动端口。
```javaScript
const port = 8080;
```

### 3.前后端进行连接

（1）安装`axios`库
```bash
npm install axios
```

（2）在前端的`main.js`中使用`axios`发送HTTP请求
```javaScript
import axios from 'axios'
axios.defaults.baseURL = "http://localhost:8080";
```

## 二、后端提供的接口名称及其功能
### 1.登录注册
#### （1）admin/login:
```json
//request
{
    "account":[account],
    "password":[password]
}
//respond when success
{
    "code":200,
    "msg":"登录成功"
}
//respond when unsuccess
{
    "code":500,
    "msg":"登录失败"
}
```
#### (2)admin/signup:
```json
//request
{
    "account":[account],
    "password":[password]
}
//respond when success
{
    "code":200,
    "msg":"注册成功"
}
//respond when unsuccess(1)
{
    "code":500,
    "msg":"账号已存在"
}
//respond when unsuccess(2)
{
    "code":500,
    "msg":"注册失败"
}
```
(3)/dashboard
1）/weekView
输入：
1.学生：
user
string 
示例值:
24教学7班

userType
string 
示例值:
student

week
string 
示例值:
1

2.教师：
export interface Request {
    /**
     * 教师编号
     */
    user?: string;示例值:304
    /**
     * 用户类型
     */
    userType?: string;示例值:teacher
    /**
     * 查看周
     */
    week?: string;
    [property: string]: any;示例值:1
}


返回：
export interface Datum {
    /**
     * 楼名
     */
    building: string;
    /**
     * 校区名
     */
    campus: string;
    /**
     * 教室名
     */
    classroom: string;
    /**
     * 结束时间
     */
    endTime: string;
    /**
     * 排课记录唯一标识
     */
    id: number;
    /**
     * 课程名
     */
    name: string;
    /**
     * 开始时间
     */
    startTime: string;
    /**
     * 结束时间
     */
    teacher: string;
    /**
     * 上课星期几
     */
    weekday: number;
    /**
     * 上课周集合
     */
    weeks: number[];
    [property: string]: any;
}

2）/termView
输入：
1.学生：
user
string 
示例值:
24教学7班

userType
string 
示例值:
student

2.教师：
export interface Request {
    /**
     * 教师编号
     */
    user?: string;示例值:304
    /**
     * 用户类型
     */
    userType?: string;示例值:teacher
}


返回：
同/weekView