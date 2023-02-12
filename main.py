from os import name
from lexer import *
import time
import re
import sys
# 自动等级 当其为1，将标准输入输出重定向到指定文件，为0则在命令行窗口输入输出
Auto_level = 0
Auto_in = "./auto/auto1.in"
Auto_out = "./auto/auto1.out"
# 测试等级 当其为1，从指定文件读入构建变量表,默认为0
Test_level = 0
Test_var = "./var/test1.var"
# 调试等级，是否输出调试（错误）信息,默认输出
Dbg_level = 1
# 日志等级，是否将脚本运行详情运行写入日志，默认为1（写入）
Log_level = 1
Logname = "./log/dsl_rsl.log"

# 类型符号
Type = ["KEY", "DTYPE", "BLOCK", "NOTE", "OP", "NUM", "STRING", "BOUND", "ID"]
# 运行时全局变量表
# 变量名，类型，值
Var_table = []
# 栈信息
# 层深，行号，该层switch（选择分支）控制符,选择分支，比较符
Stack = []
# 当前行指针
Temp_line = 0
# 当前层深
Temp_depth = 0
# 允许定义变量标志
Dflag = 1


# 变量类型
class Var(object):
    def __init__(self, name, type, val):
        self.name = name
        self.type = type
        self.val = val


# 栈元素
class Level(object):
    def __init__(self, depth, line, sflag, smember):
        self.depth = depth
        self.line = line
        self.sflag = sflag
        self.smember = smember


def init_var():
    global Temp_depth, Temp_line
    # 初始化层深和行号 选择分支标志，比较符
    Temp_line = 0
    Temp_depth = 0
    sflag = 0
    smember = ""
    # print(smember)
    level0 = Level(Temp_depth, Temp_line, sflag, smember)
    Stack.append(level0)
    # 初始化运行时变量表
    for i in range(len(Var_list)):
        name = Var_list[i]
        type = ""
        value = ""
        var = Var(name, type, value)
        Var_table.append(var)


def syn_error():
    global Dbg_level, Log_level
    if Dbg_level > 0:
        print("该脚本有语法错误，在第{}行".format(Temp_line + 1))
    if Log_level > 0:
        content = "该脚本有语法错误，在第{}行".format(Temp_line + 1)
        log_in(content)
        end_log()
    exit()


def run_error():
    global Dbg_level, Log_level
    if Dbg_level > 0:
        print("非法操作，在第{}行".format(Temp_line + 1))
    if Log_level > 0:
        content = "非法操作，在第{}行".format(Temp_line + 1)
        log_in(content)
        end_log()
    exit()


def scr_exit():
    global Dbg_level, Log_level
    if Dbg_level:
        print("\n在第{}行，脚本遇到退出命令，结束运行".format(Temp_line + 1))
    if Log_level > 0:
        content = "\n在第{}行，脚本遇到退出命令，结束运行".format(Temp_line + 1)
        log_in(content)
        end_log()
    exit()


def inc():
    global Temp_line, Temp_depth, Dbg_level, Log_level
    Temp_line += 1
    Stack[Temp_depth].line = Temp_line
    if Temp_line > len(token_list):
        if Dbg_level > 0:
            print("该脚本无法正常结束，请检查Step 与End_step数目是否匹配")
            if Log_level > 0:
                content = "该脚本无法正常结束，请检查Step 与End_step数目是否匹配"
                log_in(content)
                end_log()
        exit()


# 该函数的作用是 判断变量是否为变量表的一项，如果是，返回下标（索引）
def check_var(var):
    vflag = -1
    for i in range(len(Var_table)):
        if var.name == Var_table[i].name:
            vflag = i
    return vflag


def closeDflag():
    global Dflag
    if Dflag == 1:
        Dflag = 0


# 打印当前全局变量表
def print_var_table():
    for i in Var_table:
        print("{}   {}  {}".format(i.name, i.type, i.val))


