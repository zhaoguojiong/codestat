# -*- coding: utf-8 -*-

'实用工具'

__author__ = "Jason Zhao <guojiongzhao@139.com>"

import datetime

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