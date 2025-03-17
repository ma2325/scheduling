package com.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import com.baomidou.mybatisplus.annotation.*;

@Data
@AllArgsConstructor
@NoArgsConstructor
@TableName("schedule")
public class Schedule {
    @TableId(type = IdType.AUTO)  // 主键
    @TableField("scid")
    private int scid;

    @TableField("sctask")
    private int sctask;

    @TableField("scroom")
    private int scroom;

    @TableField("tabegin_week")
    private int tabegin_week;

    @TableField("taend_week")
    private int taend_week;

    @TableField("tabegin_time")
    private String tabegin_time;

    @TableField("taend_time")
    private String taend_time;
}//schedule表
