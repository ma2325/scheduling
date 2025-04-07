const express = require("express");
const router = express.Router();
const { db } = require("../db/DbUtils");

router.get("/room",async(req,res)=>{
    const building = req.query.building;
    const campus = req.query.campus;
    let query,params;
    if(building && campus){
        query = "SELECT `rid`,`rname` FROM `room` WHERE `rbuilding` LIKE ? AND `rcampus` LIKE ? ;";
        params = [`%${building}%`,`%${campus}%`];
    }else if(building){
        query = "SELECT `rid`,`rname` FROM `room` WHERE `rbuilding` LIKE ? ;";
        params = [`%${building}%`];
    }else if(campus){
        query = "SELECT `rid`,`rname` FROM `room` WHERE `rcampus` LIKE ? ;";
        params = [`%${campus}%`];
    }else{
        query = "SELECT `rid`,`rname` FROM `room`;";
        params = [];
    }
    const {err,rows} = await db.async.all(query,params);
    if(err){
        res.send({
            "code":500,
            "msg":"数据库读取错误"
        });
    }else{
        res.send({
            "code":200,
            rows
        });
    }
});

router.get("/task",async (req,res)=>{
    const building = req.query.building;
    const campus = req.query.campus;
    const week = req.query.week;
    let query,params;
    if(building && campus && week){
        query = "SELECT `scid`,`sctask` FROM `schedule` WHERE `scbuilding` LIKE ? AND `sccampus` LIKE ? AND `scbegin_week` <= ? AND `scend_week` >= ?;";
        params = [`%${building}%`,`%${campus}%`,`%${week}%`,`%${week}%`];
    }else if(building && week){
        query = "SELECT `scid`,`sctask` FROM `schedule` WHERE `scbuilding` LIKE ? AND `scbegin_week` <= ? AND `scend_week` >= ?;";
        params = [`%${building}%`,`%${week}%`,`%${week}%`];
    }else if(campus && week){
        query = "SELECT `scid`,`sctask` FROM `schedule` WHERE `sccampus` LIKE ? AND `scbegin_week` <= ? AND `scend_week` >= ?;";
        params = [`%${campus}%`,`%${week}%`,`%${week}%`];
    }else if(building){
        query = "SELECT `scid`,`sctask` FROM `schedule` WHERE `scbuilding` LIKE ?;";
        params = [`%${building}%`];
    }else if(campus){
        query = "SELECT `scid`,`sctask` FROM `schedule` WHERE `sccampus` LIKE ?;";
        params = [`%${campus}%`];
    }else if(week){
        query = "SELECT `scid`,`sctask` FROM `schedule` WHERE `scbegin_week` <= ? AND `scend_week` >= ?;";
        params = [`%${week}%`,`%${week}%`];
    }else{
        query = "SELECT `scid`,`sctask` FROM `schedule`;";
        params = [];
    }
    const {err,rows} = await db.async.all(query,params);
    if(err){
        res.send({
            "code":500,
            "msg":"数据库读取错误"
        });
    }else{
        res.send({
            "code":200,
            rows
        });
    }
});
//!SCHEDULE relative
router.post("/change",async(req,res)=>{
    const { scid, sctask, scroom, scbegin_week, scend_week, scday_of_week, scbegin_time, scend_time, scteacher} = req.body;
    const queryOld = "SELECT * FROM `schedule` WHERE `scid` = ?;";
    const paramsOld = [scid];
    const { err: errOld, rows: rowsOld } = await db.async.all(queryOld, paramsOld);
    if (errOld) {
        return res.send({
            code: 500,
            msg: "数据库读取错误"
        });
    }
    if (rowsOld.length === 0) {
        return res.send({
            code: 404,
            msg: "未找到对应的课程"
        });
    }
    //If value posted is null, it should equals with old data, else it should be changed
    const oldData = rowsOld[0];
    const oldScid = scid || oldData.scid;
    const oldTask = sctask || oldData.sctask;
    const oldRoom = scroom || oldData.scroom;
    const oldBeginWeek = scbegin_week || oldData.scbegin_week;
    const oldEndWeek = scend_week || oldData.scend_week;
    const oldDay = scday_of_week || oldData.scday_of_week;
    const oldBeginTime = scbegin_time || oldData.scbegin_time;
    const oldEndTime = scend_time || oldData.scend_time;
    const oldTeacher = scteacher || oldData.scteacher;
    //Check if the new data is valid
    if (oldBeginWeek > oldEndWeek || oldBeginTime > oldEndTime) {
        return res.send({
            code: 400,
            msg: "参数错误"
        });
    }
    //update the data in database
    const queryUpdate = "UPDATE `schedule` SET `sctask` = ?, `scroom` = ?, `scbegin_week` = ?, `scend_week` = ?, `scday_of_week` = ?, `scbegin_time` = ?, `scend_time` = ?, `scteacher` = ? WHERE `scid` = ?;";
    const paramsUpdate = [oldTask, oldRoom, oldBeginWeek, oldEndWeek, oldDay, oldBeginTime, oldEndTime, oldTeache, scid];
    const { err: errUpdate, result: resultUpdate } = await db.async.run(queryUpdate, paramsUpdate);
    if (errUpdate) {
        return res.send({
            code: 500,
            msg: "数据库更新错误"
        });
    }else{
        return res.send({
            code: 200,
            msg: "课程信息修改成功"
        });
    }

})

router.get("/all",async(req,res)=>{
    const query = "SELECT `scid`, `sctask`, `scday`, `scroom`, `scbegin_week`, `scend_week`, `scbegin_time`s, `scend_time`, `scteacher`, task.taformclass as `composition` FROM `schedule` join `task` on schedule.sctask=task.taname;";
    const params = [];
    const {err,rows} = await db.async.all(query,params);
    if(err){
        res.send({
            "code":500,
            "msg":"数据库读取错误"
        });
    }else{
        res.send({
            "code":200,
            rows
        });
    }
})

module.exports = router;