def Def_process():
    # Def语句每行只允许有4个单词，仅在Dflag 为1时可以定义全局变量
    global Dflag
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    if tnum == 4 and Dflag == 1:
        if token_line[1].type == "DTYPE":
            if token_line[2].type == "ID":
                if token_line[3].type in ["NUM", "STRING"]:
                    # 检查该变量是否在变量表中
                    var = token_line[2]
                    i = check_var(var)
                    # 若该行没有语法错误，执行语义动作
                    if i >= 0:
                        syn = 0
                        # 语义动作为，为变量表中对应变量设置type和value
                        Var_table[i].type = token_line[1].name
                        Var_table[i].val = token_line[3].val
                        # 指针下移一行
                        inc()
                        # print_var_table()
    if syn == 1:
        syn_error()
        # exit()


def Step_process():
    # 一旦进入Step禁止再定义全局变量
    closeDflag()

    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    # 语法检查： Step 后只能跟1个程序块符号
    if tnum == 2:
        if token_line[1].type == "BLOCK":
            # 该行没有语法错误, 也无语义动作,指针下移一行
            syn = 0
            inc()

    if syn == 1:
        syn_error()
        # exit()


def Speak_process():
    global Log_level
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    # 语法检查： Speak 后只能跟1个标识符/字符串
    if tnum == 2:
        if token_line[1].type == "ID" or token_line[1].type == "STRING":
            # 用sentence存储要输出的内容
            sentence = ""
            if token_line[1].type == "ID":
                # 获取变量在变量表的位置
                var = token_line[1]
                i = check_var(var)
                if i >= 0:
                    syn = 0
                    sentence = Var_table[i].val
            if token_line[1].type == "STRING":
                syn = 0
                sentence = token_line[1].val
            # 该行没有语法错误, 语义动作是输出标识符的内容,指针下移一行
            if syn == 0:
                sentence = str(sentence)
                print(sentence)

                if Log_level > 0:
                    content = sentence
                    log_in(content)

                inc()
    if syn == 1:
        syn_error()
        # exit()


def Listen_process():
    global Log_level
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    # 语法检查： Listen 后只能跟1个(字符串类型)标识符
    if tnum == 2:
        if token_line[1].type == "ID":
            var = token_line[1]
            i = check_var(var)
            if i >= 0 and Var_table[i].type in ["Str","Num"]:
                # 该行没有语法错误, 语义动作是接受键盘输入的内容，保存到变量表对应的变量中,指针下移一行
                syn = 0
                try:
                    sentence = input()
                    if  Var_table[i].type =="Num":
                        sentence = float(sentence)
                    Var_table[i].val = sentence
                    if Log_level > 0:
                        content = "\n用户输入：" + str(sentence) + "\n"
                        log_in(content)
                    inc()
                # print_var_table()
                except:
                    run_error()
    if syn == 1:
        syn_error()
        # exit()


def Switch_process():
    global Temp_line, Temp_depth
    # Switch 后跟1个标识符
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    if tnum == 2 and token_line[1].type in ["ID"] and Stack[Temp_depth].sflag == 0:
        var = token_line[1]
        i = check_var(var)
        if i >= 0:
            member = Var_table[i].val
            # 语法正确，语义动作为：
            # 开启当前层的sflag，以允许Branch和Default 匹配
            # 直到遇到End_switch ,关闭当前层的sflag
            # 将标识符暂存到当前层的smember
            syn = 0
            Stack[Temp_depth].sflag = 1
            Stack[Temp_depth].smember = member
            inc()

    if syn == 1:
        syn_error()


def End_switch_process():
    global Temp_line, Temp_depth
    # End_switch 后不接任何符号
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    if tnum == 1:
        # 语法正确，语义动作为：
        # 关闭当前层的sflag
        syn = 0
        Stack[Temp_depth].sflag = 0
        inc()

    if syn == 1:
        syn_error()


def go_to(block_name):
    global Temp_depth, Temp_line
    # 栈保存当前层次信息，创建新层次
    new_depth = Temp_depth + 1
    new_line = Step_table[block_name]
    new_sflag = 0
    new_smember = ''
    new_level = Level(new_depth, new_line, new_sflag, new_smember)
    Stack.append(new_level)
    # 更新当前层次，当前行号指针
    Temp_depth = new_depth
    Temp_line = new_line


