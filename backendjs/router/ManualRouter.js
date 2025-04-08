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

router.get("/task", async (req, res) => {
    const building = req.query.building;
    const campus = req.query.campus;
    const week = req.query.week;
    let query, params;

    if (building && campus && week) {
        query = `
            SELECT s.scid, s.sctask 
            FROM schedule s 
            JOIN room r ON s.scroom = r.rid 
            WHERE r.rbuilding LIKE ? AND r.rcampus LIKE ? 
            AND s.scbegin_week <= ? AND s.scend_week >= ?;
        `;
        params = [`%${building}%`, `%${campus}%`, week, week];
    } else if (building && week) {
        query = `
            SELECT s.scid, s.sctask 
            FROM schedule s 
            JOIN room r ON s.scroom = r.rid 
            WHERE r.rbuilding LIKE ? 
            AND s.scbegin_week <= ? AND s.scend_week >= ?;
        `;
        params = [`%${building}%`, week, week];
    } else if (campus && week) {
        query = `
            SELECT s.scid, s.sctask 
            FROM schedule s 
            JOIN room r ON s.scroom = r.rid 
            WHERE r.rcampus LIKE ? 
            AND s.scbegin_week <= ? AND s.scend_week >= ?;
        `;
        params = [`%${campus}%`, week, week];
    } else if (building) {
        query = `
            SELECT s.scid, s.sctask 
            FROM schedule s 
            JOIN room r ON s.scroom = r.rid 
            WHERE r.rbuilding LIKE ?;
        `;
        params = [`%${building}%`];
    } else if (campus) {
        query = `
            SELECT s.scid, s.sctask 
            FROM schedule s 
            JOIN room r ON s.scroom = r.rid 
            WHERE r.rcampus LIKE ?;
        `;
        params = [`%${campus}%`];
    } else if (week) {
        query = `
            SELECT s.scid, s.sctask 
            FROM schedule s 
            WHERE s.scbegin_week <= ? AND s.scend_week >= ?;
        `;
        params = [week, week];
    } else {
        query = `
            SELECT s.scid, s.sctask 
            FROM schedule s;
        `;
        params = [];
    }

    const { err, rows } = await db.async.all(query, params);
    if (err) {
        res.send({
            code: 500,
            msg: "数据库读取错误"
        });
    } else {
        res.send({
            code: 200,
            rows
        });
    }
});

//!SCHEDULE relative
router.post("/change",async(req,res)=>{
    const { scid, sctask, scroom, scbegin_week, scend_week, scday_of_week, scslot, scteacherid, scteacherdepartment} = req.body;
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
    const oldSlot = scslot || oldData.scslot;
    const oldTeacherid = scteacherid || oldData.scteacherid;
    const oldTeacherdepartment = scteacherdepartment || oldData.scteacherdepartment;
    //Check if the new data is valid
    if (oldBeginWeek > oldEndWeek) {
        return res.send({
            code: 400,
            msg: "参数错误"
        });
    }
    //update the data in database
    const queryUpdate = "UPDATE `schedule` SET `sctask` = ?, `scroom` = ?, `scbegin_week` = ?, `scend_week` = ?, `scday_of_week` = ?,`scslot` = ?, `scteacherid` = ?, `scteacherdepartment` = ? WHERE `scid` = ?;";
    const paramsUpdate = [oldTask, oldRoom, oldBeginWeek, oldEndWeek, oldDay,oldSlot, oldTeacherid, oldTeacherdepartment, scid];
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
    const query = "SELECT `scid`, `sctask`, `scday_of_week`, `scroom`, `scbegin_week`, `scend_week`,`scslot`, `scteacherid`, `scteacherdepartment`, task.taformclass as `composition` FROM `schedule` join `task` on schedule.sctask=task.taformclassid;";
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