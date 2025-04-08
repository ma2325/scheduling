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
#### （1）/admin/login:
作用：登录，请求形式：post，附加参数：body
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
#### (2)/admin/signup:
作用：注册，请求形式：post，附加参数：body
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
### 2.统计数据
#### (1)/statistics:
作用：获取统计信息，请求形式：get，附加参数：无
```json
//request
query:week=[week]//查询的周
//respond when success
{
    "code":200,
    "data":[
        [
            {
                "building": "车间",
                "occupied": 0,//占用教室数
                "total": 9,//总教室数
                "rate": 0//占用率
            },
            {
                "building":[building],
                "occupied":[occupied],
                "total":[total],
                "rate":[rate]
            }
            //其他建筑及其对应占用率
        ],
        [
            {
                "type": "理论",
                "count": 0//此种类型的课程数量
            },
            {
                "type":[type],
                "count":[count]
            }
            //其他类型课程及其数量
        ]
    ]
}
//respond when unsuccess
{
    "code":400,
    "msg":"缺少week参数"
}
//respond when unsuccess2
{
    "code":500,
    "msg":"服务器异常"
}
```
### 3.手动排课
#### (1)/manual/room:
作用：按需获取教室，请求形式：get，附加参数：query
参数格式：*building=[building],campus=[campus]*
**备注：1.二者均为可选参数； 2.*building*和*campus*均为LIKE查询 3.*campus*为校区，后同**
```json
//respond when success
{
    "code":200,
    "rows":
    [
        {
            "rid": "CJ1-bjcj",//教室id号
            "rname": "CJ1-钣金车间"//教室名称
        },
        {
            "rid":[rid],
            "rname":[rname]
        }
        //其他教室
    ]
}
//respond when unsuccess
{
    "code":500,
    "msg":[msg]
}
```
#### (2)/manual/task:
作用：按需获取课程，请求形式：post，附加参数：query
参数格式：*week=[week], building=[building], campus=[campus]*
**备注：1.三者均为可选参数; 2.*building*参数和*campus*参数均为*LIKE*查询**
```json
//respond when success
{
    "code":200,
    "rows":
    [
        {
            "scid": 1,//任务id号
            "sctask": "570102KBOB032024202511017"//任务对应的task的教学班编号
        },
        {
            "scid":[scid],
            "sctask":[sctask]
        }
        //其他课程信息
    ]
}
```
#### (3)/manual/change:
作用：按需更改课程安排，请求形式：post，附加参数：body
**备注：此处为更改schedule表的接口，将根据传输的数据进行更改，没有传的数据将不会更改**
```json
//request参数格式(scid为必选参数，其他所有参数均为可选参数)
{ 
    "scid":[scid], //auto increment integer primary key唯一标识
    "sctask":[sctask], //教学班id
    "scroom":[scroom], //教室号
    "scbegin_week":[scbegin_week], 
    "scend_week":[scend_week], 
    "scday_of_week":[scday], //星期几
    "scslot":[scslot], //第几节课,只有一节课的为形如“m-m”的字符串，连续的课程会出现形如“m-n”的字符串
    "scteacherid":[scteacherid],
    "scteacherdepartment":[scteacherdepartment],//教师所在部门名称
}
//respond when success
{
    "code":200,
    "msg":"修改成功"
}
//respond when unsuccess
{
    "code":500,
    "msg":"修改失败"
}
```
#### (4)/manual/all:
作用：获取所有课程，请求形式：get，附加参数：无
```json
//respond when success
{
    "code":200,
    "rows":
    [
        {
            "scid": 1,
            "sctask": "570102KBOB032024202511017",//教学班id
            "scday_of_week": 2,//星期几
            "scroom": "JXL517",//教室号
            "scbegin_week": 1,
            "scend_week": 16,
            "scslot": "1-1",//第几节课,只有一节课的为形如“m-m”的字符串，连续的课程会出现形如“m-n”的字符串
            "scteacherid": "130",
            "scteacherdepartment": "教育艺术学院",
            "composition": "23学前教育5班"
        },
        {
            "scid":[scid],
            "sctask":[sctask],
            "scday_of_week":[scday_of_week],
            "scroom":[scroom],
            "scbegin_week":[scbegin_week],
            "scend_week":[scend_week],
            "scslot":[scslot], 
            "scteacherid":[scteacherid],
            "scteacherdepartment":[scteacherdepartment],
            "composition":[composition]
        }
        //其他课程信息
    ]
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
