import random
from collections import defaultdict
from typing import List
from main import courses, rooms
import test
from sql.models import Schedule
import json
import deepseek
from collections import defaultdict
import time
from ConstraintSolver import ConstraintSolver
#连排开始规则
CONTINUOUS_SLOT_RULES = {
    2: [1, 3, 5, 7],  # 两节连排允许的开始节次
    4: [1, 3, 5],     # 四节连排允许的开始节次
    # 可以继续添加其他连排类型的规则
}
#可删
#这里是绝望的zq进行新尝试
#这里小数据是可以的
#总课程应该为66944
'''三维时间模型'''
WEEKS_IN_SEMESTER = 20  # 总教学周数
DAYS_PER_WEEK = 5       # 每周上课天数 (周一至周五)
SLOTS_PER_DAY = 8       # 每天节次数
def generate_weekly_pattern(course):
    """为课程生成周模式，确保符合continuous和task要求"""
    continuous = getattr(course, 'continuous', 1)
    total_lessons_per_week = sum(lpw for _, _, lpw in course.time_slots)

    # 检查课时数是否匹配continuous设置
    if continuous > 1:
        if total_lessons_per_week % continuous != 0:
            raise ValueError(f"课程{course.cid}的每周课时数{total_lessons_per_week}不匹配连排设置{continuous}")

    pattern = []

    if continuous > 1:
        # 连排课程处理
        allowed_days = list(range(1, DAYS_PER_WEEK + 1))
        allowed_starts = CONTINUOUS_SLOT_RULES.get(continuous, [])

        # 计算需要多少组连排
        groups_needed = total_lessons_per_week // continuous

        # 确保同一天不排多组连排（除非必须）
        for _ in range(groups_needed):
            day = random.choice(allowed_days)
            start = random.choice(allowed_starts)
            pattern.append((day, start, continuous))

            # 减少选择同一天的概率
            allowed_days = [d for d in allowed_days if d != day] or list(range(1, DAYS_PER_WEEK + 1))
    else:
        # 非连排课程：均匀分布在周中
        days = random.sample(range(1, DAYS_PER_WEEK + 1), min(total_lessons_per_week, DAYS_PER_WEEK))
        for day in days:
            slot = random.randint(1, SLOTS_PER_DAY)
            pattern.append((day, slot, 1))

    return pattern
def calculate_priority(course):
    """计算课程优先级"""
    score = 0

    # 1. 课程性质（必修课优先）
    '''
    if course.course_type == "必修":
        score += 100
    elif course.course_type == "选修":
        score += 50
    '''
    # 2. 学时（学时多的优先）
    score += course.total_hours

    # 3. 学生规模（人数多的优先）
    score += course.popularity * 0.5

    # 4. 特殊要求（有固定教室的优先）
    if course.fixedroom:
        score += 30

    return score
def find_available_room(course, pattern, resources, rooms):
    """带详细调试信息的教室查找函数"""
    print(f"\n=== 正在为课程 {course.uid} 寻找教室 ===")
    print(f"课程需求: 类型={getattr(course, 'fixedroomtype', '无')}, 固定教室={getattr(course, 'fixedroom', '无')}")
    print(f"时间模式: {pattern}")

    # 策略1：固定教室
    if hasattr(course, 'fixedroom') and course.fixedroom:
        print(f"\n[策略1] 查找固定教室: {course.fixedroom}")
        fixed_room = next((r for r in rooms if r.rname == course.fixedroom), None)
        if fixed_room:
            print(f"找到固定教室: {fixed_room.rid}({fixed_room.rtype}), 容量={fixed_room.rcapacity}")
            if is_room_available(fixed_room, course, pattern, resources):
                print("✅ 固定教室可用")
                return fixed_room
            else:
                print("❌ 固定教室时间冲突")
        else:
            print(f"⚠️ 警告: 指定的固定教室 {course.fixedroom} 不存在")

    # 策略2：精确类型匹配
    required_type = getattr(course, 'fixedroomtype', None)
    if required_type:
        print(f"\n[策略2] 查找 {required_type} 类型教室")
        candidates = [r for r in rooms if r.rtype == required_type]
        print(f"找到 {len(candidates)} 间 {required_type} 教室")

        if candidates:
            # 按容量排序
            candidates.sort(key=lambda r: abs(r.rcapacity - course.popularity))
            for i, room in enumerate(candidates[:3]):  # 只检查前3个最合适的
                print(f"尝试 #{i+1}: {room.rid} (容量:{room.rcapacity})")
                if is_room_available(room, course, pattern, resources):
                    print(f"✅ 找到可用教室: {room.rid}")
                    return room
                else:
                    print("❌ 时间冲突")
            print(f"已尝试 {len(candidates)} 间教室均不可用")

    # 策略3：备用类型
    backup_types = {
        "多媒体教室": ["智慧教室", "普通教室"],
        "实验室": ["实训室"]
    }.get(required_type, [])

    print(f"\n[策略3] 尝试备用类型: {backup_types}")
    for backup_type in backup_types:
        backup_candidates = [r for r in rooms if r.rtype == backup_type]
        print(f"找到 {len(backup_candidates)} 间 {backup_type} 教室")

        for room in backup_candidates:
            if is_room_available(room, course, pattern, resources):
                print(f"✅ 找到备用教室: {room.rid}({room.rtype})")
                return room

    # 策略4：强制分配
    print("\n[策略4] 尝试强制分配任何可用教室")
    all_rooms_sorted = sorted(rooms, key=lambda r: abs(r.rcapacity - course.popularity))
    for room in all_rooms_sorted[:5]:  # 只检查前5个最接近的
        print(f"尝试强制分配: {room.rid}({room.rtype})")
        if is_room_available(room, course, pattern, resources):
            print(f"⚠️ 强制分配: {room.rid}({room.rtype})")
            return room

    print("❌ 所有策略均失败，无法找到合适教室")
    return None

