import json
#教室
from sqlalchemy import Column, String, Integer, Float, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()
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
    def __init__(self, cid,formclass,formclassid,popularity,total_hours,taproperty,teacherid,teachername,task,continuous,fixedroomtype,fixedroom,fixedtime,fixedbuilding,capmpus,combine=False):
        self.uid = f"{cid}-{teacherid}-{task}-{fixedroom}"
        self.teacher_uid = f"{teacherid}-{teachername}"
        self.cid = cid
        self.formclass = formclass
        self.formclassid = formclassid
        self.popularity = popularity
        self.total_hours = total_hours
        self.taproperty = taproperty
        self.teacherid = teacherid
        self.teachername = teachername
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
class Schedule(Base):
    __tablename__ = 'schedule'

    scid = Column(String, primary_key=True)
    sctask=Column(String)
    scteacherid = Column(String)
    scroom = Column(String)
    scbegin_week = Column(Integer)
    scend_week = Column(Integer)
    scday_of_week = Column(Integer)
    scbegin_time = Column(Float)    # 新增字段：开始时间
    scend_time = Column(Float)   # 新增字段：结束时间
    scteachername = Column(String)
    scslots=Column(String)

    def __init__(
            self,
            scid: str,
            sctask:str,
            scteacherid: str,
            scroom: str,
            scbegin_week: int,
            scend_week: int,
            scday_of_week: int,
            scbegin_time: float,
            scend_time: float,
            scteachername: str,
            scslots: str
    ):
        """
        :param scid: 唯一标识
        :param course_uid: 课程唯一ID
        :param scteacher: 教师ID
        :param rid: 教室ID
        :param start_week: 开始周（1-20）
        :param end_week: 结束周（>= start_week）
        :param day: 上课日（1-5，周一至周五）
        :param slots: 节次列表（如 [1, 2] 表示1-2节连排）
        :param start_time: 上课开始时间（如 8.0 表示 8:00）
        :param end_time: 上课结束时间（如 9.5 表示 9:30）
        """
        self.scid = scid
        #self.course_uid = course_uid
        self.sctask = sctask
        self.scteacherid = scteacherid
        self.scroom = scroom
        self.scbegin_week = scbegin_week
        self.scend_week = scend_week
        self.scday_of_week = scday_of_week
        self.scbegin_time = scbegin_time
        self.scend_time = scend_time
        self.scteachername= scteachername
        self.scslots=scslots


    def to_dict(self):
        return {
            "scid": self.scid,
            #"course_uid": self.course_uid,
            'scroom': self.scroom,
            "sctask": self.sctask,
            "teacherid": self.scteacherid,
            "start_week": self.scbegin_week,
            "end_week": self.scend_week,
            "day": self.scday_of_week,
            "start_time": self.scbegin_time,
            "end_time": self.scend_time,
            "scteachername": self.scteachername,
            "slots": self.scslots,
        }

