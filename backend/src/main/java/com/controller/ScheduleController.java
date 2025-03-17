package com.controller;

import com.entity.Schedule;
import com.mapper.ScheduleMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
public class ScheduleController {
    @Autowired
    private ScheduleMapper scheduleMapper;


    @RequestMapping("/select")//显示schedule表的示例
    public List<Schedule> select(){
        return scheduleMapper.selectList(null);
    }
}//查看schedule表的控制器