def return_to():
    global Temp_depth, Temp_line
    Stack.pop()
    Temp_depth = Temp_depth - 1
    Temp_line = Stack[Temp_depth].line
    Temp_line = Temp_line + 1


def Branch_process():
    global Temp_line, Temp_depth
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    if tnum == 3 and token_line[1].type in [
            "ID", "STRING"
    ] and token_line[2].type in ["BLOCK"]:
        block_name = token_line[2].name
        if block_name in Step_table.keys():
            content = token_line[1].val
            vflag = 1
            if token_line[1].type in ["ID"]:
                var = token_line[1]
                i = check_var(var)
                if i >= 0:
                    content = Var_table[i].val
                else:
                    vflag = 0
            if vflag == 1:
                # 语法正确，语义动作为: 当sflag开启时匹配，否则直接跳过
                # 将content 与 smember 进行匹配，
                # 成功跳转到下一程序块，失败则不做任何跳转
                # 成功则关闭sflag
                # 匹配规则有两种
                # 若content 与smember均为数值型，只有相等才算成功
                # 若content 与smember均为字符串型，content
                syn = 0
                smember = Stack[Temp_depth].smember
                if Stack[Temp_depth].sflag == 0:
                    inc()
                else:
                    success = 0
                    if type(content) == type(smember) and type(
                            content) == type(1.0):
                        if content == smember:
                            # 数值，匹配成功
                            success = 1
                        else:
                            #匹配失败
                            success = 0
                    elif type(content) == type(smember) and type(
                            content) == type("yyt"):
                        if len(content) == 0:
                            if len(smember) == 0:
                                success = 1
                        else:
                            content = '(.*)' + content + '(.*)'
                            if re.match(content, smember, re.M | re.I) != None:
                                success = 1
                            else:
                                # 匹配失败
                                success = 0
                    if success == 1:
                        # 注意关闭sflag要在跳转之前，且不用再更新当前行号指针
                        # 更新行号该操作在返回时进行
                        Stack[Temp_depth].sflag = 0
                        go_to(block_name)
                    else:
                        # 失败，不操作，直接进入下一行
                        inc()
    if syn == 1:
        syn_error()


def Default_process():
    global Temp_line, Temp_depth
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1

    if tnum == 2 and token_line[1].type in ["BLOCK"]:
        block_name = token_line[1].name
        if block_name in Step_table.keys():
            # 语法正确 只要当前层次sflag为1，即可跳转,并关闭sflag,否则 不可以跳转
            syn = 0
            if Stack[Temp_depth].sflag == 1:
                Stack[Temp_depth].sflag = 0
                go_to(block_name)
            else:
                inc()
    if syn == 1:
        syn_error()


def Go_process():
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    if tnum == 2 and token_line[1].type in ["BLOCK"]:
        block_name = token_line[1].name
        if block_name in Step_table.keys():
            # 语法正确，跳转到该程序块
            go_to(block_name)
            syn = 0
    if syn == 1:
        syn_error()


def End_step_process():
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    if tnum == 1:
        # 语法正确，调用return_to
        syn = 0
        return_to()
    if syn == 1:
        syn_error()
        # exit()


