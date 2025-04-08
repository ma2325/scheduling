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
    "scbegin_time":[scbegin_time],//上课时间(time) 
    "scend_time":[scend_time], //下课时间(time)
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
            "scday_of_week": "2",//星期几
            "scroom": "JXL517",//教室号
            "scbegin_week": 1,
            "scend_week": 16,
            "scbegin_time": "08:00:00",
            "scend_time": "09:40:00",
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
            "scbegin_time":[scbegin_time],
            "scend_time":[scend_time],
            "scteacherid":[scteacherid],
            "scteacherdepartment":[scteacherdepartment],
            "composition":[composition]
        }
        //其他课程信息
    ]
}
## 三、Dashboard 功能接口

### 1. 周视图查询接口 `/weekView`
**作用**  
查询指定用户（学生/教师）在特定周次的课表信息

**请求方式**  
`GET`

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| user | string | 是 | 用户标识（班级名/教师编号） | `"24教学7班"`（学生）<br>`"304"`（教师） |
| userType | string | 是 | 用户类型 | `"student"`（学生）<br>`"teacher"`（教师） |
| week | string | 是 | 查询周次 | `"1"` |

#### 响应示例
```json
{
  "building": "教学楼",
  "campus": "主校区",
  "classroom": "517",
  "id": 101,
  "name": "数据结构",
  "teacher": "张老师",
  "weekday": 2,
  "weeks": [1,3,5,7,9,11,13,15],
  "slot": "1-2"//上课课次
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
