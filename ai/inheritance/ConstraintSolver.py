from collections import defaultdict

class ConstraintSolver:

    def __init__(self, courses, rooms):
        """
        改进版约束检查器，完全兼容Timetable.py的三维时间模型
        :param courses: 课程列表（与Timetable.py相同结构）
        :param rooms: 教室列表
        """
        self.courses = courses
        self.rooms = rooms
        self.course_dict = {c.uid: c for c in courses}  # 使用 uid 作为键
        self.room_dict = {r.rid: r for r in rooms}

        # 连排规则（与Timetable.py一致）
        self.CONTINUOUS_SLOT_RULES = {
            2: [1, 3, 5, 7],  # 两节连排允许的开始节次
            4: [1, 3, 5],      # 四节连排允许的开始节次
        }

    def check_hard_constraints(self, individual):
        """
        检查所有硬约束（三维时间模型）
        :param individual: 排课方案 [(uid, rid, tid, week, day, slot), ...]
        :return: True/False
        """
        error_score = 0

        error_score += self._check_teacher_conflicts(individual) * 100
        error_score += self._check_room_conflicts(individual) * 50
        error_score += self._check_room_type_and_fixed(individual) * 10
        # ...其他约束...

        return error_score < 30

    def _check_teacher_conflicts(self, individual):
        """增强健壮性的检查"""
        if not individual or any(entry is None for entry in individual):
            return False

        teacher_schedule = defaultdict(set)
        try:
            for uid, _, tid, week, day, slot in individual:
                course = self.course_dict.get(uid)  # 使用 uid 查找课程
                if not course:
                    print(f"⚠️ 数据错误: 课程{uid}不存在")
                    continue

                time_key = (week, day, slot)
                if time_key in teacher_schedule[tid]:
                    return False
                teacher_schedule[tid].add(time_key)
            return True
        except (TypeError, ValueError):
            return False

    def _check_room_conflicts(self, individual):
        """检查教室在同一时间是否被占用"""
        room_schedule = defaultdict(set)
        for uid, rid, _, week, day, slot in individual:
            course = self.course_dict.get(uid)  # 使用 uid 查找课程
            if not course:
                print(f"⚠️ 数据错误: 课程{uid}不存在")
                continue

            room = self.room_dict.get(rid)
            if not room:
                print(f"⚠️ 数据错误: 教室{rid}不存在")
                return False

            time_key = (week, day, slot)
            if time_key in room_schedule[rid]:
                return False
            room_schedule[rid].add(time_key)
        return True

    def _check_room_type_and_fixed(self, individual):
        print("\n=== 开始教室分配检查 ===")
        error_log = []

        for uid, rid, _, _, _, _ in individual:
            course = self.course_dict.get(uid)
            room = self.room_dict.get(rid)

            if not course:
                error_log.append(f"课程 {uid} 不存在")
                continue
            if not room:
                error_log.append(f"教室 {rid} 不存在")
                continue

            print(f"\n检查课程 {uid} -> 教室 {rid}({room.rtype})")

            # 固定教室检查
            if hasattr(course, 'fixedroom') and course.fixedroom:
                print(f"固定教室要求: {course.fixedroom}")
                if room.rname != course.fixedroom:
                    error_log.append(f"课程 {uid} 需要固定教室 {course.fixedroom} 但分配到 {room.rname}")
                else:
                    print("✅ 固定教室匹配")

            # 教室类型检查
            elif hasattr(course, 'fixedroomtype'):
                print(f"教室类型要求: {course.fixedroomtype}")
                if room.rtype != course.fixedroomtype:
                    error_log.append(f"课程 {uid} 需要 {course.fixedroomtype} 但分配到 {room.rtype}")
                else:
                    print("✅ 教室类型匹配")

        if error_log:
            print("\n=== 检查发现错误 ===")
            for error in error_log[:5]:  # 只显示前5个错误避免刷屏
                print(error)
            return False

        print("✅ 所有教室分配检查通过")
        return True

    def _check_continuous_courses(self, individual):
        """检查连排课程规则（节次连续性和开始节次）"""
        # 按课程分组
        course_entries = defaultdict(list)
        for entry in individual:
            course_entries[entry[0]].append(entry)

        for uid, entries in course_entries.items():
            course = self.course_dict.get(uid)  # 使用 uid 查找课程
            if not course:
                print(f"⚠️ 数据错误: 课程{uid}不存在")
                continue

            if not hasattr(course, 'continuous') or course.continuous == 1:
                continue  # 非连排课程跳过

            # 按周和天分组
            week_day_groups = defaultdict(list)
            for entry in entries:
                week, day = entry[3], entry[4]
                week_day_groups[(week, day)].append(entry)

            # 检查每组连排课程
            for (week, day), group in week_day_groups.items():
                if len(group) != course.continuous:
                    return False  # 连排节数不符

                # 检查节次连续性
                slots = sorted([entry[5] for entry in group])
                if any(slots[i+1] != slots[i] + 1 for i in range(len(slots)-1)):
                    return False

                # 检查开始节次是否符合规则
                start_slot = slots[0]
                allowed_starts = self.CONTINUOUS_SLOT_RULES.get(course.continuous, [])
                if allowed_starts and start_slot not in allowed_starts:
                    return False

                # 检查同一连排是否使用相同教室
                if len(set(entry[1] for entry in group)) > 1:
                    return False
        return True

    def _check_room_capacity(self, individual):
        """检查教室容量是否满足课程人数"""
        for uid, rid, _, _, _, _ in individual:
            course = self.course_dict.get(uid)  # 使用 uid 查找课程
            if not course:
                print(f"⚠️ 数据错误: 课程{uid}不存在")
                continue

            room = self.room_dict.get(rid)
            if not room:
                print(f"⚠️ 数据错误: 教室{rid}不存在")
                return False

            if course.popularity > room.rcapacity:
                print(f"⚠️ 教室容量不足: 课程{uid}需要容纳{course.popularity}人，但教室{room.rname}只能容纳{room.rcapacity}人")
                return False
        return True