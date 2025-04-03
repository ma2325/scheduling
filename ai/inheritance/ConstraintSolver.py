class ConstraintSolver:
    def __init__(self, schedule, rooms, courses):
        """
        初始化约束求解器。
        :param schedule: 当前课表，格式为 {course_id: (time_slot, room_id, teacher_id, duration)}
        :param rooms: 教室列表，包含教室容量和类型信息。
        :param courses: 课程列表，包含课程的开课要求，如固定教室或教室类型。
        """
        self.schedule = schedule
        self.rooms = rooms
        self.courses = courses

    def check_teacher_conflicts(self):
        """检查教师是否存在时间冲突"""
        teacher_schedules = {}
        for course in self.courses:
            teacher_id = course['teacher_id']
            time_slot, _, _, duration = self.schedule[course['id']]
            if teacher_id not in teacher_schedules:
                teacher_schedules[teacher_id] = set()
            for t in range(time_slot, time_slot + duration):
                if t in teacher_schedules[teacher_id]:
                    return False  # 存在时间冲突
                teacher_schedules[teacher_id].add(t)
        return True

    def check_room_availability(self):
        """检查教室是否存在冲突"""
        room_schedules = {}
        for course in self.courses:
            time_slot, room_id, _, duration = self.schedule[course['id']]
            if room_id not in room_schedules:
                room_schedules[room_id] = set()
            for t in range(time_slot, time_slot + duration):
                if t in room_schedules[room_id]:
                    return False  # 教室冲突
                room_schedules[room_id].add(t)
        return True

    def check_room_capacity(self):
        """检查教室容量是否满足课程需求"""
        for course in self.courses:
            room_id = self.schedule[course['id']][1]
            if self.rooms[room_id]['capacity'] < course['required_capacity']:
                return False  # 教室容量不足
        return True

    def check_course_time_requirements(self):
        """检查课程的开课课时是否满足要求"""
        for course in self.courses:
            scheduled_duration = self.schedule[course['id']][3]
            if scheduled_duration < course['min_duration']:
                return False  # 课时不足
        return True

    def check_room_type_requirements(self):
        """检查课程是否安排在符合要求的教室类型"""
        for course in self.courses:
            room_id = self.schedule[course['id']][1]
            required_type = course.get('required_room_type')
            if required_type and self.rooms[room_id]['type'] != required_type:
                return False  # 教室类型不匹配
        return True

    def is_valid_schedule(self):
        """检查当前课表是否满足所有硬性约束"""
        return (self.check_teacher_conflicts() and
                self.check_room_availability() and
                self.check_room_capacity() and
                self.check_course_time_requirements() and
                self.check_room_type_requirements())