def Exp_process():
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    # 语法检查： Exp 能跟3个单词或5个单词
    # 标识符 = 标识符/数字/字符串
    # 标识符 = 标识符/数字 运算符 标识符/数字（只支持数值运算）
    # 标识符 = 标识符/字符串 + 标识符/字符串
    if tnum == 4 and token_line[2].name == "=":
        if token_line[1].type in ["ID"] and token_line[3].type in [
                "NUM", "STRING"
        ]:
            # 常数给变量赋值
            var = token_line[1]
            con = token_line[3]
            i = check_var(var)
            if i >= 0:
                # 无语法错误 语义动作是赋值操作
                if (Var_table[i].type == "Num"
                        and con.type == "NUM") or (Var_table[i].type == "Str"
                                                   and con.type in ["STRING","NUM"]):
                    syn = 0
                    Var_table[i].val = con.val
                    inc()
        if token_line[1].type in ["ID"] and token_line[3].type in ["ID"]:
            # 变量给变量赋值
            # 需要进行类型检查
            var1 = token_line[1]
            var2 = token_line[3]
            i = check_var(var1)
            j = check_var(var2)
            if i >= 0 and j >= 0 and (Var_table[i].type == Var_table[j].type or Var_table[i].type == "Str"):
                # 类型匹配，变量非未定义，即无语法错误
                # 语义动作是赋值操作，执行完毕行号和当前栈行号+1
                syn = 0
                Var_table[i].val = Var_table[j].val
                inc()
    if tnum == 6 and token_line[2].name == "=":
        if token_line[1].type in ["ID"]:
            var1 = token_line[1]
            i = check_var(var1)
            if i >= 0:
                # 变量存在，且为数值类型，那么该表达式为数值运算
                if Var_table[i].type == "Num":
                    if token_line[4].type in ["OP"]:
                        op = token_line[4].name
                        if token_line[3].type in [
                                "ID", "NUM"
                        ] and token_line[5].type in ["ID", "NUM"]:
                            # 常数与变量组成的表达式，检查变量是否定义，检查是否均为数值类型
                            num2 = token_line[3].val
                            num3 = token_line[5].val
                            vflag2 = 1
                            vflag3 = 1
                            # 符号表（不是变量表）中变量初值是"",类型不处理也无所谓，下面会跟据变量表查找当前变量值
                            # 而常数初值一定是float型的
                            if token_line[3].type in ["ID"]:
                                var2 = token_line[3]
                                j = check_var(var2)
                                if j >= 0 and Var_table[j].type == "Num":
                                    # 变量存在且类型为数值型
                                    num2 = float(Var_table[j].val)
                                else:
                                    vflag2 = 0

                            if token_line[5].type in ["ID"]:
                                var3 = token_line[5]
                                k = check_var(var3)
                                if k >= 0 and Var_table[k].type == "Num":
                                    num3 = float(Var_table[k].val)
                                else:
                                    vflag3 = 0

                            if vflag2 == 1 and vflag3 == 1:
                                if type(num2) == type(num3) and type(
                                        num2) == type(1.0):
                                    # 无语法错误，执行语义动作
                                    syn = 0
                                    num1 = 0
                                    if op == "+":
                                        num1 = num2 + num3
                                    if op == "-":
                                        num1 = num2 - num3
                                    if op == "*":
                                        num1 = num2 * num3
                                    if op == "/":
                                        # 除操作可能导致出错
                                        if num3 == 0:
                                            run_error()
                                            # exit()
                                        else:
                                            num1 = num2 / num3
                                    Var_table[i].val = num1
                                    inc()
                # 变量存在，且为字符串类型，那么该表达式为字符串拼接运算
                if Var_table[i].type == "Str":
                    # 字符串支持的运算只有拼接
                    if token_line[4].name in ["+"]:
                        # 检查参与拼接的变量，常量类型是否正确
                        if token_line[3].type in [
                                "ID", "NUM", "STRING"
                        ] and token_line[5].type in ["ID", "NUM", "STRING"]:
                            vflag2 = 1
                            vflag3 = 1
                            str2 = token_line[3].val
                            str3 = token_line[5].val
                            # 检查变量是否未定义
                            if token_line[3].type in ["ID"]:
                                var2 = token_line[3]
                                j = check_var(var2)
                                if j < 0:
                                    vflag2 = 0
                                else:
                                    str2 = str(Var_table[j].val)
                            if token_line[5].type in ["ID"]:
                                var3 = token_line[5]
                                k = check_var(var3)
                                if k < 0:
                                    vflag2 = 0
                                else:
                                    str3 = str(Var_table[k].val)
                            if vflag2 == 1 and vflag3 == 1:
                                # 无语法错误,执行语义动作进行字符串拼接
                                syn = 0
                                Var_table[i].val = str2 + str3
                                inc()
    if syn == 1:
        syn_error()
        # exit()
    # else:
    # print_var_table()


