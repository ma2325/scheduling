CREATE DATABASE schedule;

USE schedule;

--楼号表
CREATE TABLE building(
    bid INTEGER PRIMARY KEY,
    bname VARCHAR(20)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 教室表
CREATE TABLE room(
    rid INTEGER PRIMARY KEY,
    rname VARCHAR(20),
    rbuilding INTEGER NOT NULL,
    rtype ENUM('common','multimedia','sport','special') NOT NULL,
    FOREIGN KEY (rbuilding) REFERENCES building(rbuilding)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 学院表
CREATE TABLE college(
    cid INTEGER PRIMARY KEY,
    cname VARCHAR(20),
    cbuilding INTEGER NOT NULL,
    FOREIGN KEY (cbuilding) REFERENCES building(bid)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 系表
CREATE TABLE department(
    did INTEGER PRIMARY KEY,
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
    coname VARCHAR(20)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 教学任务表
CREATE TABLE task(
    taid INTEGER AUTO_INCREMENT PRIMARY KEY,
    --taname VARCHAR(20),
    tacourse INTEGER  NOT NULL,
    FOREIGN KEY (tacourse) REFERENCES course(coid)
);

CREATE TABLE distance(
    diid INTEGER,
    dibuilding1 INTEGER NOT NULL,
    dibuilding2 INTEGER NOT NULL,
    didistance INTEGER CHECK (didistance > 0) NOT NULL,
    FOREIGN KEY (dibuilding1) REFERENCES building(bid),
    FOREIGN KEY (dibuilding2) REFERENCES building(bid),
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

CREATE TABLE schedule(
    sctask INTEGER NOT NULL,
    scroom INTEGER NOT NULL,
    FOREIGN KEY (sctask) REFERENCES task(taid),
    FOREIGN KEY (scroom) REFERENCES room(rid),
    tabegin_week INTEGER NOT NULL,
    taend_week INTEGER NOT NULL,
    tabegin_time TIME NOT NULL,
    taend_time TIME NOT NULL,
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

DELIMITER $$

CREATE TRIGGER before_schedule_insert
BEFORE INSERT ON schedule
FOR EACH ROW
BEGIN
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