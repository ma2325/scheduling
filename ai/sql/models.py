import json
#教室
'''教室编号，类型，容纳人数，校区，教学楼'''
class Room:
    def __init__(self,rid,rtype,rcapacity,rcampus,rbuilding):
        self.rid = rid
        self.rtype = rtype
        self.rcapacity = rcapacity
        self.rcampus = rcampus
        self.rbuilding = rbuilding


#课程
'''课程号，教学班名，课程人数，老师（工号表示），时间，周节次，连排节次，指定教室类型，指定教室，指定时间，指定教学楼,开课校区,是否为合班，'''
class Course:
    def __init__(self, cid,formclass,popularity,teacherid,task,continuous,fixedroomtype,fixesroom,fixedtime,fixedbuilding,capmpus,combine=False):
        self.cid = cid
        self.formclass = formclass
        self.popularity = popularity
        self.teacherid = teacherid
        self.task = task
        self.continuous = continuous
        self.fixedroomtype = fixedroomtype
        self.fixedroom = fixesroom
        self.fixedtime = fixedtime
        self.fixedbuilding = fixedbuilding
        self.capmpus = capmpus

        if self.formclass is None:
            self.combine = True
        else:
            if "，" in self.formclass or "," in self.formclass:
                self.combine = True

        #行政班
'''班名，固定教室'''
class myclass:
    def __init__(self,clname,clfixedroom):
        self.clname = clname
        self.clfixedroom = clfixedroom

#结果：
#课程表
'''课程号，教学班名，教室，时间'''
class Schedule:
    def __init__(self, scid,teacher,rid,time):
        self.scid = scid
        self.teacher = teacher
        self.rid = rid
        self.time = time
    def to_dict(self):
        return{
            "scid":self.scid,
            "teacher":self.teacher,
            "rid":self.rid,
            "time":self.time
        }
