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
        self.course_dict = {c.cid: c for c in courses}
        self.room_dict = {r.rid: r for r in rooms}

        # 连排规则（与Timetable.py一致）
        self.CONTINUOUS_SLOT_RULES = {
            2: [1, 3, 5, 7],  # 两节连排允许的开始节次
            4: [1, 3, 5],      # 四节连排允许的开始节次
        }

    def check_hard_constraints(self, individual):
        """
        检查所有硬约束（三维时间模型）
        :param individual: 排课方案 [(cid, rid, tid, week, day, slot), ...]
        :return: True/False
        """
        return (
                self._check_teacher_conflicts(individual) and
                self._check_room_conflicts(individual) and
                self._check_room_type_and_fixed(individual) and
                self._check_continuous_courses(individual) and
                self._check_room_capacity(individual)
        )

    def _check_teacher_conflicts(self, individual):
        """增强健壮性的检查"""
        if not individual or any(entry is None for entry in individual):
            return False

        teacher_schedule = defaultdict(set)
        try:
            for cid, _, tid, week, day, slot in individual:
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
        for _, rid, _, week, day, slot in individual:
            time_key = (week, day, slot)
            if time_key in room_schedule[rid]:
                return False
            room_schedule[rid].add(time_key)
        return True

    def _check_room_type_and_fixed(self, individual):
        """改进版教室类型和固定教室检查"""
        # 先收集所有需要固定教室的课程
        fixed_course_rooms = {
            c.cid: c.fixedroom
            for c in self.courses
            if getattr(c, 'fixedroom', None)
        }

        # 检查每个课程的教室分配
        for cid, rid, _, _, _, _ in individual:
            course = self.course_dict.get(cid)
            room = self.room_dict.get(rid)

            # 基础检查
            if not course or not room:
                print(f"⚠️ 数据错误: 课程{cid}或教室{rid}不存在")
                return False

            # 检查教室类型
            if room.rtype != course.fixedroomtype:
                print(f"⚠️ 教室类型不匹配: 课程{cid}需要{course.fixedroomtype}但教室{rid}是{room.rtype}")
                return False

            # 检查固定教室要求（仅当课程有固定教室要求时）
            if cid in fixed_course_rooms:
                if room.rname != fixed_course_rooms[cid]:
                    print(f"⚠️ 固定教室不匹配: 课程{cid}需要{fixed_course_rooms[cid]}但分配到{room.rname}")
                    return False

        return True

    def _check_continuous_courses(self, individual):
        """检查连排课程规则（节次连续性和开始节次）"""
        # 按课程分组
        course_entries = defaultdict(list)
        for entry in individual:
            course_entries[entry[0]].append(entry)

        for cid, entries in course_entries.items():
            course = self.course_dict.get(cid)
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
        for cid, rid, _, _, _, _ in individual:
            course = self.course_dict.get(cid)
            room = self.room_dict.get(rid)
            if course and room and course.popularity > room.rcapacity:
                return False
        return True