def Read_process():
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    if tnum == 4 and token_line[1].type in [
            "STRING", "ID"
    ] and token_line[2].type in ["NUM"] and token_line[3].type in ["ID"]:
        fname = token_line[1].val
        fline = int(token_line[2].val)
        vflag2 = 1
        vflag3 = 1
        if token_line[1].type in ["ID"]:
            var2 = token_line[1]
            i = check_var(var2)
            if i >= 0 and Var_table[i].type == "Str":
                fname = Var_table[i].val

            else:
                vflag2 = 0
        var3 = token_line[3]
        j = check_var(var3)
        if j >= 0 and Var_table[j].type in ["Str","Num"]:
            vflag3 = 1
        else:
            vflag3 = 0
        if vflag2 == 1 and vflag3 == 1:
            # 语法正确,执行语义动作
            syn = 0
            # 从文件读入某一行
            try:
                file = open(fname, 'r', encoding='utf-8')
                for i in range(fline - 1):
                    templine = file.readline()
                templine = file.readline()
                templine = templine.strip('\n')
                if Var_table[j].type =="Num":
                    templine= float(templine)
                Var_table[j].val = templine
                file.close()
            except:
                run_error()
            inc()
    if syn == 1:
        syn_error()
    # else:
    #     print_var_table()


def Write_process():
    # 第一个符号指明文件名，
    # 第二个指明写入信息，
    # 第三个符号是写入方式： 0覆盖，1追加
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    if tnum == 4:
        if token_line[1].type in ["STRING", "ID"] and token_line[2].type in [
                "STRING", "ID"
        ] and token_line[3].type in ["NUM"]:
            mode = int(token_line[3].val)
            if mode == 1 or mode == 0:
                fname = token_line[1].val
                wline = token_line[2].val
                vflag2 = 1
                vflag3 = 1
                if token_line[1].type in ["ID"]:
                    var2 = token_line[1]
                    i = check_var(var2)
                    if i >= 0 and Var_table[i].type == "Str":
                        fname = Var_table[i].val
                    else:
                        vflag2 = 0
                if token_line[2].type in ["ID"]:
                    var3 = token_line[2]
                    j = check_var(var3)
                    if j >= 0 and Var_table[j].type in ["Str","Num"]:
                        wline = Var_table[j].val
                    else:
                        vflag2 = 0
                if vflag2 == 1 and vflag3 == 1:
                    # 无语法错误
                    syn = 0
                    wline = str(wline) + "\n"
                    if mode == 1:
                        # 追加写文件
                        try:
                            file = open(fname, 'a+', encoding='utf-8')
                            file.write(wline)
                            file.close()
                        except:
                            run_error()
                    if mode == 0:
                        # 覆盖写文件
                        try:
                            file = open(fname, 'w', encoding='utf-8')
                            file.write(wline)
                            file.close()
                        except:
                            run_error()
                    inc()

    if syn == 1:
        syn_error()


def Slience_process():
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    if tnum == 2 and token_line[1].type in ["NUM"]:
        # 语法正确，语义动作是等待一段时间
        syn = 0
        con = token_line[1]
        time.sleep(con.val)
        inc()
    if syn == 1:
        syn_error()
        # exit()


def Exit_process():
    token_line = token_list[Temp_line]
    tnum = len(token_line)
    syn = 1
    if tnum == 1:
        # 语法正确
        syn = 0
        scr_exit()
        inc()

    if syn == 1:
        syn_error()


def Note_process():
    inc()


def Blank_process():
    inc()


