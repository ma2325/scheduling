#地点：
#教室
class Room:
    def __init__(self,rid,rvolume):
        self.rid = rid
        self.rvolume = rvolume


#学院
class College:
    def __init__(self, cid):
        self.cid = cid

#系
class Department:
    def __init__(self, did, dcollege):
        self.did = did
        self.dcollege = dcollege

#人物：

#老师
class Teacher:
    def __init__(self, tid):
        self.tid = tid

#课：
#课程
class Course:
    def __init__(self, coid, cotype, covolume):
        self.coid = coid
        self.cotype = cotype
        self.covolume = covolume


#结果：
#课程表
class Schedule:
    def __init__(self, scid, sctask, scroom, tabegin_week, taend_week, tabegin_time, taend_time):
        self.scid = scid
        self.sctask = sctask
        self.scroom = scroom
        self.tabegin_week = tabegin_week
        self.taend_week = taend_week
        self.tabegin_time = tabegin_time
        self.taend_time = taend_time