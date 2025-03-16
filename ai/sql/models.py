#地点：
#教学楼
class Building:
    def __init__(self,bid,bname):
        self.bid = bid
        self.bname = bname

#教室
class Room:
    def __init__(self,rid,rname,rbuilding,rtype,rvolume):
        self.rid = rid
        self.rname = rname
        self.rbuilding = rbuilding
        self.rtype = rtype
        self.rvolume = rvolume

#楼间距
class Distance:
    def __init__(self, diid, dibuilding1, dibuilding2, didistance):
        self.diid = diid
        self.dibuilding1 = dibuilding1
        self.dibuilding2 = dibuilding2
        self.didistance = didistance

#学院
class College:
    def __init__(self, cid, cname, cbuilding):
        self.cid = cid
        self.cname = cname
        self.cbuilding = cbuilding

#系
class Department:
    def __init__(self, did, dcollege, dname):
        self.did = did
        self.dcollege = dcollege
        self.dname = dname

#人物：
#学生
class Student:
    def __init__(self, sid, scollege):
        self.sid = sid
        self.scollege = scollege

#老师
class Teacher:
    def __init__(self, tid, tname, tcollege):
        self.tid = tid
        self.tname = tname
        self.tcollege = tcollege

#课：
#课程
class Course:
    def __init__(self, coid, coname, cohour, cotype, covolume):
        self.coid = coid
        self.coname = coname
        self.cohour = cohour
        self.cotype = cotype
        self.covolume = covolume

#教学任务
class Task:
    def __init__(self, taid, tacourse):
        self.taid = taid
        self.tacourse = tacourse

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