import json
#教室
'''教室编号，类型，容纳人数，校区，教学楼'''
class Room:
    def __init__(self,rid,rname,rtype,rcapacity,rcampus,rbuilding):
        self.rid = rid
        self.rname = rname
        self.rtype = rtype
        self.rcapacity = rcapacity
        self.rcampus = rcampus
        self.rbuilding = rbuilding


#课程
'''课程号，教学班名，课程人数，老师（工号表示），时间，周节次，连排节次，指定教室类型，指定教室，指定时间，指定教学楼,开课校区,是否为合班，'''
class Course:
    def __init__(self, cid,formclass,popularity,total_hours,taproperty,teacherid,task,continuous,fixedroomtype,fixedroom,fixedtime,fixedbuilding,capmpus,combine=False):
        self.uid = f"{cid}-{teacherid}-{task}-{fixedroom}"
        self.cid = cid
        self.formclass = formclass
        self.popularity = popularity
        self.total_hours = total_hours
        self.taproperty = taproperty
        self.teacherid = teacherid
        self.task = task
        self.continuous = continuous
        self.fixedroomtype = fixedroomtype
        self.fixedroom = fixedroom
        self.fixedtime = fixedtime
        self.fixedbuilding = fixedbuilding
        self.capmpus = capmpus

        self.time_slots=Course.parse_task(task) if task else[]
        #是否合班？
        if self.formclass is None:
            self.combine = True
        else:
            if "，" in self.formclass or "," in self.formclass:
                self.combine = True

    #字段拆分
    def parse_task(task: str):
        """解析 task 字符串，支持多个时间范围，如 '1-4:2,9-12:2' -> [(1,4,2), (9,12,2)]"""
        if not isinstance(task, str):
            raise ValueError(f"⚠️ task 不是字符串: {task}")

        time_slots = []
        parts = task.split(",")  # 按逗号拆分多个时间段

        for part in parts:
            try:
                week_range, lessons_per_week = part.split(":")
                start_week, end_week = map(int, week_range.split("-"))
                time_slots.append((start_week, end_week, int(lessons_per_week)))
            except Exception as e:
                raise ValueError(f"⚠️ 解析 task 失败: {task}, 出错部分: {part}, 错误: {e}")


        return time_slots  # 返回多个时间段

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