def is_room_available(room, course, pattern, resources):
    """带冲突详细信息的检查函数"""
    required_weeks = get_course_weeks(course)
    print(f"检查教室 {room.rid} 的可用性...")

    for day, start_slot, length in pattern:
        for week in required_weeks:
            for offset in range(length):
                slot = start_slot + offset
                if (week, day, slot) in resources['rooms'][room.rid]:
                    conflict_entry = next(
                        (e for e in resources['timetable']
                         if e[1] == room.rid and e[3] == week and e[4] == day and e[5] == slot),
                        None
                    )
                    if conflict_entry:
                        print(f"❌ 冲突详情: 第{week}周 周{day} 第{slot}节")
                        print(f"   已被课程 {conflict_entry[0]} 占用")
                    return False
    return True
def has_conflict(entry, resources):
    """
    检查单个课程安排是否有冲突
    :param entry: 课程安排项 (cid, rid, teacherid, week, day, slot)
    :param resources: 资源占用情况
    :return: True如果有冲突
    """
    cid, rid, teacherid, week, day, slot = entry

    # 1. 检查教师时间冲突
    teacher_key = (week, day, slot)
    if teacher_key in resources['teachers'].get(teacherid, set()):
        return True

    # 2. 检查教室时间冲突
    room_key = (week, day, slot)
    if room_key in resources['rooms'].get(rid, set()):
        return True

    return False
def find_alternative_pattern(course, resources, max_attempts=10):
    """
    为课程寻找替代周模式
    :param course: 课程对象
    :param resources: 当前资源占用
    :param max_attempts: 最大尝试次数
    :return: 新周模式或None
    """
    continuous = getattr(course, 'continuous', 1)
    lessons_per_week = sum(lpw for _, _, lpw in course.time_slots)
    required_weeks = get_course_weeks(course)

    for _ in range(max_attempts):
        # 生成新周模式
        new_pattern = generate_weekly_pattern(course)

        # 检查新模式是否可用
        pattern_ok = True

        for day, start_slot, length in new_pattern:
            for week in required_weeks:
                # 检查教师时间
                for offset in range(length):
                    slot = start_slot + offset
                    if (week, day, slot) in resources['teachers'].get(course.teacherid, set()):
                        pattern_ok = False
                        break

                if not pattern_ok:
                    break

            if not pattern_ok:
                break

        if pattern_ok:
            return new_pattern

    return None  # 找不到合适模式
