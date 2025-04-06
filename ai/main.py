import ga_optimizer
import sql.connect
import sql.models
from sql.models import *
from csp_solver import CSPScheduler
from hybid import HybridScheduler
from inheritance.ConstraintSolver import ConstraintSolver
from collections import defaultdict

#连接数据库
conn=sql.connect.connect()
cursor=conn.cursor()


def convert_to_schedules(best_solution):
    # 按课程、教室、教师、天、节次分组
    grouped = defaultdict(list)
    for entry in best_solution:
        course_uid, rid, teacher, week, day, slot = entry
        key = (course_uid, rid, teacher, day, slot)
        grouped[key].append(week)

    schedules = []
    for key, weeks in grouped.items():
        course_uid, rid, teacher, day, slot = key
        weeks_sorted = sorted(weeks)

        # 分割连续周次区间（如 [1,2,3,5,6,8] → [[1-3], [5-6], [8-8]）
        ranges = []
        if not weeks_sorted:
            continue

        start = end = weeks_sorted[0]
        for week in weeks_sorted[1:]:
            if week == end + 1:
                end = week
            else:
                ranges.append((start, end))
                start = end = week
        ranges.append((start, end))

        # 为每个连续区间生成记录
        for start_week, end_week in ranges:
            scid = f"{course_uid}_{rid}_{teacher}_{start_week}_{end_week}_{day}_{slot}"
            schedules.append(
                Schedule(
                    scid=scid,
                    course_uid=course_uid,
                    teacher=teacher,
                    rid=rid,
                    start_week=start_week,
                    end_week=end_week,
                    day=day,
                    slots=[slot]
                )
            )

    return schedules
#载入课程
'''课程号，教学班名，课程人数，老师（工号表示），时间，周节次，连排节次，指定教室类型，指定教室，指定时间，指定教学楼，开课校区,是否为合班，'''
def load_course():
    cursor.execute("SELECT tacode,taformclass,tapopularity,taclasshour ,taproperty,tateacherid,tahourweek,tacontinuous,tafixedtype,tafixedroom,tafixedtime,tafixedbuilding,tacampus FROM task")
    courses=[]#列表储存
    for row in cursor.fetchall():
        course=sql.models.Course(
            cid=row['tacode'],
            formclass=row['taformclass'],
            popularity=row['tapopularity'],
            total_hours=row['taclasshour'],
            taproperty=row['taproperty'],
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

    print(f"\n=== 数据加载完成 ===")
    print(f"课程总数: {len(courses)}")
    print(f"教室总数: {len(rooms)}")
    print(f"行政班总数: {len(myclasses)}")

    # 使用混合排课算法
    print("\n=== 开始排课 ===")
    scheduler = HybridScheduler(courses, rooms)
    schedule, unscheduled = scheduler.solve()

    schedules=convert_to_schedules(schedule)
    print("=== 转换结果 ===")
    for idx, schedule in enumerate(schedules, 1):
        print(f"\n记录 {idx}:")
        for key, value in schedule.to_dict().items():
            print(f"  {key}: {value}")
    # 计算排课率
    scheduled_courses = {entry[0] for entry in schedule}
    total_courses = len(courses)
    scheduling_rate = len(scheduled_courses) / total_courses * 100

    print("\n=== 排课结果 ===")
    print(f"排课成功率: {scheduling_rate:.2f}%")
    print(f"已排课程: {len(scheduled_courses)}/{total_courses}")
    print(f"排课记录总数: {len(schedule)}条")
    print(f"未排课程: {len(unscheduled)}门")

    # 打印前20条排课记录
    print("\n=== 排课详情（前20条）===")
    print("序号 | 课程ID | 教室ID | 教师ID | 周次 | 星期 | 节次")
    print("-" * 60)
    for i, entry in enumerate(schedule[:20]):
        print(f"{i+1:3} | {entry[0]:8} | {entry[1]:6} | {entry[2]:8} | 第{entry[3]:2}周 | 周{entry[4]} | 第{entry[5]}节")

    # 打印未排课程
    if unscheduled:
        print("\n=== 未排课程列表 ===")
        print("课程ID | 周数要求 | 连排节次 | 教室类型要求")
        print("-" * 60)
        for course in unscheduled[:20]:  # 只显示前20条
            weeks = ", ".join(f"{s}-{e}" for s, e, _ in course.time_slots)
            print(f"{course.uid:8} | {weeks:10} | {getattr(course, 'continuous', 1):8} | {getattr(course, 'fixedroomtype', '无'):12}")

    # 简单统计
    print("\n=== 简单统计 ===")
    room_usage = {}
    for entry in schedule:
        room_id = entry[1]
        room_usage[room_id] = room_usage.get(room_id, 0) + 1

    teacher_workload = {}
    for entry in schedule:
        teacher_id = entry[2]
        teacher_workload[teacher_id] = teacher_workload.get(teacher_id, 0) + 1

    print("\n教室使用频率TOP5:")
    for room_id, count in sorted(room_usage.items(), key=lambda x: -x[1])[:5]:
        print(f"教室 {room_id}: {count}次")

    print("\n教师授课量TOP5:")
    for teacher_id, count in sorted(teacher_workload.items(), key=lambda x: -x[1])[:5]:
        print(f"教师 {teacher_id}: {count}节课")

finally:
    # 关闭数据库连接
    cursor.close()
    conn.close()
    print("\n数据库连接已关闭")



