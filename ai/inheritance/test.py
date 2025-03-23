
from typing import List


def time_slot_to_str(time_slot: int) -> str:
    """将时间片转换为可读的日期和时间"""
    day = (time_slot - 1) // 8 + 1
    period = (time_slot - 1) % 8 + 1
    return f"星期{['一','二','三','四','五'][day-1]} 第{period}节课"

from typing import List

def time_slot_to_str(time_slot: int) -> str:
    """将时间片转换为可读的日期和时间"""
    day = (time_slot - 1) // 8 + 1
    period = (time_slot - 1) % 8 + 1
    return f"星期{['一','二','三','四','五'][day-1]} 第{period}节课"

def validate_schedule(schedule: List[tuple], courses: List[str]) -> List[str]:
    """验证排课方案并返回冲突报告"""
    teacher_conflicts = {}
    room_conflicts = {}
    report = []
    assigned_courses = set()  # 用于存储已排课的课程 ID

    # 检查教师和教室时间冲突
    for entry in schedule:
        cid, rid, teacher_id, ts = entry  # 元组顺序修正
        assigned_courses.add(cid)  # 记录已安排的课程

        # 教师冲突检测
        teacher_key = (teacher_id, ts)
        if teacher_key in teacher_conflicts:
            teacher_conflicts[teacher_key].append(cid)
        else:
            teacher_conflicts[teacher_key] = [cid]

        # 教室冲突检测
        room_key = (rid, ts)
        if room_key in room_conflicts:
            room_conflicts[room_key].append(cid)
        else:
            room_conflicts[room_key] = [cid]

    # 生成冲突报告
    for key, courses in teacher_conflicts.items():
        if len(courses) > 1:
            time_str = time_slot_to_str(key[1])
            report.append(
                f"冲突：教师 {key[0]} 在 {time_str} 同时教授课程 {', '.join(courses)}"
            )

    for key, courses in room_conflicts.items():
        if len(courses) > 1:
            time_str = time_slot_to_str(key[1])
            report.append(
                f"冲突：教室 {key[0]} 在 {time_str} 同时安排课程 {', '.join(courses)}"
            )

    # 检查无效时间片
    for entry in schedule:
        cid, _, _, ts = entry
        if ts < 1 or ts > 40:
            report.append(f"错误：课程 {cid} 的时间片 {ts} 无效（有效范围：1-40）")

    # 检查未安排的课程
    missing_courses = set(courses) - assigned_courses
    if missing_courses:
        report.append(f"未安排课程：{', '.join(missing_courses)}")

    return report