def update_timetable(timetable, resources, index_to_replace, new_pattern):
    """
    更新课表中的一项安排
    :param timetable: 当前课表列表
    :param resources: 资源占用字典
    :param index_to_replace: 要替换的条目索引
    :param new_pattern: 新周模式 [(day, start_slot, length), ...]
    :return: 更新后的课表
    """
    if index_to_replace >= len(timetable):
        return timetable

    # 1. 获取原课程信息
    old_entry = timetable[index_to_replace]
    cid, old_rid, teacherid, old_week, old_day, old_slot = old_entry
    course = next((c for c in courses if c.uid == cid), None)

    if not course:
        return timetable  # 如果未找到课程，保留原状态

    # 2. 移除原安排占用的资源
    for week in get_course_weeks(course):
        for day, start_slot, length in get_current_pattern(timetable, cid):
            for offset in range(length):
                slot = start_slot + offset
                resources['teachers'][teacherid].discard((week, day, slot))
                resources['rooms'][old_rid].discard((week, day, slot))

    # 3. 删除原课程所有相关条目
    timetable = [e for e in timetable if e[0] != cid]

    # 4. 添加新安排
    room = find_available_room(course, new_pattern, resources, rooms)
    if not room:
        return timetable  # 无法找到教室，保留原状态

    for week in get_course_weeks(course):
        for day, start_slot, length in new_pattern:
            for offset in range(length):
                slot = start_slot + offset
                new_entry = (cid, room.rid, teacherid, week, day, slot)
                timetable.append(new_entry)
                # 更新资源占用
                resources['teachers'][teacherid].add((week, day, slot))
                resources['rooms'][room.rid].add((week, day, slot))

    return timetable
def get_course_weeks(course):
    """获取课程所有教学周（考虑多个时间段）"""
    weeks = []
    for start, end, _ in course.time_slots:
        weeks.extend(range(start, end + 1))
    return weeks

def resolve_conflicts(timetable, resources, courses, rooms):
    """尝试解决冲突"""
    # 按优先级升序排序（先尝试调整低优先级课程）
    sorted_entries = sorted(timetable, key=lambda x: calculate_priority(next(
        c for c in courses if c.uid == x[0])))

    for i, entry in enumerate(sorted_entries):
        cid, rid, tid, week, day, slot = entry
        course = next((c for c in courses if c.uid == cid), None)

        if not course:
            continue

        # 检查是否有冲突
        if has_conflict(entry, resources):
            # 尝试找新时间
            new_pattern = find_alternative_pattern(course, resources)
            if new_pattern:
                # 替换原有安排
                update_timetable(timetable, resources, i, new_pattern)
                return True

    return False  # 无法解决

def get_current_pattern(timetable, cid):
    """
    获取课程当前周模式
    :param timetable: 课表
    :param cid: 课程的唯一标识符 uid
    :return: 周模式 [(day, start_slot, length), ...]
    """
    course_entries = [e for e in timetable if e[0] == cid]
    if not course_entries:
        return []

    # 获取第一周的安排作为模式
    first_week = min(e[3] for e in course_entries)
    week_entries = [e for e in course_entries if e[3] == first_week]

    pattern = []
    current_day = None
    current_start = None
    current_length = 0

    for entry in sorted(week_entries, key=lambda x: (x[4], x[5])):
        _, _, _, _, day, slot = entry

        if day != current_day or slot != current_start + current_length:
            if current_day is not None:
                pattern.append((current_day, current_start, current_length))
            current_day = day
            current_start = slot
            current_length = 1
        else:
            current_length += 1

    if current_day is not None:
        pattern.append((current_day, current_start, current_length))

    return pattern
# 在初始化时按优先级排序
sorted_courses = sorted(courses, key=calculate_priority, reverse=True)
class TimeSlot:
    """三维时间点表示 (周次, 周几, 节次)"""
    def __init__(self, week, day, slot):
        self.week = week    # 1-20教学周
        self.day = day      # 1-5 (周一至周五)
        self.slot = slot    # 1-8节

    def __str__(self):
        return f"第{self.week}周 周{self.day} 第{self.slot}节"

'''根据课程的time_slots生成所有有效时间点'''
def generate_course_slots(course):
    all_slots = []
    for start_week, end_week, lessons_per_week in course.time_slots:
        continuous = getattr(course, 'continuous', 1)
        groups_needed_per_week = lessons_per_week // continuous

        for week in range(start_week, end_week + 1):
            # 随机打乱周几的顺序，避免总是从周一开始
            days = list(range(1, DAYS_PER_WEEK + 1))
            random.shuffle(days)

            for day in days:
                if continuous > 1:
                    allowed_starts = CONTINUOUS_SLOT_RULES.get(continuous, [])
                    for start in allowed_starts:
                        if start + continuous - 1 <= SLOTS_PER_DAY:
                            group = [TimeSlot(week, day, start + i) for i in range(continuous)]
                            all_slots.append(group)
                else:
                    # 对于非连排课程，更均匀地分布在不同的天
                    slots = list(range(1, SLOTS_PER_DAY + 1))
                    random.shuffle(slots)
                    for slot in slots[:groups_needed_per_week]:
                        all_slots.append([TimeSlot(week, day, slot)])

                # 如果已经找到足够的组，就停止
                if len(all_slots) >= groups_needed_per_week * (end_week - start_week + 1):
                    break
    return all_slots

