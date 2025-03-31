const express = require("express");
const router = express.Router();
const crypto = require('crypto');
const { db } = require("../db/DbUtils");

router.get("/",async(req,res)=>{
    try {
        // 获取课程安排数据接口
        const coursesResult = await db.async.all(`
            SELECT
                s.scid,
                c.coname as name,
                s.sccampus as campus,
                s.scbuilding as building,
                t.tname as teacher,
                s.scroom as classroom,
                s.scday_of_week as day_of_week,
                s.scbegin_time as startTime,
                s.scend_time as endTime,
                s.scbegin_week as beginWeek,
                s.scend_week as endWeek
            FROM
                schedule s
            LEFT JOIN
                course c ON s.sctask = c.coid
            LEFT JOIN
                teacher t ON s.scteacher = t.tcode
            ORDER BY
                s.scid
        `)

        // 处理课程数据，转换为前端需要的格式
        const formattedCourses = coursesResult.rows
            ? coursesResult.rows.map((course) => {
                const weekday = course.day_of_week || 0;

                const startTime = course.startTime || '00:00';
                const endTime = course.endTime || '00:00';

                const weeks = [];
                if (course.beginWeek && course.endWeek) {
                    for (let i = course.beginWeek; i <= course.endWeek; i++) {
                        weeks.push(i);
                    }
                }

                return {
                    id: course.scid,
                    name: course.name || '未命名课程',
                    teacher: course.teacher || '未分配教师',
                    classroom: course.classroom || '未分配教室',
                    campus: course.campus || '未知校区',
                    building: course.building || '未知教学楼',
                    weekday: weekday,
                    startTime: startTime,
                    endTime: endTime,
                    weeks: weeks.length > 0 ? weeks : [1], // Default to week 1 if no weeks specified
                };
            })
            : [];

        // 如果数据库中没有数据，提供一些模拟数据以便前端开发测试
        if (formattedCourses.length === 0) {
            formattedCourses.push(
                {
                    id: 1,
                    name: "高等数学",
                    teacher: "张教授",
                    classroom: "教学楼A-101",
                    campus: "主校区",
                    building: "教学楼A",
                    weekday: 1,
                    startTime: "08:00",
                    endTime: "09:40",
                    weeks: [1, 2, 3, 4, 5, 6, 7, 8],
                },
                {
                    id: 2,
                    name: "大学物理",
                    teacher: "李教授",
                    classroom: "教学楼B-202",
                    campus: "主校区",
                    building: "教学楼B",
                    weekday: 2,
                    startTime: "10:00",
                    endTime: "11:40",
                    weeks: [1, 2, 3, 4, 5, 6, 7, 8],
                })
        }
        res.send({
            code: 200,
            data: formattedCourses,
        })
    } catch (error) {
        console.error("仪表盘数据错误:", error)
        res.send({
            code: 500,
            msg: "获取仪表盘数据失败",
            error: error.message,
        })
    }
});



module.exports = router;