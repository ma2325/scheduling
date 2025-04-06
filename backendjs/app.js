const express = require("express")
const multer = require("multer")
const path =require("path");
const app = express();
const { db } = require("./db/DbUtils");
const port = 8080;

/*Cross-Origin Requests */
app.use(function(req,res,next){
    res.header("Access-Control-Allow-Origin","*");
    res.header("Access-Control-Allow-Headers","*");
    res.header("Access-Control-Allow-Methods","DELETE,PUT,POST,GET,OPTIONS");
    if(req.method == "OPTIONS") res.sendStatus(200);
    else next();
});

/*Dealing json data */
app.use(express.json());

app.use("/admin",require("./router/AdminRouter"))
app.use("/dashboard",require("./router/DashboardRouter"))
app.use("/statistics",require("./router/StatisticsRouter"))
app.use("/manual",require("./router/ManualRouter"));

app.get("/",(req,res)=>{
    res.send("hello world");
});

app.listen(port,()=>{
    console.log(`启动成功: http://localhost:${port}/`);
});