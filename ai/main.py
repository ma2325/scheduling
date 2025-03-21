import sql.connect
import sql.models
import inheritance.Timetable

#连接数据库
conn=sql.connect.connect()
cursor=conn.cursor()

#载入课程
def load_course():
    cursor.execute("SELECT coid,cotype2,codepartment FROM course")
    courses=[]#列表储存
    for row in cursor.fetchall():
        course=sql.models.Course(
            coid=row['coid'],
            cotype2=row['cotype2'],
            codepartment=row['codepartment']
        )
        courses.append(course)
    return courses

#载入教室
def load_room():
    cursor.execute("SELECT rid,rtype,rcapacity FROM room")
    rooms=[]
    for row in cursor.fetchall():
        room=sql.models.Room(
            rid=row['rid'],
            rtype=row['rtype'],
            rcapacity=row['rcapacity']
        )
        rooms.append(room)
    return rooms

#载入老师
def load_teacher():
    cursor.execute("SELECT tcode,tdepartment FROM teacher")
    teachers=[]
    for row in cursor.fetchall():
        teacher=sql.models.Teacher(
            tcode=row['tcode'],
            tdepartment=row['tdepartment']
        )
        teachers.append(teacher)
    return teachers


if __name__ == "__main__":
    try:
        courses=load_course()
        print("courses:")
        '''
        for course in courses:
            print(f"ID: {course.coid}, Type: {course.cotype2}")
        '''
        print("courses OK\n")

        rooms=load_room()
        print("rooms: ")
        '''
        for room in rooms:
            print(f"ID: {room.rid}, Volume:{room.rvolume}, Type: {room.rtype}")
        '''
        print("rooms OK\n")

        teachers=load_teacher()
        '''
        print("teachers: ")
        for teacher in teachers:
            print(f"ID:{teacher.tcode}")
        '''
        print("teachers OK\n")
    finally:
        #关闭
        cursor.close()
        print("exit to mysql")
        conn.close()

    print("OK")
    '''
    shedule= inheritance.Timetable.result(courses, rooms, teachers)
    for eachclass in shedule:
        print(eachclass)
    '''