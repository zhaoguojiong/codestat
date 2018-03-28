# -*- coding: utf-8 -*-

'实用工具'

__author__ = "Jason Zhao <guojiongzhao@139.com>"

import datetime
import os

# 日期中年、月、日之间的分隔符，例如：2018-01-01
SEP_DATE = '-'
# 日期格式
DATE_FORMAT = '%Y' + SEP_DATE + '%m' + SEP_DATE + '%d'

# 判断一个字符串是否为有效的日期
def is_valid_date(date_str):
	try:
		datetime.datetime.strptime(date_str, DATE_FORMAT)
		return True
	except Exception:
		return False

# 标准化日期字符串，变为：yyyy-mm-dd
def normalize_date(date_str):
	# 通过日期格式化方法，比较笨
	# 先转换为日期
	the_date = datetime.datetime.strptime(date_str, DATE_FORMAT)
	# 然后再对日期进行格式化：yyyy-mm-dd
	return the_date.strftime(DATE_FORMAT)	

# 返回下一个月份，格式为：yyyy-mm-dd
def get_next_month(date_str):
	year = int(date_str.split(SEP_DATE)[0])
	month = int(date_str.split(SEP_DATE)[1])
	if month == 12:
		month = 1
		year += 1
	else:
		month += 1
	next_month = str(year) + SEP_DATE + str(month) + SEP_DATE + '01'

	# 对next_month进行格式规范化
	return normalize_date(next_month)

# 当一个文件名称（含路径）的长度超过指定长度时，将中间目录替换为'...'
def fit_filname(fname, max_len):
	# 循环截取，直到文件名称长度满足要求
	while len(fname) > max_len:
		paths = fname.split(os.path.sep)
		# 取出最中间元素的位置
		middle = round(len(paths) / 2)
		# 将中间的元素替换为'...'
		# 如果中间的元素已经是'...'了，则向左移动，直到遇到第一个不是'...'的元素，将其替换为'...'
		while paths[middle] == '...':
			middle -= 1
		paths[middle] = '...'
		# 重新拼接文件名称
		fname = ''
		for p in paths:
			fname = os.path.join(fname, p)

	return fname

# 将一个字符串line，按一行最大长度max_len折行，返回一个list
# TODO: 未完成
def next_line(line, sep, max_len):
	line_arr = []
	curr_line = line
	while len(curr_line) > max_len:
		# 先拆分为数组
		arr = curr_line.split(sep)
		# 循环尾部删除，直到满足一行长度要求
		new_arr = []


