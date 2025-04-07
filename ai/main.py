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
    6: (17., 19.0),   # 第6节
    7: (19.1, 21.0),  # 第7节
    8: (21.1, 23.0)    # 第8节
}

def convert_to_schedules(best_solution):
    # 假设 SLOT_TIME_MAP 是节次到时间的映射，例如：
    # SLOT_TIME_MAP = {1: (8.0, 8.5), 2: (8.5, 9.0), ...}
    # 请根据实际情况补充定义

    # 按周、天、课程、教室、教师分组，收集该周该天的所有节次
    weekly_entries = defaultdict(list)
    for entry in best_solution:
        course_uid, rid, teacher, week, day, slot = entry
        key = (course_uid, rid, teacher, week, day)
        weekly_entries[key].append(slot)

    # 处理每个周次的节次，合并连续节次
    processed = []
    for key, slots in weekly_entries.items():
        course_uid, rid, teacher, week, day = key
        sorted_slots = sorted(slots)
        # 检查节次是否连续
        is_continuous = all(sorted_slots[i] == sorted_slots[i-1] + 1 for i in range(1, len(sorted_slots)))
        if not is_continuous:
            continue  # 忽略非连续节次（根据需求调整）
        start_slot = sorted_slots[0]
        end_slot = sorted_slots[-1]
        processed.append((course_uid, rid, teacher, week, day, start_slot, end_slot))

    # 按课程、教室、教师、天、起始终止节次分组，合并周次范围
    grouped = defaultdict(list)
    for entry in processed:
        course_uid, rid, teacher, week, day, start_slot, end_slot = entry
        group_key = (course_uid, rid, teacher, day, start_slot, end_slot)
        grouped[group_key].append(week)

    schedules = []
    for group_key, weeks in grouped.items():
        course_uid, rid, teacher, day, start_slot, end_slot = group_key
        weeks_sorted = sorted(weeks)
        # 合并周次为连续区间
        ranges = []
        start_week = end_week = weeks_sorted[0]
        for week in weeks_sorted[1:]:
            if week == end_week + 1:
                end_week = week
            else:
                ranges.append((start_week, end_week))
                start_week = end_week = week
        ranges.append((start_week, end_week))

        # 计算起止时间（需确保 SLOT_TIME_MAP 已定义）
        start_time = SLOT_TIME_MAP[start_slot][0]
        end_time = SLOT_TIME_MAP[end_slot][1]

        # 生成 Schedule 对象
        for start_w, end_w in ranges:
            scid = f"{course_uid}_{rid}_{teacher}_{start_w}_{end_w}_{day}_{start_slot}-{end_slot}"
            schedules.append(
                Schedule(
                    scid=scid,
                    sctask=course_uid,  # 假设 task 使用 course_uid 填充
                    scteacher=teacher,
                    scroom=rid,
                    scbegin_week=start_w,
                    scend_week=end_w,
                    scday_of_week=day,
                    scbegin_time=start_time,
                    scend_time=end_time
                )
            )
    return schedules
#载入课程
'''课程号，教学班名，课程人数，老师（工号表示），时间，周节次，连排节次，指定教室类型，指定教室，指定时间，指定教学楼，开课校区,是否为合班，'''
def load_course():
    cursor.execute("SELECT tacode,taformclass,tapopularity,taclasshour ,taproperty,tateacherid,tateachername,tahourweek,tacontinuous,tafixedtype,tafixedroom,tafixedtime,tafixedbuilding,tacampus FROM task")
    courses=[]#列表储存
    for row in cursor.fetchall():
        course=sql.models.Course(
            cid=row['tacode'],
            formclass=row['taformclass'],
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

    schedules=convert_to_schedules(schedule)
    print("=== 转换结果 ===")
    for idx, schedule in enumerate(schedules, 1):
        print(f"\n记录 {idx}:")
        for key, value in schedule.to_dict().items():
            print(f"  {key}: {value}")
    '''
    写入数据库
    session=get_session()
    session = get_session()

    schedules = [
        Schedule(scid="001", sctask='111',scteacher="T001", scroom="R101",
                 scbegin_week=1, scend_week=8, scday_of_week=1,  scbegin_time=8.0, scend_time=9.5),
        # 更多数据...
    ]

    session.add_all(schedules)
    session.commit()
    session.close()

    '''
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

finally:
    # 关闭数据库连接
    cursor.close()
    conn.close()
    print("\n数据库连接已关闭")



