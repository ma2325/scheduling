from typing import List
from collections import defaultdict
#可删

def validate_schedule(schedule: List[tuple], courses: List[dict]) -> List[str]:
    """
    验证排课方案并返回冲突报告（适配三维时间模型）
    
    参数:
        schedule: 排课方案列表，每个元素为 (cid, rid, teacher_id, week, day, slot)
        courses: 所有课程对象列表（用于检查未安排课程）
    
    返回:
        冲突报告列表
    """
    # 转换课程列表为ID集合
    course_ids = {c.cid for c in courses} if hasattr(courses[0], 'cid') else set(courses)

    teacher_conflicts = defaultdict(list)  # {(teacher_id, week, day, slot): [cid1, cid2]}
    room_conflicts = defaultdict(list)     # {(rid, week, day, slot): [cid1, cid2]}
    report = []
    assigned_courses = set()  # 已排课的课程ID

    # 检查教师和教室时间冲突
    for entry in schedule:
        if len(entry) == 6:  # 新格式 (cid, rid, teacher_id, week, day, slot)
            cid, rid, teacher_id, week, day, slot = entry
        else:  # 兼容旧格式
            cid, rid, teacher_id, ts = entry
            week = (ts - 1) // (5 * 8) + 1  # 转换为三维时间（如果需要）
            day = ((ts - 1) // 8) % 5 + 1
            slot = (ts - 1) % 8 + 1

        assigned_courses.add(cid)

        # 教师冲突检测
        teacher_key = (teacher_id, week, day, slot)
        teacher_conflicts[teacher_key].append(cid)

        # 教室冲突检测
        room_key = (rid, week, day, slot)
        room_conflicts[room_key].append(cid)

    # 生成冲突报告
    for (teacher_id, week, day, slot), cids in teacher_conflicts.items():
        if len(cids) > 1:
            report.append(
                f"⛔ 教师冲突：教师 {teacher_id} 在第{week}周 星期{day} 第{slot}节 "
                f"同时教授课程 {', '.join(cids)}"
            )

    for (rid, week, day, slot), cids in room_conflicts.items():
        if len(cids) > 1:
            report.append(
                f"⛔ 教室冲突：教室 {rid} 在第{week}周 星期{day} 第{slot}节 "
                f"同时安排课程 {', '.join(cids)}"
            )

    # 检查时间有效性
    for entry in schedule:
        if len(entry) == 6:
            _, _, _, week, day, slot = entry
            if not (1 <= week <= 20):
                report.append(f"⚠️ 无效周次：{week}（应在1-20周内）")
            if not (1 <= day <= 5):
                report.append(f"⚠️ 无效星期：{day}（应为1-5，对应周一到周五）")
            if not (1 <= slot <= 8):
                report.append(f"⚠️ 无效节次：{slot}（应为1-8节）")

    # 检查未安排的课程
    missing_courses = course_ids - assigned_courses
    if missing_courses:
        report.append(f"❌ 未安排课程：{', '.join(map(str, missing_courses))}")

    return report

# 辅助函数（兼容旧时间片格式）
def time_slot_to_3d(ts: int) -> tuple:
    """将旧时间片(1-40)转换为三维时间(week,day,slot)"""
    week = (ts - 1) // (5 * 8) + 1
    day = ((ts - 1) // 8) % 5 + 1
    slot = (ts - 1) % 8 + 1
    return (week, day, slot)

def format_time(week: int, day: int, slot: int) -> str:
    """格式化三维时间为可读字符串"""
    day_names = ["一", "二", "三", "四", "五"]
    return f"第{week}周 星期{day_names[day-1]} 第{slot}节课"