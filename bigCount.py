# -*- coding: utf-8 -*-
#/usr/bin/env python
# Get the number of files in the directory
import subprocess
import threading
from multiprocessing import Manager
from multiprocessing import Process
import getopt, sys
# Dirs
Father = '/app'
# True result
Ok_result = Manager().list()
# Temp result
Temp_result = Manager().list()


def paternal(part_char, th_args):
    """
    thread Fun
    :return:
    """
    asc_sign = th_args['asc_sign']
    on_sign = th_args['on_sign']
    other_list = th_args['other_list']
    oasc_sign = th_args['oasc_sign']
    info_sign = th_args['info_sign']
    global Temp_result
    global Ok_result
    if asc_sign:
        part_char = chr(part_char)
    # info
    out_list = []
    command = 'cd %s;find %s* -type f |wc -l' % (Father, part_char)
    res = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out_list.append('%s/%s*' % (Father, part_char))
    err_str = res.stderr.read()
    if not err_str:
        nums = res.stdout.read()
        Ok_result.append(int(nums))
        out_list.append('--- have %s' % nums)
    elif 'No such file' in err_str:
        nums = 0
        Ok_result.append(nums)
        out_list.append('--- have %d' % 0)
    elif 'Argument list too long' in err_str:
        if on_sign and other_list:
            inner(str(part_char), oasc_sign, other_list, info_sign, 0, 0)
        else:
            inner(str(part_char), False, None, info_sign)
            inner(str(part_char), True, None, info_sign, 97, 122)
            inner(str(part_char), True, None, info_sign, 65, 90)
            if other_list:
                inner(str(part_char), oasc_sign, other_list, info_sign, 0, 0)
        all_result = sum(Temp_result)
        Temp_result = []
        Ok_result.append(all_result)
        out_list.append('--- have %d' % all_result)
    else:
        out_list.append('--- %s' % err_str)
    if info_sign != 'False':
        for info_part in out_list:
            print(info_part)


