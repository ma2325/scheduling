const express = require("express");
const router = express.Router();
const crypto = require('crypto');
const { db } = require("../db/DbUtils");

router.post("/login",async(req,res)=>{
    let { account,password } = req.body;
    let passwordh = crypto.createHash('sha256').update(password).digest('hex');
    let {err,rows} = await db.async.all("select * from `admin` where `account` = ? AND `password` = ?",[account,passwordh]);
    if(err == null && rows.length > 0){
        res.send({
            code:200,
            msg:"登录成功"
        })
    }else{
        res.send({
            code:500,
            msg:"登陆失败"
        })
    }
})

router.post("/signup",async(req,res)=>{
    let { account,password } = req.body;
    let passwordh = crypto.createHash('sha256').update(password).digest('hex');
    let {err,rows} = await db.async.all("select * from `admin` where `account` = ?",[account]);
    if(err == null && rows.length > 0){
        res.send({
            code:500,
            msg:"账号已存在"
        })
    }else{
        let {err,result} = await db.async.run("insert into `admin` (`account`,`password`) values (?,?)",[account,passwordh]);
        if(err == null && result.affectedRows > 0){
            res.send({
                code:200,
                msg:"注册成功"
            })
        }else{
            res.send({
                code:500,
                msg:"注册失败"
            })
        }
    }
})
module.exports = router;