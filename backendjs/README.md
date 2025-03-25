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
(3)dashboard
/**
 * Request
 */
export interface Request {
    code: number;
    data: Datum[];
    [property: string]: any;
}

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
     * 课程结果唯一标明
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
     * 教师名
     */
    teacher: string;
    /**
     * 周几上课
     */
    weekday: number;
    /**
     * 上课周
     */
    weeks: number[];
    [property: string]: any;
}