def run():
    global Temp_line, Dbg_level
    # 第0层的行号未到End_step行，则继续执行即可
    if Dbg_level > 0:
        print("脚本开始执行\n\n")
    while token_list[Stack[0].line][0].name != "End_step":
        # 根据语法规则：每行第一个符号必须是关键字,根据关键字分情况处理
        if token_list[Temp_line][0].name in KEY_LIST or token_list[Temp_line][
                0].name in ["Blank", "#"]:
            t1 = token_list[Temp_line][0].name
            if t1 == "Def":
                Def_process()
            elif t1 == "Step":
                Step_process()
            elif t1 == "End_step":
                End_step_process()
            elif t1 == "Speak":
                Speak_process()
            elif t1 == "Listen":
                Listen_process()
            elif t1 == "Switch":
                Switch_process()
            elif t1 == "End_switch":
                End_switch_process()
            elif t1 == "Branch":
                Branch_process()
            elif t1 == "Default":
                Default_process()
            elif t1 == "Go":
                Go_process()
            elif t1 == "Exp":
                Exp_process()
            elif t1 == "Write":
                Write_process()
            elif t1 == "Read":
                Read_process()
            elif t1 == "Slience":
                Slience_process()
            elif t1 == "Exit":
                Exit_process()
            elif t1 == "#":
                Note_process()
            elif t1 == "Blank":
                Blank_process()
        else:
            syn_error()
    if Temp_depth == 0:
        if Dbg_level > 0:
            print("\n\n脚本执行完毕")


# 脚本按行号逐行执行，边语法检查边执行
# 执行完一句（非跳转语句），当前行号+1
# 层深初始化为0，（将该程序块入栈），直到该块结束，脚本运行结束
# 遇到跳转到一程序块，保存当前层次信息（层深，行号）即遇到BLOCK符号，层深+1
# 根据程序块表跳转到对应行，（相当于该程序块入栈）记录新的当前行号及层深，接着执行
# 直到遇到End_step,


def start_log():
    global Logname
    file = open(Logname, 'a+', encoding='utf-8')
    t = time.asctime() + "\n"
    file.write("********************************************\n")
    file.write(t)
    file.write("脚本开始解释执行\n")
    file.close()


def end_log():
    global Logname
    file = open(Logname, 'a+', encoding='utf-8')
    t = "\n\n" + time.asctime() + "\n"
    file.write(t)
    file.write("脚本解释执行结束\n")
    file.write("********************************************\n")
    file.close()


def log_in(content):
    global Logname
    file = open(Logname, 'a+', encoding='utf-8')
    content = str(content) + "\n"
    file.write(content)
    file.close()


def renew_var():
    file = open(Test_var, "r", encoding='utf-8')
    line_var_list = file.readline().split()
    while len(line_var_list) > 0:
        try:
            name = line_var_list[0]
            type = line_var_list[1]
            value = line_var_list[2]
            if type in ["Num", "Str"]:
                if type == "Num":
                    value = float(value)
            var1 = Var(name, type, value)
            i = check_var(var1)
            if i >= 0:
                Var_table[i].type = var1.type
                Var_table[i].value = var1.val
            else:
                Var_table.append(var1)
            line_var_list = file.readline().split()
        except:
            pass


def deal_argv(argv):
    global Auto_level, Auto_in, Auto_out, Test_level, Test_var, Dbg_level, Log_level
    filename = './script/t0.txt'
    if len(argv) > 1:
        filename = argv[1]
    if len(argv) > 2:
        Auto_level = int(argv[2])
    if len(argv) > 3:
        Test_level = int(argv[3])
    if len(argv) > 4:
        Dbg_level = int(argv[4])
    if len(argv) > 5:
        Log_level = int(argv[5])
    if len(argv) > 6:
        Auto_out = argv[6]
    if len(argv) > 7:
        Auto_in = argv[7]
    if len(argv) > 8:
        Test_var = argv[8]
    return filename


# main
# 接受参数分别为 filename,auto_level,test_level,dbg_level,log_level,Auto_out,Auto_in,Test_var
# 默认值分别为： ./script/t0.txt   0   0   1   1 ./auto/auto1.out ./auto/auto1.in ./var/test1.var
argv = sys.argv
filename = deal_argv(argv)
if Log_level > 0:
    start_log()
auto_out = open(Auto_out, 'w', encoding='utf-8')
auto_in = open(Auto_in, 'r', encoding='utf-8')
if Auto_level > 0:
    sys.stdout = auto_out
    sys.stdin = auto_in
lexer(filename, Dbg_level, Log_level, Logname)
init_var()
if Test_level > 0:
    renew_var()
run()
if Log_level > 0:
    end_log()
auto_out.close()
auto_in.close()