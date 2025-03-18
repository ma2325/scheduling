import sql.connect
import sql.models

#连接数据库
conn=sql.connect.connect()
cursor=conn.cursor()

#载入课程
def load_course():
    cursor.execute("SELECT coid,cotype,covolume FROM course")
    courses=[]#列表储存
    for row in cursor.fetchall():
        course=sql.models.Course(
            coid=row['coid'],
            cotype=row['cotype'],
            covolume=row['covolume']
        )
        courses.append(course)
    return courses

#载入教室
def load_room():
    cursor.execute("SELECT rid,rvolume FROM room")
    rooms=[]
    for row in cursor.fetchall():
        room=sql.models.Room(
            rid=row['rid'],
            rvolume=row['rvolume']
        )
        rooms.append(room)
    return rooms

#载入老师
def load_teacher():
    cursor.execute("SELECT tid FROM teacher")
    teachers=[]
    for row in cursor.fetchall():
        teacher=sql.models.Teacher(
            tid=row['tid']
        )
        teachers.append(teacher)
    return teachers


if __name__ == "__main__":
    try:
        courses=load_course()
        print("courses:")
        for course in courses:
            print(f"ID: {course.coid}, Type: {course.cotype}, Volume: {course.covolume}")
        print("courses OK\n")

        rooms=load_room()
        print("rooms: ")
        for room in rooms:
            print(f"ID: {room.rid}, Volume:{room.rvolume}")
        print("rooms OK\n")

        teachers=load_teacher()
        print("teachers: ")
        for teacher in teachers:
            print(f"ID:{teacher.tid}")
        print("teachers OK\n")
    finally:
        cursor.close()
        print("exit to mysql")
        conn.close()
    #关闭
