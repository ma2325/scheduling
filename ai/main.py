import ga_optimizer
import sql.connect
import sql.models
from csp_solver import CSPScheduler
from ga_optimizer import GAOptimizer
from inheritance.ConstraintSolver import ConstraintSolver


#连接数据库
conn=sql.connect.connect()
cursor=conn.cursor()

#载入课程
'''课程号，教学班名，课程人数，老师（工号表示），时间，周节次，连排节次，指定教室类型，指定教室，指定时间，指定教学楼，开课校区,是否为合班，'''
def load_course():
    cursor.execute("SELECT tacode,taformclass,tapopularity,taclasshour ,tateacherid,tahourweek,tacontinuous,tafixedtype,tafixedroom,tafixedtime,tafixedbuilding,tacampus FROM task")
    courses=[]#列表储存
    for row in cursor.fetchall():
        course=sql.models.Course(
            cid=row['tacode'],
            formclass=row['taformclass'],
            popularity=row['tapopularity'],
            total_hours=row['taclasshour'],
            teacherid=row['tateacherid'],
            task=row['tahourweek'],
            continuous=row['tacontinuous'],
            fixedroomtype=row['tafixedtype'],
            fixedroom=row['tafixedroom'],
            fixedtime=row['tafixedtime'],
            fixedbuilding=row['tafixedbuilding'],
            capmpus=row['tacampus']
        )
        courses.append(course)
        print(course.cid,course.fixedroomtype)
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
# 在main.py中添加以下函数
def parse_time_slots(task_str):
    """将"1-8:2,10-15:2"格式的字符串解析为[(start,end,lessons),...]格式"""
    time_slots = []
    if not task_str:
        return [(1, 20, 1)]  # 默认全学期每周1节

    for part in task_str.split(','):
        if ':' in part:
            weeks, lessons = part.split(':')
            if '-' in weeks:
                start, end = map(int, weeks.split('-'))
            else:
                start = end = int(weeks)
            time_slots.append((start, end, int(lessons)))
        else:
            if '-' in part:
                start, end = map(int, part.split('-'))
            else:
                start = end = int(part)
            time_slots.append((start, end, 1))
    return time_slots

def prepare_courses(raw_courses):
    """将数据库课程转换为CSPScheduler需要的格式"""
    prepared = []
    for course in raw_courses:
        # 创建符合CSPScheduler期望的课程对象
        prepared_course = type('Course', (), {
            'uid': f"{course.cid}_{course.formclass}",
            'time_slots': parse_time_slots(course.task),
            'total_hours': course.total_hours,
            'continuous': course.continuous,
            'popularity': course.popularity,
            'teacherid': course.teacherid,
            'fixedroomtype': course.fixedroomtype,
            'fixedroom': course.fixedroom,
            # 添加其他必要属性...
        })
        prepared.append(prepared_course)
    return prepared

def prepare_rooms(raw_rooms):
    """将数据库教室转换为CSPScheduler需要的格式"""
    prepared = []
    for room in raw_rooms:
        prepared_room = type('Room', (), {
            'rid': room.rid,
            'rtype': room.rtype,
            'rname': room.rname,
            'rcapacity': room.rcapacity,
            # 添加其他必要属性...
        })
        prepared.append(prepared_room)
    return prepared
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
    # 从数据库加载原始数据
    raw_courses = load_course()
    raw_rooms = load_room()
    myclasses = load_myclass()

    # 转换数据格式
    courses = prepare_courses(raw_courses)
    rooms = prepare_rooms(raw_rooms)


    constraint_checker = ConstraintSolver(courses, rooms)

    # 2. 使用CSP生成初始解
    csp_scheduler = CSPScheduler(courses, rooms)
    initial_solution, unscheduled = csp_scheduler.solve()

    if not initial_solution:
        print("CSP阶段未能生成有效初始解")

    # 3. 使用GA优化
    ga_optimizer = GAOptimizer(
        courses=courses,
        rooms=rooms,
        constraint_checker=constraint_checker  # 确保传入的是ConstraintSolver实例
    )

    optimized_solution = ga_optimizer.optimize(initial_solution=initial_solution)

    if optimized_solution:
        print("优化成功！")

        # 计算排课率
        scheduled_courses = {entry[0] for entry in optimized_solution}  # 获取已排课程ID
        total_courses = len(courses)  # 总课程数
        scheduling_rate = len(scheduled_courses) / total_courses * 100

        print("\n=== 最终课表 ===")
        print(f"优化完成，最终适应度: {ga_optimizer.fitness(optimized_solution):.2f}")
        print(f"排课率: {scheduling_rate:.2f}% ({len(scheduled_courses)}/{total_courses})")

        # 可选：显示未排课程
        unscheduled_courses = [c for c in courses if c.uid not in scheduled_courses]
        if unscheduled_courses:
            print("\n未排课程列表:")
            for course in unscheduled_courses:
                print(f"- {course.uid} ({course.cname})")
    else:
        print("优化失败")

finally:
    # 关闭数据库连接
    cursor.close()
    conn.close()
    print("数据库连接已关闭")

    '''
    # 测试数据
    courses = [
        sql.models.Course(
            cid=1,
            formclass="A班",
            popularity=30,
            total_hours=28,
            teacherid=1,
            task="1-8:2,10-15:2",
            continuous=2,
            fixedroomtype="普通教室",
            fixedroom=None,
            fixedtime=None,
            fixedbuilding=None,
            capmpus="东校区",
            combine=False
        ),
        sql.models.Course(
            cid=2,
            formclass="B班",
            popularity=25,
            total_hours=6,
            teacherid=2,
            task="2-4:2",
            continuous=2,
            fixedroomtype="多媒体教室",
            fixedroom="102教室",
            fixedtime=None,
            fixedbuilding=None,
            capmpus="西校区",
            combine=False
        ),
        sql.models.Course(
            cid=3,
            formclass="C班",
            popularity=40,
            total_hours=15,
            teacherid=1,
            task="6-10:2",
            continuous=2,
            fixedroomtype="普通教室",
            fixedroom=None,
            fixedtime=None,
            fixedbuilding=None,
            capmpus="东校区",
            combine=False
        ),
        sql.models.Course(
            cid=4,
            formclass="D班",
            popularity=20,
            total_hours=8,
            teacherid=3,
            task="3-4:4",
            continuous=4,
            fixedroomtype="实验室",
            fixedroom=None,
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
    '''


