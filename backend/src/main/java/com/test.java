package com.example.backend;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class test {
    @RequestMapping("/toin")
    public String toIndex(){
        return "index";
    }
}
