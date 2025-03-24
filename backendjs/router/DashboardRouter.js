const express = require("express");
const router = express.Router();
const { db } = require("../db/DbUtils");

router.get("/",async(req,res)=>{
    let {err,rows} = await db.async.all("select * from `schedule`;");
    if(err == null && rows.length > 0){
        res.send({
            code:200,
            data:rows
        });
    }else{
        res.send({
            code:500,
            msg:"获取失败"
        });
    }
});

module.exports = router;