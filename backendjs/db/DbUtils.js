const mysql = require("mysql2"); // 使用 mysql2 库
const path = require("path");

// 创建 MySQL 连接池
const pool = mysql.createPool({
  host: "localhost", // MySQL 服务器地址
  user: "root",      // 数据库用户名
  password: "123456", // 数据库密码
  database: "schedule",  // 数据库名称
  waitForConnections: true, // 是否等待连接
  connectionLimit: 200,      // 连接池最大连接数
  queueLimit: 0,            // 排队等待的连接数（0 表示不限制）
});

require('events').EventEmitter.defaultMaxListeners = 150;

pool.getConnection((err, connection) => {
  if (err) {
    if (err.code === 'ER_ACCESS_DENIED_ERROR') {
      console.error("数据库账号或密码错误！");
    } else {
      console.error("数据库连接失败：", err.message);
    }
    process.exit(1);
  } else {
    console.log("数据库连接成功！");
    connection.setMaxListeners(150); 
    connection.release();
  }
});

// 封装异步方法
const db = {
  async: {
    // 查询多条数据
    all: (sql, params) => {
      return new Promise((resolve, reject) => {
        pool.query(sql, params, (err, rows) => {
          if (err) {
            reject(err);
          } else {
            resolve({ err: null, rows });
          }
        });
      });
    },

    // 执行 SQL 语句（如 INSERT, UPDATE, DELETE）
    run: (sql, params) => {
      return new Promise((resolve, reject) => {
        pool.query(sql, params, (err, result) => {
          if (err) {
            reject(err);
          } else {
            resolve({ err: null, result });
          }
        });
      });
    },
  },
};

// 导出模块
module.exports = { db };