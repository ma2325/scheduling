#地点：
#教室
class Room:
    def __init__(self,rid,rtype,rcapacity):
        self.rid = rid
        self.rtype = rtype
        self.rcapacity = rcapacity

#人物：

#老师
class Teacher:
    def __init__(self, tcode,tdepartment):
        self.tcode = tcode
        self.tdepartment = tdepartment

#课：
#课程
class Course:
    def __init__(self, coid, cotype2,codepartment):
        self.coid = coid
        self.cotype2 = cotype2
        self.codepartment = codepartment

#结果：
#课程表
class Schedule:
    def __init__(self, scid,  scroom, tabegin_week, taend_week, tabegin_time, taend_time):
        self.scid = scid
        self.scroom = scroom
        self.tabegin_week = tabegin_week
        self.taend_week = taend_week
        self.tabegin_time = tabegin_time
        self.taend_time = taend_time