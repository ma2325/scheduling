import sql.connect
import sql.models


#连接数据库
conn=sql.connect.connect()
cursor=conn.cursor()

#载入课程
'''课程号，教学班名，课程人数，老师（工号表示），时间，周节次，连排节次，指定教室类型，指定教室，指定时间，指定教学楼，开课校区,是否为合班，'''
def load_course():
    cursor.execute("SELECT tacode,taformclass,tapopularity,tateacherid,tahourweek,tacontinuous,tafixedtype,tafixedroom,tafixedtime,tafixedbuilding,tacampus FROM task")
    courses=[]#列表储存
    for row in cursor.fetchall():
        course=sql.models.Course(
            cid=row['tacode'],
            formclass=row['taformclass'],
            popularity=row['tapopularity'],
            teacherid=row['tateacherid'],
            task=row['tahourweek'],
            continuous=row['tacontinuous'],
            fixedroomtype=row['tafixedtype'],
            fixesroom=row['tafixedroom'],
            fixedtime=row['tafixedtime'],
            fixedbuilding=row['tafixedbuilding'],
            capmpus=row['tacampus']
        )
        courses.append(course)
    return courses

#载入教室
'''教室编号，类型，容纳人数，校区，教学楼'''
def load_room():
    cursor.execute("SELECT rid,rtype,rname,rcapacity,rcampus,rbuilding FROM room")
    rooms=[]
    for row in cursor.fetchall():
        room=sql.models.Room(
            rid=row['rid'],
            rtype=row['rtype'],
            rname=row['rname'],
            rcapacity=row['rcapacity'],
            rcampus=row['rcampus'],
            rbuilding=row['rbuilding']
        )
        rooms.append(room)
    return rooms

#载入行政班
'''班名，固定教室'''
def load_myclass():
    cursor.execute("SELECT clname,clfixedroom FROM class")
    myclasses=[]
    for row in cursor.fetchall():
        myoneclass=sql.models.myclass(
            clname=row['clname'],
            clfixedroom=row['clfixedroom']
        )
        myclasses.append(myoneclass)
    return myclasses


try:
    courses=load_course()
    for course in courses:
        if course.teacherid is None:
            print(f"⚠️ 课程 {course.cid} ，未安排老师")

    print("courses OK\n")

    rooms=load_room()
    print("rooms OK\n")

    myclasses=load_myclass()
    print("myclasses OK\n")

    # 测试数据
    courses = [
        sql.models.Course(
            cid=1,
            formclass="A班",
            popularity=30,
            teacherid=1,
            task="1-8:2,10-15:2",
            continuous=1,
            fixedroomtype="普通教室",
            fixesroom=None,
            fixedtime=None,
            fixedbuilding=None,
            capmpus="东校区",
            combine=False
        ),
        sql.models.Course(
            cid=2,
            formclass="B班",
            popularity=25,
            teacherid=2,
            task="2-4:2",
            continuous=2,
            fixedroomtype="多媒体教室",
            fixesroom=None,
            fixedtime=None,
            fixedbuilding=None,
            capmpus="西校区",
            combine=False
        ),
        sql.models.Course(
            cid=3,
            formclass="C班",
            popularity=40,
            teacherid=1,
            task="6-10:3",
            continuous=1,
            fixedroomtype="普通教室",
            fixesroom=None,
            fixedtime=None,
            fixedbuilding=None,
            capmpus="东校区",
            combine=False
        ),
        sql.models.Course(
            cid=4,
            formclass="D班",
            popularity=20,
            teacherid=3,
            task="3-4:4",
            continuous=4,
            fixedroomtype="实验室",
            fixesroom=None,
            fixedtime=None,
            fixedbuilding=None,
            capmpus="西校区",
            combine=False
        ),
    ]

    rooms = [
        sql.models.Room(
            rid=101,
            rname="101教室",
            rtype="普通教室",
            rcapacity=50,
            rcampus="东校区",
            rbuilding="教学楼A"
        ),
        sql.models.Room(
            rid=102,
            rname="102教室",
            rtype="多媒体教室",
            rcapacity=30,
            rcampus="西校区",
            rbuilding="教学楼B"
        ),
        sql.models.Room(
            rid=103,
            rname="103实验室",
            rtype="实验室",
            rcapacity=20,
            rcampus="西校区",
            rbuilding="实验楼A"
        ),
        sql.models.Room(
            rid=104,
            rname="104教室",
            rtype="普通教室",
            rcapacity=40,
            rcampus="东校区",
            rbuilding="教学楼B"
        ),
    ]



finally:
    #关闭
    cursor.close()
    print("exit to mysql")
    conn.close()

    print("OK")