'''统计未被安排的课'''
def count_unscheduled_courses(timetable):
    scheduled_courses = {entry[0] for entry in timetable}
    unscheduled_courses = [c.cid for c in courses if c.cid not in scheduled_courses]
    return len(unscheduled_courses), unscheduled_courses

'''初始种群，贪心'''
'''初始种群，贪心'''
import random
from collections import defaultdict

def initialize_population_improved(size, courses, rooms, max_attempts=300):
    """
    终极版初始种群生成器
    特性：
    1. 多级教室分配策略（固定教室 > 精确类型 > 备用类型 > 强制分配）
    2. 动态优先级调整
    3. 冲突最小化设计
    4. 详细调试输出
    """
    print("\n=== 初始化种群 - 终极版 ===")
    print(f"课程总数: {len(courses)} | 教室总数: {len(rooms)}")

    # 预计算资源池
    room_pools = defaultdict(list)
    for room in rooms:
        room_pools[room.rtype].append(room)

    # 教室类型统计
    type_stats = {k: len(v) for k, v in room_pools.items()}
    print("教室类型统计:", type_stats)

    population = []
    global_start = time.time()

    for pop_num in range(size):
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            timetable = []
            resources = {
                "teachers": defaultdict(set),
                "rooms": defaultdict(set),
                "timetable": []  # 用于存储完整排课记录
            }

            # 动态课程排序（优先级 + 约束严格度）
            sorted_courses = sorted(
                courses,
                key=lambda x: (
                    -calculate_priority(x),
                    -sum(lpw for _, _, lpw in x.time_slots),
                    len([r for r in rooms if r.rtype == getattr(x, 'fixedroomtype', '')]),
                    random.random()
                ),
                reverse=True
            )

            success_count = 0
            for course_idx, course in enumerate(sorted_courses):
                # 获取教室候选池（多级策略）
                candidates = []
                if getattr(course, 'fixedroom', None):
                    fixed_room = next((r for r in rooms if r.rname == course.fixedroom), None)
                    candidates = [fixed_room] if fixed_room else []
                else:
                    required_type = getattr(course, 'fixedroomtype', None)
                    if required_type:
                        candidates = room_pools.get(required_type, [])
                        # 添加备用类型
                        backup_types = {
                            "多媒体教室": ["智慧教室", "普通教室"],
                            "实验室": ["实训室"]
                        }.get(required_type, [])
                        for bt in backup_types:
                            candidates.extend(room_pools.get(bt, []))

                # 智能分配尝试
                scheduled = False
                for time_slot in course.time_slots:
                    start_week, end_week, lpw = time_slot
                    weeks = list(range(start_week, end_week + 1))
                    pattern = generate_weekly_pattern(course)

                    # 尝试原始模式
                    room = find_available_room_smart(
                        course, pattern, weeks, resources, candidates
                    )

                    # 尝试备用模式（最多3次）
                    retry_count = 0
                    while not room and retry_count < 3:
                        new_pattern = generate_alternative_pattern(course, resources)
                        room = find_available_room_smart(
                            course, new_pattern, weeks, resources, candidates
                        )
                        retry_count += 1

                    if room:
                        # 添加到时间表
                        for week in weeks:
                            for day, start_slot, length in pattern:
                                for offset in range(length):
                                    slot = start_slot + offset
                                    entry = (
                                        course.uid, room.rid, course.teacherid,
                                        week, day, slot
                                    )
                                    timetable.append(entry)
                                    resources["teachers"][course.teacherid].add((week, day, slot))
                                    resources["rooms"][room.rid].add((week, day, slot))
                                    resources["timetable"].append(entry)
                        success_count += 1
                        scheduled = True
                        break

                # 课程安排失败日志
                if not scheduled:
                    print(f"\n❌ 课程安排失败: {course.uid}")
                    print(f"  需求: 类型={getattr(course, 'fixedroomtype', '无')} 固定={getattr(course, 'fixedroom', '无')}")
                    print(f"  时段: {course.time_slots}")
                    if candidates:
                        print(f"  候选教室: {len(candidates)}间 (示例: {candidates[0].rid if candidates else '无'})")
                    else:
                        print("  无可用候选教室!")

            # 验证并加入种群
            if timetable:
                constraint_ok = ConstraintSolver(courses, rooms).check_hard_constraints(timetable)
                unique_courses = len(set(e[0] for e in timetable))

                print(f"\n尝试 #{attempt} 结果: "
                      f"课程={unique_courses}/{len(courses)} "
                      f"约束={constraint_ok} "
                      f"耗时={time.time()-global_start:.1f}s")

                if constraint_ok:
                    population.append(timetable)
                    print(f"✅ 成功生成个体 {len(population)}/{size} "
                          f"安排率={unique_courses*100/len(courses):.1f}%")
                    break

        # 终止条件检查
        if attempt >= max_attempts:
            print(f"⚠️ 无法生成更多个体 (已达最大尝试次数 {max_attempts})")
            break

    # 最终统计
    print("\n=== 初始化完成 ===")
    stats = {
        "总个体数": len(population),
        "平均课程安排率": f"{sum(len(set(e[0] for e in ind)) for ind in population)*100/(len(population)*len(courses)):.1f}%",
        "总耗时": f"{time.time()-global_start:.1f}s"
    }
    print("\n".join(f"{k}: {v}" for k, v in stats.items()))

    return population

