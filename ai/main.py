import ga_optimizer
import sql.connect
import sql.models
from sql.models import *
from csp_solver import CSPScheduler
from hybid import HybridScheduler
from inheritance.ConstraintSolver import ConstraintSolver
from collections import defaultdict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
def get_session():
    engine = create_engine("mysql+pymysql://zq:123456@localhost/myAI?charset=utf8mb4")
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
#开始新一轮实验
#连接数据库
conn=sql.connect.connect()
cursor=conn.cursor()
# 每节课的时间段映射（单位：小时）
SLOT_TIME_MAP = {
    1: (7.0, 9.0),    # 第1节
    2: (9.1, 11.0),   # 第2节
    3: (11.1, 13.0),  # 第3节
    4: (13.1, 15.0),   # 第4节
    5: (15.1, 17.0),  # 第5节
    6: (17.0, 19.0),   # 第6节
    7: (19.1, 21.0),  # 第7节
    8: (21.1, 23.0)    # 第8节
}

def convert_to_schedules(best_solution, courses):
    """将排课结果转换为合并后的时间段记录"""
    course_map = {course.uid: course for course in courses}

    # 按课程+教室+教师+星期+周次分组，同时收集节次信息
    schedule_groups = defaultdict(lambda: defaultdict(list))
    for entry in best_solution:
        course_uid, rid, teacher_uid, week, day, slot = entry
        if course_uid not in course_map:
            continue

        # 分组键：(课程, 教室, 教师, 星期, 周次)
        group_key = (course_uid, rid, teacher_uid, day, week)
        schedule_groups[group_key]['slots'].append(slot)

    schedules = []
    record_id = 1
    for key, slot_data in schedule_groups.items():
        course_uid, rid, teacher_uid, day, week = key
        slots = slot_data['slots']
        course = course_map[course_uid]
        teacher_name = getattr(course, 'teachername', None) or teacher_uid.split('-')[-1]
        teacher_id = getattr(course, 'teacherid', None) or teacher_uid.split('-')[0]

        # 合并连续节次（如[1,2,3,5]→[(1,3),(5,5)]）
        merged_slots = merge_continuous_numbers(sorted(slots))

        # 创建slots字符串（如"1-3,5"）
        slot_str = ",".join(f"{s}-{e}" if s != e else str(s) for s, e in merged_slots)

        schedules.append(
            Schedule(
                scid=record_id,
                sctask=course.formclassid,
                scteacherid=teacher_id,
                scroom=rid,
                scbegin_week=week,
                scend_week=week,
                scday_of_week=day,
                scbegin_time=0,  # 设置为0
                scend_time=0,   # 设置为0
                scteachername=teacher_name,
                scslot=slot_str  # 新增的slots字段
            )
        )
        record_id += 1

    # 第二次合并：合并相同课程+教室+教师+星期+节次模式的连续周次
    final_schedules = []
    temp_dict = defaultdict(list)

    for s in schedules:
        # 使用除周次外的所有属性作为合并键
        merge_key = (s.sctask, s.scroom, s.scteacherid, s.scday_of_week, s.scslot)
        temp_dict[merge_key].append(s.scbegin_week)  # 只需要周次

    record_id = 1
    for key, weeks in temp_dict.items():
        sctask, scroom, scteacherid, scday_of_week, scslot = key
        first_schedule = next(s for s in schedules if
                              (s.sctask, s.scroom, s.scteacherid, s.scday_of_week, s.scslot) == key)

        # 合并连续周次
        merged_weeks = merge_continuous_numbers(sorted(weeks))

        for start_week, end_week in merged_weeks:
            final_schedules.append(
                Schedule(
                    scid=record_id,
                    sctask=sctask,
                    scteacherid=scteacherid,
                    scroom=scroom,
                    scbegin_week=start_week,
                    scend_week=end_week,
                    scday_of_week=scday_of_week,
                    scbegin_time=0,
                    scend_time=0,
                    scteachername=first_schedule.scteachername,
                    scslot=scslot
                )
            )
            record_id += 1

    return final_schedules

def merge_continuous_numbers(numbers):
    """合并连续数字 如[1,2,3,5,6]→[(1,3),(5,6)]"""
    if not numbers:
        return []

    ranges = []
    start = end = numbers[0]

    for num in numbers[1:]:
        if num == end + 1:
            end = num
        else:
            ranges.append((start, end))
            start = end = num
    ranges.append((start, end))

    return ranges

#载入课程
'''课程号，教学班名，课程人数，老师（工号表示），时间，周节次，连排节次，指定教室类型，指定教室，指定时间，指定教学楼，开课校区,是否为合班，'''
def load_course():
    cursor.execute("SELECT tacode,taformclass,taname,taformclassid,tapopularity,taclasshour ,taproperty,tateacherid,tateachername,tahourweek,tacontinuous,tafixedtype,tafixedroom,tafixedtime,tafixedbuilding,tacampus FROM task")
    courses=[]#列表储存
    for row in cursor.fetchall():
        course=sql.models.Course(
            cid=row['tacode'],
            formclass=row['taformclass'],
            taname=row['taname'],
            formclassid=row['taformclassid'],
            popularity=row['tapopularity'],
            total_hours=row['taclasshour'],
            taproperty=row['taproperty'],
            teacherid=row['tateacherid'],
            teachername=row['tateachername'],
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
    """将数据库课程转换为CSPScheduler需要的格式（保留所有属性）"""
    prepared = []
    for course in raw_courses:
        # 确保原始课程有teacher_uid
        if not hasattr(course, 'teacher_uid'):
            course.teacher_uid = f"{course.teacherid}-{course.teachername}"

        # 创建新对象并复制所有必要属性
        prepared_course = type('Course', (), vars(course).copy())  # 复制所有属性

        # 添加/覆盖特定属性
        prepared_course.uid = f"{course.cid}_{course.formclass}"
        prepared_course.time_slots = parse_time_slots(course.task)

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
    # 数据加载后检查
    raw_rooms = load_room()
    myclasses = load_myclass()

    # 转换数据格式
    courses = prepare_courses(raw_courses)
    rooms = prepare_rooms(raw_rooms)

    print(f"\n=== 数据加载完成 ===")
    sample_course = courses[0]
    print("\n验证课程属性:")
    print(f"uid: {sample_course.uid}")
    print(f"teacher_uid: {getattr(sample_course, 'teacher_uid', '属性不存在')}")
    print(f"所有属性: {vars(sample_course).keys()}")
    print(f"课程总数: {len(courses)}")
    print(f"教室总数: {len(rooms)}")
    print(f"行政班总数: {len(myclasses)}")

    # 使用混合排课算法
    print("\n=== 开始排课 ===")
    scheduler = HybridScheduler(courses, rooms)
    schedule, unscheduled = scheduler.solve()

    schedules=convert_to_schedules(schedule,courses)
    print("=== 转换结果 ===")
    for idx, schedule in enumerate(schedules, 1):
        print(f"\n记录 {idx}:")
        for key, value in schedule.to_dict().items():
            print(f"  {key}: {value}")
    

    session=get_session()
    session.query(Schedule).delete()
    session.commit();

    session.add_all(schedules)
    session.commit()
    session.close()


# 计算排课率
    '''scheduled_courses = {entry[0] for entry in schedule}
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
            print(f"{course.uid:8} | {weeks:10} | {getattr(course, 'continuous', 1):8} | {getattr(course, 'fixedroomtype', '无'):12}")'''

finally:
    # 关闭数据库连接
    cursor.close()
    conn.close()
    print("\n数据库连接已关闭")



