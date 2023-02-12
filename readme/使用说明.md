# DSL领域特定语言设计 ——chatbot

***

## 简介

chatbot是Windows环境下的DSL客服聊天机器人，支持命令行交互、文件交互

***

## 使用说明

1. 保证您的计算机上安装了Python3.0及以上的版本（推荐Python3.9.5）

2. 下载chatbot.zip并解压，检查文件是否完整
    chatbot目录下内容：
    /lexer.py
    /main.py
    /rcx.txt(非必须)
    /complain.txt(非必须)
    子目录：
    /auto/
    /bat/
    /log/
    /readme/
    /script/
    /var/

3. auto子目录中为示例重定向文件，分别为 `auto1.in,auto1.out, auto2.in, auto2.out`

4. bat子目录中为示例自动执行脚本，共计7个，分别为a0_1.bat, a0_2.bat, a0_3.bat, a1_1.bat, a1_2.bat, a1_3.bat, a2.bat

5. log子目录中保留了脚本解释器的运行日志dsl_rsl.log

6. readme子目录中的是文档，其中有三份说明，分别是语法规则说明、使用说明、设计文档。

7. script子目录中为示例脚本，共计两个：t0.txt, t1.txt

8. var子目录保留了一份示例变量文件：test1.var

***

## 启动

解释器由命令行参数启动，参数默认值可见设计文档和源代码

### 默认启动方式

默认启动方式是命令行交互模式，脚本为示例脚本/script/t0.txt
在chatbot目录下打开cmd窗口
输入以下命令：
>`python main.py`

结果如下

``` python
F:\A\vs code\py_workspace\program_design>python main.py
脚本开始执行


你好,请问有什么可以帮您

```

可见脚本开始解释执行

### 自定义方式

可以通过在`python main.py`之后加入参数的方式来选择脚本、设定解释器的交互方式、是否输出调试信息、是否保留日志等

脚本解释器提供了8个位置参数，自左到右分别为filename,auto_level,test_level,dbg_level,log_level,Auto_out,Auto_in,Test_var

### 参数说明

该解释器接受的是位置参数，所以请确保对应参数形式正确，否则可能造成意想不到的错误

|参数位置|含义      |说明                                                                       |默认值|
|:---:  |:----      |:---:                                                                     |:---:  |
|1      |filename   |指定脚本文件                                                               |./script/t0.txt|
|2      |auto_level |自动等级，当其为1，将标准输入输出重定向到指定文件，为0则在命令行窗口输入输出，默认0    |0|
|3      |test_level |测试等级 当其为1，从指定文件读入构建(补充)变量表，默认0                                |0|
|4      |dbg_level  |调试等级，是否输出调试（错误）信息,1输出，0不输出，默认输出                            |1|
|5      |log_level  |日志等级，是否将脚本运行详情运行写入日志，1写入，0写入，默认为1（写入）                |1|
|6      |Auto_out   |指定重定向输出文件|./auto/auto1.out|
|7      |Auto_in    |指定重定向输入文件|./auto/auto1.in|
|8      |Test_var   |指定变量文件|./var/test1.var|

**注意**:

1. 所有参数都是位置参数，如果只需要更改脚本，其余选择默认条件，那么只需要输入第一个参数
    如：
    >`python main.py ./script/t1.txt`

    但是，如果要设定第5个参数（日志等级）为0，则前4个参数都要输入
    如：
    >`python main.py ./script/t0.txt 0 0 1 0`

2. 请勿输入错误形式的参数，这将导致无法预料的错误

## 执行范例

1. 运行示例脚本t0.txt
   在chatbot目录下打开cmd窗口，输入以下命令(指定不输出调试信息，其余使用默认选项)，开始运行脚本
    >`python main.py ./script/t0.txt 0 0 0 1`

    屏幕输出：
    >`你好,请问有什么可以帮您`

    输入：
    >`你好`

    屏幕输出：
    >`对不起，无法理解您所说的内容，请说再一遍`
    `你好,请问有什么可以帮您`

    输入：
    >`查账单`

    屏幕输出：
    >`请输入你的账户`

    输入：
    >`rcx`

    屏幕输出：
    >`您的本月账单是20.0元`
    `你好,请问有什么可以帮您`

    输入：
    >`退出`

    屏幕输出：
    >`感谢你的来电，再见`

    至此，脚本执行完毕，程序结束
    完整的过程如下

    ``` python
    F:\A\vs code\py_workspace\program_design>python main.py ./script/t0.txt 0 0 0 1
    你好,请问有什么可以帮您
    你好
    对不起，无法理解您所说的内容，请说再一遍
    你好,请问有什么可以帮您
    查账单
    请输入你的账户
    rcx
    您的本月账单是20.0元
    你好,请问有什么可以帮您
    退出
    感谢你的来电，再见

    ```
