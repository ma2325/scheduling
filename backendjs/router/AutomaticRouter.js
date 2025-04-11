const express = require("express");
const router = express.Router();
const { spawn } = require("child_process");
const { db } = require("../db/DbUtils");

// 接收前端的调课请求
router.put("/", async (req, res) => {
    try {
        const constraints = req.body.soft_constraints;

        // 将 soft_constraints 数组转换为目标字符串格式
        const constraintsString = `${constraints
            .map(item => `(${item.constraintItem}, ${item.priority})`)
            .join(',')}`;

        if (!Array.isArray(constraints)) {
            return res.send({
                code: 400,
                msg: "参数格式错误，应为二维数组 [(id, priority), ...]"
            });
        }

        // 构造 Python 命令行参数
        const softConstraintsArg = constraintsString;
        const pythonPath = "C:\\Users\\86182\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"; // 可按需指定具体路径

        const scriptPath = "C:\\Users\\86182\\OneDrive\\桌面\\软创\\scheduling\\ai\\scheduler_cli.py";

        // 使用 --soft_constraints 参数传递约束条件
        const pythonProcess = spawn(pythonPath, [
            scriptPath,
            "--soft_constraints",
            `(${constraintsString})`
        ], {
            env: {
                ...process.env,
                PYTHONIOENCODING: 'utf-8'  //强制 Python 输出为 UTF-8
            }
        });

        let pythonOutput = "";
        let pythonError = "";

        pythonProcess.stdout.on("data", (data) => {
            pythonOutput += data.toString();
        });

        pythonProcess.stderr.on("data", (data) => {
            pythonError += data.toString();
        });

        pythonProcess.on("close", async (code) => {
            if (code !== 0) {
                return res.send({
                    code: 500,
                    msg: "Python 调度失败",
                    error: pythonError
                });
            }

            const queryTaskCount = "SELECT COUNT(*) AS totalTasks FROM task;";
            const { err: taskErr, rows: taskRows } = await db.async.all(queryTaskCount, []);
            const totalClasses = taskRows[0].totalTasks;

            const queryScheduleCount = "SELECT COUNT(*) AS totalschdule FROM schedule;";
            const { err: scheduleErr, rows: scheduleRows } = await db.async.all(queryScheduleCount, []);
            const scheduledClasses = scheduleRows[0].totalschdule;

            const unscheduledClasses=totalClasses-scheduledClasses;

            const queryRoomCount = "SELECT COUNT(*) AS totalRooms FROM room;";
            const { err: roomErr, rows: roomRows } = await db.async.all(queryRoomCount, []);
            const totalRooms = roomRows[0].totalRooms;

            const queryUsedRoomCount= "SELECT COUNT(DISTINCT scroom) AS usedRoom \n" + "FROM schedule;";
            const { err: usedroomErr, rows: usedRoomRows } = await db.async.all(queryUsedRoomCount, []);
            const usedRooms = usedRoomRows[0].usedRoom;

            const roomRate=usedRooms/totalRooms;

            const queryTeacherCount = "SELECT COUNT(*) AS totalTeacher FROM (SELECT DISTINCT scteachername, scslot FROM schedule) AS unique_pairs;";
            const { err: teacherErr, rows: teacherRows } = await db.async.all(queryTeacherCount, []);
            const totalTeachers = teacherRows[0].totalTeacher;

            const queryScheduledTeacherCount = "SELECT COUNT(*) AS totalScheduledTeacher FROM (SELECT DISTINCT scteachername, scslot FROM schedule) AS unique_pairs;";
            const { err: teacherScheduledErr, rows: ScheduledTeacherRows } = await db.async.all(queryScheduledTeacherCount, []);
            const totalScheduledTeachers = ScheduledTeacherRows[0].totalScheduledTeacher;

            const summary = {
                totalClasses,
                scheduledClasses,
                unscheduledClasses,
                totalRooms,
                usedRooms,
                roomRate,
                totalTeachers,
                totalScheduledTeachers
            };

            return res.send({
                code: 200,
                msg: "自动调课完成",
                data: {
                    summary
                }
            });
        });
    } catch (error) {
        console.error(error);
        return res.send({
            code: 500,
            msg: "服务器内部错误",
            error: error.message
        });
    }
});

module.exports = router;