def inner(part_char, oasc_sign, other_list, info_sign, inner_start=1, inner_end=9):
    """
     The twice iteration when you have many files
    :param part_char:
    :param char_sign:
    :param inner_start:
    :param inner_end:
    :return:
    """
    out_list = []

    def common_use(common_part):
        in_command = 'cd %s;find %s%s* -type f |wc -l'%(Father, part_char, common_part)
        in_res = subprocess.Popen(in_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print('%s/%s%s*' % (Father, part_char, common_part))
        out_list.append('%s/%s%s*' % (Father, part_char, common_part))
        in_err_str = in_res.stderr.read()
        if not in_err_str:
                nums = in_res.stdout.read()
                Temp_result.append(int(nums))
                out_list.append('--- have %s' % nums)
        elif 'No such file' in in_err_str:
                nums = 0
                Temp_result.append(int(nums))
                out_list.append('--- have %d' % 0)
        elif 'Argument list too long' in in_err_str:
                inner(str(part_char), False, None, info_sign)
                inner(str(part_char), True, None, info_sign, 97, 122)
                inner(str(part_char), True, None, info_sign, 65, 90)
        else:
                out_list.append('--- %s' % in_err_str)
    global Temp_result
    for inner_part in range(inner_start, inner_end+1):
        if oasc_sign:
            temp_part = chr(inner_part)
        else:
            temp_part = inner_part
        common_use(temp_part)

    if other_list and isinstance(other_list, list):
        for other_part in other_list:
            common_use(other_part)

    if info_sign != 'False':
        for info_part in out_list:
            print(info_part)


def many_thread(part_list, th_args):
    """
    # many thread
    :return:
    """
    th_list = []
    for th_part in part_list:
        th = threading.Thread(target=paternal, args=(th_part, th_args))
        th_list.append(th)
    for th_obj in th_list:
        th_obj.start()
    for th_obj_part in th_list:
        th_obj_part.join()


def many_process(**kwargs):
    """
    2 processes
    :param pro_arg_list:
    :return:
    """
    pro_arg_list = kwargs['obj_list']
    global Ok_result
    middle_arg = len(pro_arg_list)//2
    first = pro_arg_list[0:middle_arg]
    second = pro_arg_list[middle_arg:len(pro_arg_list)]
    p1 = Process(target=many_thread, args=(first, kwargs,))
    p2 = Process(target=many_thread, args=(second, kwargs,))
    pro_ist = [p1, p2]
    for pro_part in pro_ist:
        pro_part.start()
    for pro_part_02 in pro_ist:
        pro_part_02.join()
    print("="*60)
    print("All files is: ", sum(Ok_result))


def main():
    """
    main
    :return:
    """
    def help_info():
        print("""
        --help   Display help document \n
        --info   True/False，是否打印输出,默认True \n
        --father 要查找的目录，必填，默认是/app目录 \n
        --range  True/False，Object是否是连续的数字，如果是True,Object是1,9 则实际会遍历1-9这九个数字,默认False \n
        --Object 逗号分隔的字符串,必填，遍历的范围，如果你的目录的开头是1到9数字，此处填写1,9;如果你的目录分别是
        a,b,c开头，此处填写a,b,c \n
        --ascii  True/False,是否使用ascii,默认False,比如你要遍历a-z时应该开启此项，然后Object赋值97,122 \n
        --oascii True/False,是否使用ascii,默认False,比如你要遍历a-z时应该开启此项，然后Other赋值97,122 \n
        --Other 逗号分隔的字符串,非必填,有的时候你的文件太多，只用第一个开头字母遍历时间太长，需要添加第二个字母;
        默认是遍历a-z和A-Z和1-9; \n
        --only   True/False,非必填,是否只使用Other列表，默认是False
        """)
        exit()
    opts, args = getopt.getopt(sys.argv[1:], '', ['help', 'father=', 'oascii=', 'ascii=', 'range='
                                                                     , 'Object=', 'Other=', 'only=', 'info='])
    # only sign
    on_sign = False
    # other_list
    other_list = None
    # ascii sign
    asc_sign = False
    # info message
    info_sign = True
    # other ascii sign
    oasc_sign = False
    # range sign
    range_sign = False
    #
    obj_list = []
    #
    r_obj_list = []
    global Father
    for opt_name, opt_value in opts:
        if opt_name in ('-h', '--help'):
            help_info()
        if opt_name in ('-a', '--ascii'):
            if not opt_value:
                help_info()
            elif opt_value != 'True' and opt_value != 'False':
                help_info()
            else:
                asc_sign = opt_value
        if opt_name in ('-o', '--oascii'):
            if not opt_value:
                help_info()
            elif opt_value != 'True' and opt_value != 'False':
                help_info()
            else:
                oasc_sign = opt_value
        if opt_name in ('-i', '--info'):
            if not opt_value:
                help_info()
            elif opt_value != 'True' and opt_value != 'False':
                help_info()
            else:
                info_sign = opt_value
        if opt_name in ('-f', '--father'):
            if not opt_value:
                help_info()
            else:
                Father = opt_value
        if opt_name in ('-o', '--Object'):
            if not opt_value:
                help_info()
            else:
                obj_list = opt_value.strip().split(',')
        if opt_name in ('-on', '--only'):
            if not opt_value:
                pass
            elif opt_value != 'True' and opt_value != 'False':
                help_info()
            else:
                on_sign = opt_value
        if opt_name in ('-r', '--range'):
            if not opt_value:
                pass
            elif opt_value != 'True' and opt_value != 'False':
                help_info()
            else:
                range_sign = opt_value
        if opt_name in ('-oo', '--other'):
            if not opt_value:
                help_info()
            else:
                other_list = opt_value.strip().split(',')
    #  range_sign
    if range_sign:
        r_obj_list = []
        for r_part in range(int(obj_list[0]), int(obj_list[1])+1):
            r_obj_list.append(r_part)
    # begin many process
    if len(sys.argv) > 1 and not range_sign:
        many_process(obj_list=obj_list, on_sign=on_sign, other_list=other_list, asc_sign=asc_sign,
                                        info_sign=info_sign, oasc_sign=oasc_sign)
    elif len(sys.argv) > 1 and range_sign:
        many_process(obj_list=r_obj_list, on_sign=on_sign, other_list=other_list, asc_sign=asc_sign,
                                        info_sign=info_sign, oasc_sign=oasc_sign)
    else:
        help_info()


if __name__ == '__main__':
    main()