def find_available_room_smart(course, pattern, weeks, resources, candidates):

    """智能教室查找器（带优先级排序）"""
    if not candidates:
        return None

    # 按适配度排序（容量最接近优先）
    candidates_sorted = sorted(
        candidates,
        key=lambda r: (
            abs(r.rcapacity - course.popularity),  # 容量匹配度
            len(resources["rooms"][r.rid]),        # 当前使用频次
            random.random()                        # 随机因子
        )
    )

    for room in candidates_sorted[:50]:  # 仅检查前50个最合适的
        available = True
        for day, start_slot, length in pattern:
            for week in weeks:
                for offset in range(length):
                    slot = start_slot + offset
                    if (week, day, slot) in resources["rooms"][room.rid]:
                        available = False
                        break
                if not available:
                    break
            if not available:
                break

        if available:
            return room

    return None

def generate_alternative_pattern(course, resources):
    """生成替代时间模式"""
    continuous = getattr(course, 'continuous', 1)
    if continuous > 1:
        # 连排课程尝试不同起始节次
        allowed_starts = CONTINUOUS_SLOT_RULES.get(continuous, [1, 3, 5, 7])
        day = random.randint(1, DAYS_PER_WEEK)
        start = random.choice(allowed_starts)
        return [(day, start, continuous)]
    else:
        # 非连排课程尝试不同时间段
        day = random.randint(1, DAYS_PER_WEEK)
        slot = random.randint(1, SLOTS_PER_DAY)
        return [(day, slot, 1)]


def find_available_room_for_pattern(course, pattern, weeks, resources, rooms, max_tries=5):
    """为特定模式寻找可用教室"""

    # 1️⃣ **筛选可用教室**
    if course.fixedroom:
        candidates = [r for r in rooms if r.rname == course.fixedroom]
    else:
        candidates = [r for r in rooms if r.rtype == course.fixedroomtype]

    # **⚠️ 添加调试信息**
    if not candidates:
        print(f"❌ 课程 {course.cname} 没有符合类型 {course.fixedroomtype} 的教室可用！")
        return None

    # 2️⃣ **随机尝试最多 max_tries 次**
    for _ in range(max_tries):
        room = random.choice(candidates)
        if not room:
            continue  # 避免 None 问题

        available = True  # 该教室是否可用
        for week in weeks:
            for day, start_slot, length in pattern:
                for offset in range(length):
                    slot = start_slot + offset
                    # **检查是否有冲突**
                    if ((week, day, slot) in resources["teachers"].get(course.teacherid, set()) or
                            (week, day, slot) in resources["rooms"].get(room.rid, set())):
                        available = False
                        break  # **冲突发生，跳出 slot 检查**
                if not available:
                    break  # **冲突发生，跳出 day 检查**
            if not available:
                break  # **冲突发生，跳出 week 检查**

        if available:
            #print(f"✅ 课程 {course.cid} 成功分配到教室 {room.rname} (类型: {room.rtype})")
            return room

    # **所有尝试失败**
    print(f"❌ 课程 {course.cid} 无法找到可用教室 (类型: {course.fixedroomtype})")
    return None


def resolve_conflicts(timetable, resources, courses, rooms):
    """尝试解决冲突"""
    # 按优先级升序排序（先尝试调整低优先级课程）
    sorted_entries = sorted(timetable, key=lambda x: calculate_priority(next(
        c for c in courses if c.cid == x[0])))

    for i, entry in enumerate(sorted_entries):
        cid, rid, tid, week, day, slot = entry
        course = next(c for c in courses if c.cid == cid)

        # 检查是否有冲突
        if has_conflict(entry, resources):
            # 尝试找新时间
            new_pattern = find_alternative_pattern(course, resources)
            if new_pattern:
                # 替换原有安排
                update_timetable(timetable, resources, i, new_pattern)
                return True

    return False  # 无法解决

