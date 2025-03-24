const express = require("express");
const router = express.Router();
const { db } = require("../db/DbUtils");

/** 统一处理查询 */
const getCountData = async (query, params) => {
    const { err, rows } = await db.async.all(query, params);
    if (err) return { success: false, error: err };
    return { success: true, data: rows };
};

router.get("/", async (req, res) => {
    let week = req.query.week;
    if (!week) return res.send({ code: 400, msg: "缺少 week 参数" });

    try {
        //获取建筑占用率
        const { success: buildingSuccess, data: buildingRows } = await getCountData(
            "SELECT bname FROM building",
            []
        );
        let room_occupancy_rate = [];

        if (buildingSuccess) {
            const buildingNames = buildingRows.map((b) => b.bname);

            const roomCounts = await Promise.all(
                buildingNames.map((b) =>
                    getCountData("SELECT COUNT(*) AS cnt FROM room WHERE building = ?", [b])
                )
            );

            const roomOccupied = await Promise.all(
                buildingNames.map((b) =>
                    getCountData(
                        "SELECT COUNT(*) AS cnt FROM schedule WHERE scbegin_week <= ? AND scend_week >= ? AND building = ?",
                        [week, week, b]
                    )
                )
            );

            room_occupancy_rate = buildingNames.map((building, i) => ({
                building,
                rate: roomCounts[i].success && roomCounts[i].data[0].cnt !== 0 
                      ? roomOccupied[i].data[0].cnt / roomCounts[i].data[0].cnt 
                      : 0,
            }));
        }

        //获取教师授课次数
        const { success: teacherSuccess, data: teacherRows } = await getCountData(
            "SELECT tname FROM teacher",
            []
        );
        let teaching_count = [];

        if (teacherSuccess) {
            const teacherNames = teacherRows.map((t) => t.tname);

            const teacherCounts = await Promise.all(
                teacherNames.map((t) =>
                    getCountData(
                        "SELECT COUNT(*) AS cnt FROM schedule WHERE scbegin_week <= ? AND scend_week >=? AND scteacher = ?",
                        [week, week, t]
                    )
                )
            );

            teaching_count = teacherNames.map((teacher, i) => ({
                teacher,
                teaching_count: teacherCounts[i].success ? teacherCounts[i].data[0].cnt : 0,
            }));
        }

        //获取任务类型次数
        const { success: typeSuccess, data: typeRows } = await getCountData(
            "SELECT DISTINCT tatype FROM task",
            []
        );
        let type_count = [];

        if (typeSuccess) {
            const taskTypes = typeRows.map((t) => t.tatype);

            const typeCounts = await Promise.all(
                taskTypes.map((type) =>
                    getCountData(
                        "SELECT COUNT(*) AS cnt FROM schedule WHERE scbegin_week <= ? AND scend_week >=? AND tatype = ?",
                        [week, week, type]
                    )
                )
            );

            type_count = taskTypes.map((type, i) => ({
                type,
                count: typeCounts[i].success ? typeCounts[i].data[0].cnt : 0,
            }));
        }

        //统一返回数据
        res.send({
            code: 200,
            data: [room_occupancy_rate, teaching_count, type_count],
        });
    } catch (err) {
        res.send({
            code: 500,
            msg: "服务器异常",
        });
    }
});

module.exports = router;