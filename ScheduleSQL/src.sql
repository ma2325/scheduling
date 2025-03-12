CREATE DATABASE schedule;

USE schedule;

--楼号表
CREATE TABLE building(
    bid INTEGER AUTO_INCREMENT PRIMARY KEY,
    bname VARCHAR(20)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 教室表
CREATE TABLE room(
    rid INTEGER AUTO_INCREMENT PRIMARY KEY,
    rname VARCHAR(20),
    rbuilding INTEGER NOT NULL,
    rtype ENUM('common','multimedia','sport','special') NOT NULL,
    rvolume INTEGER NOT NULL DEFAULT 50 COMMENT ,
    FOREIGN KEY (rbuilding) REFERENCES building(bid)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

DELIMITER $$

CREATE TRIGGER before_room_insert
BEFORE INSERT ON room
FOR EACH ROW
BEGIN
    IF NEW.rvolume <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Room volume must better than 0';
    END IF;
END $$

CREATE TRIGGER before_room_update
BEFORE UPDATE ON room
FOR EACH ROW
BEGIN
    IF NEW.rvolume <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Room volume must better than 0';
    END IF;
END $$

DELIMITER ;

-- 学院表
CREATE TABLE college(
    cid INTEGER AUTO_INCREMENT PRIMARY KEY,
    cname VARCHAR(20),
    cbuilding INTEGER NOT NULL,
    FOREIGN KEY (cbuilding) REFERENCES building(bid)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 系表
CREATE TABLE department(
    did INTEGER AUTO_INCREMENT PRIMARY KEY,
    dcollege INTEGER NOT NULL,
    dname VARCHAR(20),
    FOREIGN KEY (dcollege) REFERENCES college(cid)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 学生表
CREATE TABLE student(
    sid INTEGER PRIMARY KEY,
    scollege INTEGER NOT NULL,
    FOREIGN KEY (scollege) REFERENCES college(cid)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 教师表
CREATE TABLE teacher(
    tid INTEGER PRIMARY KEY,
    tname VARCHAR(20),
    tcollege INTEGER NOT NULL,
    FOREIGN KEY (tcollege) REFERENCES college(cid)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 课程表
CREATE TABLE course(
    coid INTEGER PRIMARY KEY,
    coname VARCHAR(20),
    cohour INTEGER NOT NULL,
    cotype ENUM('publicBase','majorBase','majorCore','majorElective','publicElective') NOT NULL DEFAULT 'publicElective',
    covolume INTEGER NOT NULL DEFAULT 30,
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

DELIMITER $$

CREATE TRIGGER before_course_insert
BEFORE INSERT ON course
FOR EACH ROW
BEGIN
    IF NEW.cohour <= 0 OR NEW.covolume <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Learn hours must better than 0';
    END IF;
END $$

CREATE TRIGGER before_course_update
BEFORE UPDATE ON course
FOR EACH ROW
BEGIN
    IF NEW.cohour <= 0 OR NEW.covolume <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Learn hours must better than 0';
    END IF;
END $$

DELIMITER ;

-- 教学任务表
CREATE TABLE task(
    taid INTEGER AUTO_INCREMENT PRIMARY KEY,
    tacourse INTEGER  NOT NULL,
    FOREIGN KEY (tacourse) REFERENCES course(coid)
);
-- 楼间距表
CREATE TABLE distance(
    diid INTEGER AUTO_INCREMENT PRIMARY KEY,
    dibuilding1 INTEGER NOT NULL,
    dibuilding2 INTEGER NOT NULL,
    didistance INTEGER CHECK (didistance > 0) NOT NULL,
    FOREIGN KEY (dibuilding1) REFERENCES building(bid),
    FOREIGN KEY (dibuilding2) REFERENCES building(bid),
    UNIQUE (dibuilding1, dibuilding2)
);

-- 由于企业版本MySQL可能不支持CHECK语句，因此添加对应的触发器代码
DELIMITER $$

CREATE TRIGGER before_distance_insert
BEFORE INSERT ON distance
FOR EACH ROW
BEGIN
    IF NEW.didistance < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Distance must better than 0';
    END IF;
END $$

CREATE TRIGGER before_distance_update
BEFORE UPDATE ON distance
FOR EACH ROW
BEGIN
    IF NEW.didistance < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Distance must better than 0';
    END IF;
END $$

DELIMITER ;

-- 排课结果表
CREATE TABLE schedule(
    scid INTEGER AUTO_INCREMENT PRIMARY KEY,
    sctask INTEGER NOT NULL,
    scroom INTEGER NOT NULL,
    FOREIGN KEY (sctask) REFERENCES task(taid),
    FOREIGN KEY (scroom) REFERENCES room(rid),
    tabegin_week INTEGER NOT NULL,
    taend_week INTEGER NOT NULL,
    tabegin_time TIME NOT NULL,
    taend_time TIME NOT NULL,
    UNIQUE (scroom, tabegin_week, taend_week, tabegin_time, taend_time)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

DELIMITER $$

CREATE TRIGGER before_schedule_insert
BEFORE INSERT ON schedule
FOR EACH ROW
BEGIN
    -- 检查时间冲突
    IF EXISTS (
        SELECT 1
        FROM schedule
        WHERE scroom = NEW.scroom
          AND tabegin_week = NEW.tabegin_week
          AND taend_week = NEW.taend_week
          AND (
              (NEW.tabegin_time BETWEEN tabegin_time AND taend_time)
              OR (NEW.taend_time BETWEEN tabegin_time AND taend_time)
              OR (tabegin_time BETWEEN NEW.tabegin_time AND NEW.taend_time)
              OR (taend_time BETWEEN NEW.tabegin_time AND NEW.taend_time)
          )
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Time conflict: Another course is already scheduled in this room during the specified time';
    END IF;

    IF NEW.taend_week <= NEW.tabegin_week THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'End week must better than start week';
    END IF;

    IF NEW.taend_time <= NEW.tabegin_time THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'End time must better than start time';
    END IF;

END $$

CREATE TRIGGER before_schedule_update
BEFORE UPDATE ON schedule
FOR EACH ROW
BEGIN
    -- 检查时间冲突
    IF EXISTS (
        SELECT 1
        FROM schedule
        WHERE scroom = NEW.scroom
          AND tabegin_week = NEW.tabegin_week
          AND taend_week = NEW.taend_week
          AND scid != NEW.scid -- 排除自身
          AND (
              (NEW.tabegin_time BETWEEN tabegin_time AND taend_time)
              OR (NEW.taend_time BETWEEN tabegin_time AND taend_time)
              OR (tabegin_time BETWEEN NEW.tabegin_time AND NEW.taend_time)
              OR (taend_time BETWEEN NEW.tabegin_time AND NEW.taend_time)
          )
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Time conflict: Another course is already scheduled in this room during the specified time';
    END IF;

    IF NEW.taend_week <= NEW.tabegin_week THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'End week must better than start week';
    END IF;

    IF NEW.taend_time <= NEW.tabegin_time THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'End time must better than start time';
    END IF;

END $$

DELIMITER ;