'''适应度函数'''
'''改进后的适应度函数（增加时间分布奖励）'''
def fitness(individual):
    """优化目标：只计算软约束得分（硬约束已由ConstraintSolver处理）"""
    score = 0
    course_time_distribution = defaultdict(list)
    room_utilization = defaultdict(int)

    # 数据收集阶段
    for cid, rid, _, week, day, slot in individual:
        course_time_distribution[cid].append((week, day, slot))
        room_utilization[rid] += 1

    # 1. 时间分布评分（周/天分散度）
    for cid, time_list in course_time_distribution.items():
        course = next((c for c in courses if c.cid == cid), None)
        if not course: continue

        # 周分散奖励
        unique_weeks = len({t[0] for t in time_list})
        score += unique_weeks * 5

        # 同天多课惩罚（非连排课程）
        if not hasattr(course, 'continuous') or course.continuous == 1:
            day_counts = defaultdict(int)
            for _, day, _ in time_list:
                day_counts[day] += 1
            for cnt in day_counts.values():
                if cnt > 1:
                    score -= 20 * (cnt - 1)

    # 2. 教室利用率评分（70%-90%最优）
    for cid, rid, _, _, _, _ in individual:
        course = next((c for c in courses if c.cid == cid), None)
        room = next((r for r in rooms if r.rid == rid), None)
        if course and room:
            utilization = course.popularity / room.rcapacity
            if 0.7 <= utilization <= 0.9:
                score += 30
            elif utilization > 0.9:
                score += 10
            else:
                score += max(0, 10 * utilization)

    # 3. 上午课奖励（1-4节）
    morning_slots = sum(1 for _, _, _, _, _, slot in individual if slot <= 4)
    score += morning_slots * 3

    # 4. 未排课惩罚（保留）
    scheduled_courses = {entry[0] for entry in individual}
    unscheduled_count = len([c for c in courses if c.cid not in scheduled_courses])
    score -= unscheduled_count * 1000

    return score


