from math import log
import re
import shlex
import time
KEY_LIST = [
    "Def", "Step", "End_step", "Speak", "Listen", "Switch", "End_switch",
    "Branch", "Default", "Go", "Exp", "Write", "Read", "Slience", "Exit"
]
DTYPE = ["Num", "Str"]
OP = ["+", "-", "*", "/", "="]

# 符号表按行记录，每个元素是一行也是一个列表，子列表元素是token类的对象
token_list = []
# 词法分析的变量表只记录变量名
Var_list = []
# 程序块表记录程序块名以及程序块行号,是一个字典
Step_table = {}

# 记号有四个属性，名字，类型，值，行号
class token(object):
    def __init__(self, name, type, value, line):
        self.name = name
        self.type = type
        self.val = value
        self.line = line

def log_in_lex(content,logname):
    file = open(logname,'a+',encoding='utf-8')
    content = str(content) +"\n"
    file.write(content)
    file.close()

def log_end_lex(logname):
    file = open(logname,'a+',encoding='utf-8')
    t="\n\n"+ time.asctime()+"\n"
    file.write(t)
    file.write("脚本解释执行结束\n")
    file.write("********************************************\n")
    file.close()

def lex_error(line_c,dbg_level,log_level,logname):
    if dbg_level >0:
        print("该脚本有词法错误，错误出现在第{}行".format(line_c + 1))
    if log_level>0:
        content = "该脚本有词法错误，错误出现在第{}行".format(line_c + 1)
        log_in_lex(content,logname)
        log_end_lex(logname)
    exit()


def l_syn_error(line_c,dbg_level,log_level,logname):
    if dbg_level >0:
        print("该脚本有语法错误，在第{}行".format(line_c + 1))
    if log_level>0:
        content = "该脚本有语法错误，在第{}行".format(line_c + 1)
        log_in_lex(content,logname)
        log_end_lex(logname)
    exit()

def file_error(dbg_level,log_level,logname):
    if dbg_level>0:
        print("不存在该脚本或脚本有词法错误")
    if log_level>0:
        content = "不存在该脚本或脚本有词法错误"
        log_in_lex(content,logname)
        log_end_lex(logname)
    exit()



def lex_deal(templine, line_c,dbg_level,log_level,logname):
    line_token_list = []

    lex = shlex.shlex(templine)
    lex.commenters = []
    lex.whitespace = [' ','\n']
    lex.whitespace_split = True
    line_token_row = list(lex)

    for i in line_token_row:
        name = i
        type = ""
        value = ""
        # 关键字
        if name in KEY_LIST:
            type = "KEY"

        # 数据类型符号
        elif name in DTYPE:
            type = "DTYPE"

        # 程序块符号
        elif name[0] == "_":
            type = "BLOCK"

        # 注释
        elif name == "#":
            temp_token = token("#", "NOTE", "", line_c)
            line_token_list.append(temp_token)
            break
        # 运算符
        elif name in OP:
            type = "OP"
        # 数字
        elif name.isdigit():
            type = "NUM"
            value = float(name)
        # 字符串
        elif name[0] == r'"' and name[-1] == r'"' or name[0] == r"'" and name[
                -1] == r"'":
            type = "STRING"
            value = eval(name)
        # 界符
        # elif name :
        #     type = "BOUND"

        # 标识符
        elif name.islower():
            type = "ID"

        else:
            # print("该脚本有词法错误，错误出现在第%d行" % line_c+1)
            # exit()
            lex_error(line_c,dbg_level,log_level,logname)

        temp_token = token(name, type, value, line_c)
        line_token_list.append(temp_token)
    if len(line_token_list) == 0:
        name = "Blank"
        type = "BLANK"
        value = ""
        temp_token = token(name, type, value, line_c)
        line_token_list.append(temp_token)
        # token_list.append(line_token_list)
    token_list.append(line_token_list)

    if len(line_token_row) > 0:
        if line_token_row[0] == "Def" and line_token_row[1] in DTYPE:
            if len(line_token_list) != 4:
                # print("该脚本有语法错误，在第{}行".format(line_c+1))
                # exit()
                l_syn_error(line_c,dbg_level,log_level,logname)
            else:
                temp = line_token_row[2]
                if temp not in Var_list:
                    Var_list.append(line_token_row[2])

        if line_token_row[0] == "Step":
            if line_token_list[1].type == "BLOCK" and len(
                    line_token_list) == 2:
                a = line_token_row[1]
                b = line_c
                Step_table[a] = b
            else:
                # print("该脚本有语法错误，在第{}行".format(line_c+1))
                # exit()
                l_syn_error(line_c,dbg_level,log_level,logname)


def lexer(filename,dbg_level,log_level,logname):
    try:
        # fname = input("请输入脚本文件名\n")
        # print(fname)
        file = open(filename, "r", encoding="utf-8")
        if log_level>0:
            content = "当前运行的脚本是:"+filename+"\n\n"
            log_in_lex(content,logname)
        templine = file.readline()
        # print(templine)
        line_c = 0
        while len(templine) > 0:
            lex_deal(templine, line_c,dbg_level,log_level,logname)
            line_c = line_c + 1
            try:
                templine = file.readline()
            except:
                break
    except:
        file_error(dbg_level,log_level,logname)

    return token_list


# lexer()
# print(Var_list)
# for i in range( len(token_list)):
#     for j in range(len(token_list[i])):
#         k=token_list[i][j]
#         print("{} {} {} {}".format(k.name,k.type,k.val,k.line),end="\t")
#     print()

# print(Step_table)