'''父辈选择，竞标赛'''
def selection(population: List[List[tuple]]) -> List[List[tuple]]:
    selected = []
    k = 5  # 增大锦标赛规模
    tournament_size = max(3, len(population)//10)  # 动态调整

    for _ in range(len(population)):
        # 确保选择不同的个体
        candidates = random.sample(population, min(tournament_size, len(population)))

        # 按适应度排序并加权选择
        candidates.sort(key=fitness, reverse=True)
        weights = [1/(i+1) for i in range(len(candidates))]  # 加权选择
        winner = random.choices(candidates, weights=weights, k=1)[0]

        selected.append(winner)
    return selected

'''基因重组'''
def crossover(parent1, parent2):
    """改进版交叉操作：按课程分组交叉，避免破坏连排课程"""
    # 1. 将父代按课程分组
    parent1_courses = defaultdict(list)
    parent2_courses = defaultdict(list)

    for entry in parent1:
        parent1_courses[entry[0]].append(entry)  # 按课程ID分组
    for entry in parent2:
        parent2_courses[entry[0]].append(entry)

    child = []

    # 2. 随机选择从哪个父代继承课程
    all_cids = list(set(parent1_courses.keys()).union(set(parent2_courses.keys())))
    random.shuffle(all_cids)  # 打乱顺序避免偏向某父代

    for cid in all_cids:
        # 随机选择继承父代1或父代2的该课程安排
        if random.random() < 0.5 and cid in parent1_courses:
            child.extend(parent1_courses[cid])
        elif cid in parent2_courses:
            child.extend(parent2_courses[cid])

    return child
'''基因变异'''
def mutate(individual):
    original_fitness = fitness(individual)
    """改进版变异函数，保留原有功能并确保满足硬约束"""
    constraint_solver = ConstraintSolver(courses, rooms)
    course_dict = {c.uid: c for c in courses}
    room_dict = {r.rid: r for r in rooms}

    # 最多尝试3次生成合法变异
    for _ in range(3):
        mutated = individual.copy()
        course_groups = defaultdict(list)

        # 按课程分组（保留原有分组逻辑）
        for i, entry in enumerate(mutated):
            if entry:
                course_groups[entry[0]].append((i, entry))

        # 随机选择要变异的课程（保留原有随机性）
        for cid, entries in course_groups.items():
            course = course_dict.get(cid)
            if not course or random.random() > 0.3:
                continue

            # === 连排课程处理（保留原有逻辑）===
            if hasattr(course, 'continuous') and course.continuous > 1:
                # 1. 删除原有连排段
                for i, _ in entries:
                    if i < len(mutated):
                        mutated[i] = None

                # 2. 生成新连排组（保持原有生成规则）
                valid_groups = [
                    group for group in generate_course_slots(course)
                    if len(group) == course.continuous
                       and all(ts.day == group[0].day for ts in group)
                       and group[0].slot in CONTINUOUS_SLOT_RULES.get(course.continuous, [])
                ]

                if not valid_groups:
                    continue

                new_group = random.choice(valid_groups)

                # 3. 教室选择（保留固定教室优先逻辑）
                if course.fixedroom:
                    room = next((r for r in rooms if r.rname == course.fixedroom), None)
                else:
                    original_room_id = next((e[1][1] for e in entries if e[1]), None)
                    room = room_dict.get(original_room_id) if original_room_id else None

                if not room:  # 备用选择
                    room = next((r for r in rooms if r.rtype == course.fixedroomtype), None)
                    if not room:
                        continue

                # 4. 插入新安排
                new_entries = [
                    (cid, room.rid, course.teacherid, ts.week, ts.day, ts.slot)
                    for ts in new_group
                ]

                # 找空位插入（保留原有位置优先策略）
                empty_indices = [i for i, x in enumerate(mutated) if x is None]
                for i, entry in zip(empty_indices[:len(new_entries)], new_entries):
                    mutated[i] = entry

            # === 非连排课程处理 ===
            else:
                for i, entry in entries:
                    # 保留原有教室选择策略
                    if course.fixedroom:
                        room = next((r for r in rooms if r.rname == course.fixedroom), None)
                    else:
                        room = room_dict.get(entry[1]) or \
                               next((r for r in rooms if r.rtype == course.fixedroomtype), None)

                    if not room:
                        continue

                    # 生成新时间（保留原有generate_course_slots逻辑）
                    for _ in range(3):  # 最多尝试3次
                        new_slot = random.choice(generate_course_slots(course)[0])
                        new_entry = (
                            cid, room.rid, course.teacherid,
                            new_slot.week, new_slot.day, new_slot.slot
                        )

                        # 临时替换并检查
                        original = mutated[i]
                        mutated[i] = new_entry
                        if constraint_solver.check_hard_constraints(mutated):
                            break
                        mutated[i] = original

        # 移除None并保持顺序
        mutated = [x for x in mutated if x is not None]
        new_fitness = fitness(mutated)
        if new_fitness > original_fitness:
            print(f"变异成功 Δ={new_fitness - original_fitness}")
        if constraint_solver.check_hard_constraints(mutated):
            return mutated

    # 如果无法生成合法变异，返回原个体（安全策略）
    return individual
'''遗传主算法'''
'''遗传主算法 - 添加可视化版本'''
def genetic_algorithm(iterations=100, population_size=50):
    """改进版遗传算法主函数，保留原有功能并整合ConstraintSolver"""
    print("🔄 开始初始化种群（强制满足硬约束）...")
    start_time = time.time()
    try:
        population = initialize_population_improved(population_size, courses, rooms)
    except RuntimeError as e:
        print(str(e))
        return []  # 返回空列表表示失败
    if not population:
        print("⚠️ 警告：初始种群为空，请检查输入约束条件")
        return []
    # 初始化种群
    population = initialize_population_improved(population_size, courses, rooms)
    constraint_solver = ConstraintSolver(courses, rooms)  # 约束检查器

    best_fitness_history = []

    for gen in range(iterations):
        print(f"\n=== 第 {gen+1}/{iterations} 代 ===")

        # 计算适应度并排序
        population.sort(key=fitness, reverse=True)
        best_fitness = fitness(population[0])
        best_fitness_history.append(best_fitness)

        print(f"🏆 第 {gen+1} 代 | 最佳适应度: {best_fitness} | 种群多样性: {len(set(fitness(ind) for ind in population))}")

        # **精英保留 + 变异**
        elite_size = max(1, int(population_size * 0.2))
        elites = population[:elite_size]

        # 让部分精英个体进行变异（30% 概率）
        mutated_elites = [mutate(e) if random.random() < 0.3 else e for e in elites]

        # **生成新种群**
        new_population = mutated_elites.copy()
        mating_pool = selection(population)

        while len(new_population) < population_size:
            p1, p2 = random.sample(mating_pool, 2)

            # 交叉 & 变异
            child = crossover(p1, p2)
            mutated_child = mutate(child)

            # 硬约束检查
            if constraint_solver.check_hard_constraints(mutated_child):
                if fitness(mutated_child) > fitness(population[-1]):
                    new_population.append(mutated_child)

        # **确保适应度高的个体存活**
        population = sorted(new_population, key=fitness, reverse=True)[:population_size]

        print(f"✅ 第 {gen+1} 代完成 | 最佳适应度: {fitness(population[0])} | 变化 Δ={fitness(population[0]) - best_fitness_history[-2] if gen > 0 else 0}")

        # **早停机制**
        if gen > 10 and len(set(best_fitness_history[-5:])) == 1:
            print("🚀 适应度连续5代未提升，提前终止")
            break

    print(f"\n🎉 算法完成！最终适应度: {fitness(population[0])}")
    return population[0] if population else []
    return population[0]  # 返回最佳个体



def print_schedule(timetable):
    print("\n📅 最终排课方案：")
    scheduled_courses = set()

    for i, (cid, rid, teacher, week, day, slot) in enumerate(timetable, 1):
        day_map = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五"}
        print(
            f"{i}. 课程 {cid} | "
            f"教室 {rid} | "
            f"教师 {teacher} | "
            f"时间：第{week}周 {day_map[day]} 第{slot}节"
        )
        scheduled_courses.add(cid)

    # 输出未被安排的课程
    unscheduled_courses = [c for c in courses if c.uid not in scheduled_courses]
    if unscheduled_courses:
        print("\n🚨 以下课程未被成功安排：")
        for c in unscheduled_courses:
            print(f"❌ 课程 {c.uid} (教师 {c.teacherid})")
def check_resources(courses, rooms):
    """检查资源是否充足"""
    # 教室类型需求统计
    room_demand = defaultdict(int)
    for c in courses:
        if c.fixedroomtype:
            # 计算课程总学时数（总节数），每个时间段的学时数 (lpw) 累加
            room_demand[c.fixedroomtype] += sum(lpw for _, _, lpw in c.time_slots)

    # 教师工作量统计
    teacher_load = defaultdict(int)
    for c in courses:
        teacher_load[c.teacherid] += sum(lpw for _, _, lpw in c.time_slots)

    # 检查结果
    problems = []

    # 教室检查
    room_types = {r.rtype for r in rooms}
    for req_type, demand in room_demand.items():
        # 获取该教室类型的数量
        available = sum(1 for r in rooms if r.rtype == req_type)

        # 计算每间教室在学期内的有效时间段数
        effective_slots_per_day = SLOTS_PER_DAY * 0.7  # 假设教室的70%利用率
        effective_slots_per_semester_per_room = effective_slots_per_day * DAYS_PER_WEEK * WEEKS_IN_SEMESTER

        # 计算所有教室的总有效时间段数
        total_effective_slots = available * effective_slots_per_semester_per_room

        # 比较需求与资源
        if demand > total_effective_slots:  # 如果需求超过可用教室总时间段数
            problems.append(f"教室类型 {req_type} 不足: 需要{demand}节，仅有{available}间教室，每间教室最多提供{effective_slots_per_semester_per_room}节，合计{total_effective_slots}节教室时间")

    # 教师检查
    for teacher, load in teacher_load.items():
        # 教师工作量检查：假设每个教师最多可以承担50%的教学时间
        max_load = WEEKS_IN_SEMESTER * DAYS_PER_WEEK * 0.7
        if load > max_load:
            problems.append(f"教师 {teacher} 超额: 需要{load}节，最多可承担{max_load}节")

    if problems:
        print("资源不足警告:")
        for p in problems:
            print("⚠️ " + p)
        return False
    return True


# 在main函数中添加
if __name__ == "__main__":
    if not check_resources(courses, rooms):
        print("无法继续执行，请先解决资源不足问题")
    else:
        timetable = genetic_algorithm(iterations=50, population_size=30)
        print_schedule(timetable)

        # 数据格式转换
        schedule_list = [Schedule(scid, teacher, rid, f"{week}-{day}-{slot}")
                         for scid, teacher, rid, week, day, slot in timetable]
        schedule_json = json.dumps([s.to_dict() for s in schedule_list], ensure_ascii=False, indent=4)

        # 核查
        validation_report = test.validate_schedule(timetable, courses)
        if validation_report:
            print("\n发现以下冲突：")
            for line in validation_report:
                print(f"⚠️ {line}")
        else:
            print("\n✅ 排课方案无冲突")