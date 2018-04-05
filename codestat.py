# -*- coding: utf-8 -*-

__author__ = 'Jason Zhao <guojiongzhao@139.com>'

import os
import sys
import logging
import datetime
import matplotlib.pyplot as plt
import numpy as np

# 自己的模块
import projstat
import config
import utils

# 获得logger实例
logger = logging.getLogger()
# 设置日志格式
formatter = logging.Formatter('%(levelname)s %(asctime)s: %(message)s', '%Y-%m-%d %H:%M:%S')
# 设置文件日志处理器
file_handler = logging.FileHandler('codestat.log')
file_handler.setFormatter(formatter)
# 设置控制台日志处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
# 为logger添加日志处理器（同时console输出和文件输出）
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# 设置日志级别
logger.setLevel(logging.INFO)

# output文件的根目录
output_root = os.path.join('.', 'output')

# 命令行参数的name
P_PROJECT = '--project'
P_UPDATE_CODES = '--update_codes'
P_CREATE_LOG = '--create_log'
P_SINCE = '--since'
P_BEFORE = '--before'
P_ORIGINAL_AUTHOR = '--original_author'
P_SUBTOTAL = '--subtotal'
P_DEBUG = '--debug'
P_OUTPUT = '--output'
P_STAT_BY_MONTH = '--stat_by_month'
P_STAT_TYPE = '--stat_type'
P_CHART = '--chart'
P_SKIPPED_FILES = '--skipped_files'
P_NOT_UTF8_FILES = '--not_utf8_files'
P_ERROR_FILES = '--error_files'

# 部分命令行参数的有效value
P_OUTPUT_CONSOLE = 'console'
P_OUTPUT_FILE = 'file'
P_STAT_TYPE_COMMITS = 'commits'
P_STAT_TYPE_FINAL_LINES = 'final-lines'

# 分隔符
# 各个***_stat_month{}中的key中的两个月份的分隔符，例如：2018-01-01:2018-02-01
SEP_STAT_MONTH_KEY = ':'
# 命令行参数--project的value中的group与project之间的分隔符，例如：xueleapp/classroom
SEP_CMD_PROJ = '/'
# 命令行参数中param和value的分隔符，例如：--output=file
SEP_CMD_PV = '='
# output文件中各列之间的分隔符，例如：2018-01-01	2018-02-01	treasury	unknown	23459	25.4	350	25.5
SEP_OUTPUT_FILE_COLUMN = '\t'
# 菜单序号及二级参数值的分隔符
SEP_MENU = '/'

# 统计基类
class Stat(object):
	# 公共类变量，用于设置所有子类的日志对象
	logger = None

	# 输出各个***_stat{}时的公共表头列名（统计指标列）
	metrics = ['added lines', 'lines%', 'commits', 'commits%']

	# 准备要写入文件的一行数据
	# cols是一个数组
	def prepare_to_write(self, cols):
		# 拼接一行数据，列之间以\t分隔
		line = ''
		for c in cols:
			line += SEP_OUTPUT_FILE_COLUMN + str(c)
		# 去掉行首第一个列分隔符
		line = line.strip(SEP_OUTPUT_FILE_COLUMN)
		logger.debug('prepare to write: %s', line)
		return line + '\n'

	# 将stat中的数据绘制到条形图中，stat是一个dict类型，key是X轴，key的value是一个list类型，元素序号num对应的值是Y轴
	def draw(self, stat, num):
		x_name = []
		y = []
		for d in stat:
			x_name = x_name + [d]
			y = y + [stat[d][num]]
		
		# 当X轴的点太多时，X轴显示重叠，所以X轴中显示数字序号，console打印序号与实际内容的对应关系
		x = range(1, len(x_name) + 1)
		for i in x:
			print('%3d: %s%s' % (i, x_name[i - 1].ljust(30), str(y[i - 1]).rjust(20)))
		
		plt.bar(x=x, height=y, color='green', width=0.5)
		plt.show()

# proj_stat{}的统计类
class ProjStat(Stat):
	# 输出proj_stat{}时的表头列名
	COLUMNS_PROJ_STAT = ['project', 'branch'] + Stat.metrics

	def __init__(self):
		# __stat{}存储每个项目的统计结果，dict类型，key为project名称，value为统计结果数组[branch, added lines, commits]
		self.__stat = {}
	
	def get_stat(self):
		return self.__stat

	# proj参数类型是Project对象
	def add(self, proj):
		proj_name = proj.get_proj_name()
		# 转换项目名称，并合并统计结果
		if proj_name in config.proj_merge:
			proj_name = config.proj_merge[proj_name]
		if not (proj_name in self.__stat):
			self.__stat[proj_name] = proj.get_proj_stat()
		else:
			self.__stat[proj_name][1] += proj.get_proj_stat()[1]
			self.__stat[proj_name][2] += proj.get_proj_stat()[2]
	
	# 计算proj_stat{}的lines和commits的总数
	def sum(self):
		total_lines = 0
		total_commits = 0
		for p in self.__stat:
			total_lines += self.__stat[p][1]
			total_commits += self.__stat[p][2]
		return total_lines, total_commits

	# 格式化打印输出proj_stat{}的一行
	def __print_oneline(self, cols):
		# 设置各列的宽度
		PROJECT_COL_WIDTH = 30
		BRANCH_COL_WIDTH = 20
		LINES_COL_WIDTH = 20
		COMMITS_COL_WIDTH = 20
		PERCENT_COL_WIDTH = 10

		logger.info('%s%s%s%s%s%s',
			str(cols[0]).rjust(PROJECT_COL_WIDTH), 
			str(cols[1]).rjust(BRANCH_COL_WIDTH), 
			str(cols[2]).rjust(LINES_COL_WIDTH), 
			str(cols[3]).rjust(PERCENT_COL_WIDTH), 
			str(cols[4]).rjust(COMMITS_COL_WIDTH),
			str(cols[5]).rjust(PERCENT_COL_WIDTH))

	# 格式化打印输出proj_stat{}，返回lines和commits的总数
	def print(self):
		# 打印表头
		self.__print_oneline(self.COLUMNS_PROJ_STAT)

		# 先统计总数，因为要计算百分比
		total_lines, total_commits = self.sum()

		# 打印每一行数据
		total_projects = 0
		for p in self.__stat:
			total_projects += 1
			lines_percent = '%.1f' % (self.__stat[p][1] / total_lines * 100)
			commits_percent = '%.1f' % (self.__stat[p][2] / total_commits * 100)
			self.__print_oneline([p, self.__stat[p][0], self.__stat[p][1], lines_percent, self.__stat[p][2], commits_percent])

		# 打印最后的总计行
		logger.info('')
		self.__print_oneline(['total %d projects' % total_projects, '', total_lines, '', total_commits, ''])
		logger.info('')

		return total_lines, total_commits

	# 绘制条形图，X轴是project，Y轴是commits（index_type=2）或added lines（index_type=1）
	def draw(self, index_type):
		# 调用父类中的方法
		super().draw(self.__stat, index_type)

# proj_author_stat{}的统计类
class ProjAuthorStat(Stat):
	# 输出proj_author_stat{}时的表头列名
	COLUMNS_PROJ_AUTHOR_STAT = ['project', 'branch', 'author'] + Stat.metrics

	# subtotal：决定是否输出每个项目的合计行
	def __init__(self, subtotal: False):
		# __stat{}保存每个项目、每个人的统计结果，dict类型，key为project名称，value为另一个dict类型，该dict的key为author，value为统计结果数组[branch, added lines, commits]
		# key中的author可能为原始的author格式，即“name <email>”；也可能为规范的email。由命令行参数--original_author决定
		self.__stat = {}
		self.__subtotal = subtotal
	
	def get_stat(self):
		return self.__stat

	# stat参数类型是ProjStat对象
	def add_proj_stat(self, stat):
		self.__proj_stat = stat

	# proj参数类型是Project对象
	def add(self, proj):
		proj_name = proj.get_proj_name()	
		# 转换项目名称，并合并统计结果
		if proj_name in config.proj_merge:
			proj_name = config.proj_merge[proj_name]
		if not (proj_name in self.__stat):
			self.__stat[proj_name] = proj.get_author_stat()
		else:
			for author in proj.get_author_stat():
				if author in self.__stat[proj_name]:
					self.__stat[proj_name][author][1] += proj.get_author_stat()[author][1]
					self.__stat[proj_name][author][2] += proj.get_author_stat()[author][2]
				else:
					self.__stat[proj_name][author] = proj.get_author_stat()[author]

	# 格式化打印输出proj_author_stat{}的一行
	def __print_oneline(self, cols, author_width: 30):
		# 设置各列的宽度
		PROJECT_COL_WIDTH = 30
		BRANCH_COL_WIDTH = 20
		AUTHOR_COL_WIDTH = author_width
		LINES_COL_WIDTH = 15
		COMMITS_COL_WIDTH = 15
		PERCENT_COL_WIDTH = 15

		logger.info('%s%s%s%s%s%s%s' % (
			str(cols[0]).rjust(PROJECT_COL_WIDTH), 
			str(cols[1]).rjust(BRANCH_COL_WIDTH), 
			str(cols[2]).rjust(AUTHOR_COL_WIDTH), 
			str(cols[3]).rjust(LINES_COL_WIDTH), 
			str(cols[4]).rjust(PERCENT_COL_WIDTH), 
			str(cols[5]).rjust(COMMITS_COL_WIDTH),
			str(cols[6]).rjust(PERCENT_COL_WIDTH)))	

	# 格式化打印输出proj_author_stat{}中的给定项目的总计行
	def __print_subtotal(self, proj, proj_lines, proj_commits, author_width: 30):
		ps = self.__proj_stat.get_stat()

		# 如果proj_author_stat中的总计数值与proj_stat中的不同，则打印特殊标记
		if proj_lines != ps[proj][1]:
			proj_lines = str(proj_lines) + '!=' + str(ps[proj][1])
		if proj_commits != ps[proj][2]:
			proj_commits = str(proj_commits) + '!=' + str(ps[proj][2])
		self.__print_oneline([proj, '', 'total', proj_lines, '', proj_commits, ''], author_width)

	# 计算proj_author_stat{}中各个project的lines和commits的总数，返回一个dict结构，key为project名称，value为统计结果数组
	def sum_by_proj(self):
		tmp_proj_stat = {}
		for p in self.__stat:
			for a in self.__stat[p]:
				if p in tmp_proj_stat:
					# 累计这个项目的lines
					tmp_proj_stat[p][0] += self.__stat[p][a][1]
					# 累计这个项目的commits
					tmp_proj_stat[p][1] += self.__stat[p][a][2]
				else:
					# 放入这个项目的第一行数据
					tmp_proj_stat[p] = [self.__stat[p][a][1], self.__stat[p][a][2]]
		return tmp_proj_stat

	# 获得proj_author_stat{}中author的最大长度
	def __get_max_author_len(self):
		max_author_len = 0
		for p in self.__stat:
			for a in self.__stat[p]:
				if len(a) > max_author_len:
					max_author_len = len(a)
		max_author_len += 5
		return max_author_len

	# 格式化打印输出proj_author_stat{}
	def print(self):
		# 获得author的最大长度
		max_author_len = self.__get_max_author_len()

		# 打印表头
		self.__print_oneline(self.COLUMNS_PROJ_AUTHOR_STAT, max_author_len)

		# 先统计每个项目的总数，因为要计算百分比
		tmp_proj_stat = self.sum_by_proj()

		# 打印每一行数据
		total_commits = 0
		total_lines = 0
		last_proj = ''
		for p in self.__stat:
			for a in self.__stat[p]:
				# 可能存在有commit、但lines为0的情况
				if tmp_proj_stat[p][0] == 0:
					lines_percent = '-'
				else:
					lines_percent = '%.1f' % (self.__stat[p][a][1] / tmp_proj_stat[p][0] * 100)
				commits_percent = '%.1f' % (self.__stat[p][a][2] / tmp_proj_stat[p][1] * 100)

				# 先打印上一个项目的总计行
				if self.__subtotal and last_proj != '' and p != last_proj:
					self.__print_subtotal(last_proj, tmp_proj_stat[last_proj][0], tmp_proj_stat[last_proj][1], max_author_len)
				last_proj = p

				self.__print_oneline([p, self.__stat[p][a][0], a, self.__stat[p][a][1], lines_percent, self.__stat[p][a][2], commits_percent], max_author_len)

				# 累计所有项目的lines和commits
				total_lines += self.__stat[p][a][1]
				total_commits += self.__stat[p][a][2]

		# 打印最后一个项目的总计行
		if self.__subtotal and len(self.__stat) > 0:
			self.__print_subtotal(last_proj, tmp_proj_stat[last_proj][0], tmp_proj_stat[last_proj][1], max_author_len)

		# 打印最后的总计行
		logger.info('')
		self.__print_oneline(['total %d projects' % len(tmp_proj_stat), '', '', total_lines, '', total_commits, ''], max_author_len)
		logger.info('')

		return total_lines, total_commits

	# 绘制给定project的条形图，X轴是author，Y轴是commits（index_type=2）或added lines（index_type=1）
	def draw(self, index_type, proj):
		if proj in self.__stat:
			# 调用父类中的方法
			super().draw(self.__stat[proj], index_type)
		else:
			print(proj + ' is not existed')
	
# author_stat{}的统计类
class AuthorStat(Stat):
	# 输出author_stat{}时的表头列名
	COLUMNS_AUTHOR_STAT = ['author'] + Stat.metrics

	def __init__(self):
		# __stat{}保存每个人的统计结果（不区分项目），dict类型，key为author，value为统计结果数组[added lines, commits]
		# author的格式同ProjAuthorStat的__stat{}中的key中的author
		self.__stat = {}
	
	def get_stat(self):
		return self.__stat

	# proj参数类型是Project对象
	# 将proj对象中的author_stat{}累加到本对象的__stat{}中，按author
	def add_sum(self, proj):
		this_stat = proj.get_author_stat()
		
		for author in this_stat:
			if author in self.__stat:
				self.__stat[author][0] += this_stat[author][1]
				self.__stat[author][1] += this_stat[author][2]
			else:
				self.__stat[author] = [this_stat[author][1], this_stat[author][2]]
	
	# 格式化打印输出author_stat{}的一行
	def __print_oneline(self, cols, author_width: 30):
		# 设置各列的宽度
		AUTHOR_COL_WIDTH = author_width
		LINES_COL_WIDTH = 15
		COMMITS_COL_WIDTH = 15
		PERCENT_COL_WIDTH = 15

		logger.info('%s%s%s%s%s',
			str(cols[0]).rjust(AUTHOR_COL_WIDTH), 
			str(cols[1]).rjust(LINES_COL_WIDTH), 
			str(cols[2]).rjust(PERCENT_COL_WIDTH), 
			str(cols[3]).rjust(COMMITS_COL_WIDTH),
			str(cols[4]).rjust(PERCENT_COL_WIDTH))

	# 计算author_stat{}中的lines和commits的总数
	def sum(self):
		total_commits = 0
		total_lines = 0
		for a in self.__stat:
			# 累计所有人的lines和commits
			total_lines += int(self.__stat[a][0])
			total_commits += int(self.__stat[a][1])
		return total_lines, total_commits

	# 获得author_stat{}中author的最大长度
	def __get_max_author_len(self):
		max_author_len = 0
		for a in self.__stat:
			if len(a) > max_author_len:
				max_author_len = len(a)
		max_author_len += 5
		return max_author_len

	# 格式化打印输出author_stat{}
	def print(self):
		# 获得author的最大长度
		max_author_len = self.__get_max_author_len()

		# 打印表头
		self.__print_oneline(self.COLUMNS_AUTHOR_STAT, max_author_len)

		# 先统计所有author的总数，因为要计算百分比
		total_lines, total_commits = self.sum()

		# 打印每一行数据
		for author in self.__stat:
			lines_percent = '%.1f' % (self.__stat[author][0] / total_lines * 100)
			commits_percent = '%.1f' % (self.__stat[author][1] / total_commits * 100)

			self.__print_oneline([author, self.__stat[author][0], lines_percent, self.__stat[author][1], commits_percent], max_author_len)

		# 打印最后的总计行
		logger.info('')
		self.__print_oneline(['total %d authors' % len(self.__stat), total_lines, '', total_commits, ''], max_author_len)
		logger.info('')

		return total_lines, total_commits

	# 绘制条形图，X轴是author，Y轴是commits（index_type=2）或added lines（index_type=1）
	def draw(self, index_type):
		# 调用父类中的方法
		super().draw(self.__stat, index_type - 1)

# 月统计的基类
class StatMonth(Stat):
	# whole_since、whole_before：命令行参数传入的since、befoer，不是按月统计时的每一个月的since、before
	# stat_by_month：是否按月输出统计结果（会自动拆分月），也决定输出的文件是按月统计的***_month.txt文件，还是整体上一个统计时间段的文件
	# filename_prefix：输出文件的前缀：proj_stat、proj_author_stat、author_stat
	def __init__(self, filename_prefix, whole_since, whole_before, stat_by_month: False):
		self.whole_since = whole_since
		self.whole_before = whole_before
		self.stat_by_month = stat_by_month

		# stat_month{}保存每个月的统计结果，dict类型，key为'this_month:next_month'，value为具体的***Stat对象
		# key中的this_month为统计月份的1日的日期，格式为yyyy-mm-dd，如2018-01-01；next_month为统计月份的下一个月的1日的日期，格式同this_month。
		# 例如，存放2018年1月的统计数据，则key为'2018-01-01:2018-02-01'
		self.stat_month = {}

		# 构建输出文件名称
		if self.stat_by_month:
			self.output_filename = os.path.join(output_root, '%s_%s_%s_month.txt' % (filename_prefix, self.whole_since, self.whole_before))
		else:
			self.output_filename = os.path.join(output_root, '%s_%s_%s.txt' % (filename_prefix, self.whole_since, self.whole_before))

	# stat参数类型是***Stat对象（ProjStat、ProjAuthorStat、AuthorStat）
	def add(self, since, before, stat):
		key = since + SEP_STAT_MONTH_KEY + before
		self.stat_month[key] = stat

	# 返回month列表，list类型
	def get_month_list(self):
		month_list = []
		for sm in self.stat_month:
			month_list = month_list + [sm]
		return month_list

	# 按key（可能是一个project或author）绘制条形图，X轴是key，key的value是一个list类型，元素序号num对应的值是Y轴
	def draw_key(self, index_type, month=None):
		# 没有传month，表示不是按月统计，则取出self.stat_month中的第一个元素（实际上也只有一个元素）
		if month == None:
			for sm in self.stat_month:
				stat = self.stat_month[sm]
				break
		# 传了month，则只绘制这个月的条形图
		else:
			if month in self.stat_month:
				stat = self.stat_month[month]
			else:
				print(month + ' is not existed')
				return
		
		# stat是一个ProjStat或AuthorStat对象，要实现draw方法
		stat.draw(index_type)
	
	# 将stat_month中的给定key（可能是一个project或author）的各个月的数据绘制到条形图中，key的value是一个list类型，元素序号num对应的值是Y轴
	def draw_month(self, num, key):
		x_name = []
		y = []
		for sm in self.stat_month:
			since = sm.split(SEP_STAT_MONTH_KEY)[0]
			x_name = x_name + [since]

			stat = self.stat_month[sm].get_stat()
			if key in stat:
				y = y + [stat[key][num]]
			else:
				y = y + [0]
		
		# 当X轴的点太多时，X轴显示重叠，所以X轴中显示数字序号，console打印序号与实际内容的对应关系
		x = range(1, len(x_name) + 1)
		for i in x:
			print('%3d: %s%s' % (i, x_name[i - 1].ljust(30), str(y[i - 1]).rjust(20)))
		
		plt.bar(x=x, height=y, color='green', width=0.5)
		plt.show()

	# 返回key（可能是project或author）列表，list类型
	def get_key_list(self):
		key_list = []
		for sm in self.stat_month:
			stat = self.stat_month[sm]
			for key in stat.get_stat():
				if not (key in key_list):
					key_list = key_list + [key]
		return key_list
	
# ProjStat的月统计类
class ProjStatMonth(StatMonth):
	# 将proj_stat_month{}（即父类中的stat_month{}）写入到文件中
	def write(self):
		if len(self.stat_month) == 0:
			return

		logger.info('writing to %s', self.output_filename)
		with open(self.output_filename, 'w', encoding='utf-8') as f:
			# 写入表头
			line = self.prepare_to_write(['since', 'before'] + ProjStat.COLUMNS_PROJ_STAT)
			f.write(line)

			for sm in self.stat_month:
				# 取出这个月的since、before和proj_stat{}
				since = sm.split(SEP_STAT_MONTH_KEY)[0]
				before = sm.split(SEP_STAT_MONTH_KEY)[1]
				proj_stat = self.stat_month[sm]
				stat = proj_stat.get_stat()

				# 先统计总数，因为要计算百分比
				total_lines, total_commits = proj_stat.sum()

				# 写入每一行数据
				for p in stat:
					lines_percent = '%.1f' % (stat[p][1] / total_lines * 100)
					commits_percent = '%.1f' % (stat[p][2] / total_commits * 100)
					line = self.prepare_to_write([since, before, p, stat[p][0], stat[p][1], lines_percent, stat[p][2], commits_percent])
					f.write(line)
	
	# 按project绘制条形图，X轴是project，Y轴是commits（index_type=2）或added lines（index_type=1）
	def draw_proj(self, index_type, month=None):
		# 调用父类的方法
		super().draw_key(index_type, month)

	# 按month绘制某个proj的条形图，X轴是month，Y轴是commits（index_type=2）或added lines（index_type=1）
	def draw_month(self, index_type, proj):
		# 调用父类的方法
		super().draw_month(index_type, proj)

	# 返回project列表，list类型
	def get_proj_list(self):
		# 调用父类的方法
		return super().get_key_list()
	
# ProjAuhtorStat的月统计类
class ProjAuthorStatMonth(StatMonth):
	# 将proj_author_stat_month{}（即父类中的stat_month{}）写入到文件中
	def write(self):
		if len(self.stat_month) == 0:
			return
		
		logger.info('writing to %s', self.output_filename)
		with open(self.output_filename, 'w', encoding='utf-8') as f:
			# 写入表头
			line = self.prepare_to_write(['since', 'before'] + ProjAuthorStat.COLUMNS_PROJ_AUTHOR_STAT)
			f.write(line)

			for sm in self.stat_month:
				since = sm.split(SEP_STAT_MONTH_KEY)[0]
				before = sm.split(SEP_STAT_MONTH_KEY)[1]
				proj_author_stat = self.stat_month[sm]
				stat = proj_author_stat.get_stat()

				# 先统计每个项目的总数，因为要计算百分比
				tmp_proj_stat = proj_author_stat.sum_by_proj()

				# 写入每一行数据
				for p in stat:
					for a in stat[p]:
						# 可能存在有commit、但lines为0的情况
						if tmp_proj_stat[p][0] == 0:
							lines_percent = '-'
						else:
							lines_percent = '%.1f' % (stat[p][a][1] / tmp_proj_stat[p][0] * 100)
						commits_percent = '%.1f' % (stat[p][a][2] / tmp_proj_stat[p][1] * 100)

						line = self.prepare_to_write([since, before, p, stat[p][a][0], a, stat[p][a][1], lines_percent, stat[p][a][2], commits_percent])
						f.write(line)

	# 按author绘制给定project的条形图，X轴是author，Y轴是commits（index_type=2）或added lines（index_type=1）
	def draw_author(self, index_type, proj, month=None):
		# 没有传month，表示不是按月统计，则取出self.stat_month中的第一个元素（实际上也只有一个元素）
		if month == None:
			for sm in self.stat_month:
				proj_author_stat = self.stat_month[sm]
				break
		# 传了month，则只绘制这个月的条形图
		else:
			if month in self.stat_month:
				proj_author_stat = self.stat_month[month]
			else:
				print(month + ' is not existed')
				return

		proj_author_stat.draw(index_type, proj)
	
# AuthorStat的月统计类
class AuthorStatMonth(StatMonth):
	# 将author_stat_month{}（即父类中的stat_month{}）写入到文件中
	def write(self):
		if len(self.stat_month) == 0:
			return

		logger.info('writing to %s', self.output_filename)
		with open(self.output_filename, 'w', encoding='utf-8') as f:
			# 写入表头
			line = self.prepare_to_write(['since', 'before'] + AuthorStat.COLUMNS_AUTHOR_STAT)
			f.write(line)

			for sm in self.stat_month:
				since = sm.split(SEP_STAT_MONTH_KEY)[0]
				before = sm.split(SEP_STAT_MONTH_KEY)[1]
				author_stat = self.stat_month[sm]
				stat = author_stat.get_stat()

				# 先统计所有author的总数，因为要计算百分比
				total_lines, total_commits = author_stat.sum()

				# 打印每一行数据
				for author in stat:
					lines_percent = '%.1f' % (stat[author][0] / total_lines * 100)
					commits_percent = '%.1f' % (stat[author][1] / total_commits * 100)

					line = self.prepare_to_write([since, before, author, stat[author][0], lines_percent, stat[author][1], commits_percent])
					f.write(line)

	# 按author绘制条形图，X轴是author，Y轴是commits（index_type=2）或added lines（index_type=1）
	def draw_author(self, index_type, month=None):
		# 调用父类的方法
		super().draw_key(index_type, month)
	
	# 按month绘制某个author的条形图，X轴是month，Y轴是commits（index_type=2）或added lines（index_type=1）
	def draw_month(self, index_type, author):
		# 调用父类的方法
		super().draw_month(index_type - 1, author)

	# 返回author列表，list类型
	def get_author_list(self):
		# 调用父类的方法
		return super().get_key_list()
	
# final_lines_stat{}的统计类
class FinalLinesStat(Stat):
	# 输出final_lines_stat{}时的表头列名
	FINAL_LINES_TOTAL = projstat.Project.FINAL_LINES_TOTAL
	FINAL_LINES_OTHERS = projstat.Project.FINAL_LINES_OTHERS
	# 开始的固定列（中间的ext列，根据输出样式而定）
	COLUMNS_FINAL_LINES_STAT_FIXED = ['project', 'final lines', 'lines%']
	# 中间的ext列输出为表格样式，即每个ext独立输出一列
	OUTPUT_STYLE_TABLE = 'Table'
	# 中间的ext列输出为列样式，即所有的ext合并为一列显示
	OUTPUT_STYLE_COLUMN = 'Column'

	def __init__(self):
		# __stat{}保存每个项目的final lines统计结果，dict类型，key为project名称，value为final lines的一个dict类型，其中key为扩展名，value为final lines
		self.__stat = {}

		# 表格样式的表头列
		self.__COLUMNS_TABLE_STYLE = self.COLUMNS_FINAL_LINES_STAT_FIXED + projstat.Project.code_file_ext + [self.FINAL_LINES_OTHERS]
		# 列样式的表头列
		self.__COLUMNS_COLUMN_STYLE = self.COLUMNS_FINAL_LINES_STAT_FIXED + ['predefined ext'] + [self.FINAL_LINES_OTHERS]

	def get_stat(self):
		return self.__stat

	# proj参数类型是Project对象
	def add(self, proj):
		proj_name = proj.get_proj_name()
		self.__stat[proj_name] = proj.get_final_lines_stat()

	# 格式化打印输出final_lines_stat{}的一行
	def __print_oneline(self, cols, style):
		# 设置各列的宽度
		PROJECT_COL_WIDTH = 30
		LINES_COL_WIDTH = 20
		PERCENT_COL_WIDTH = 10
		EXT_COL_WIDTH = 10

		# 头三列：project, total lines, percentage
		fmt = '%s%s%s'

		# 中间的ext列
		# 表格样式，即每个ext单独显示一列
		if style == self.OUTPUT_STYLE_TABLE:
			for ext in projstat.Project.code_file_ext:
				fmt += '%s'

			# 最后的others列
			fmt += '%s'

			# 每增加一个新的ext，这里需要增加一个'str(cols[xxx]).rjust(EXT_COL_WIDTH)'
			logger.info(fmt,
				str(cols[0]).rjust(PROJECT_COL_WIDTH), 
				str(cols[1]).rjust(LINES_COL_WIDTH), 
				str(cols[2]).rjust(PERCENT_COL_WIDTH), 
				str(cols[3]).rjust(EXT_COL_WIDTH), 
				str(cols[4]).rjust(EXT_COL_WIDTH),
				str(cols[5]).rjust(EXT_COL_WIDTH),
				str(cols[6]).rjust(EXT_COL_WIDTH),
				str(cols[7]).rjust(EXT_COL_WIDTH),
				str(cols[8]).rjust(EXT_COL_WIDTH),
				str(cols[9]).rjust(EXT_COL_WIDTH),
				str(cols[10]).rjust(EXT_COL_WIDTH),
				str(cols[11]).rjust(EXT_COL_WIDTH),
				str(cols[12]).rjust(EXT_COL_WIDTH),
				str(cols[13]).rjust(EXT_COL_WIDTH),
				str(cols[14]).rjust(EXT_COL_WIDTH),
				str(cols[15]).rjust(EXT_COL_WIDTH),
				str(cols[16]).rjust(EXT_COL_WIDTH),
				str(cols[17]).rjust(EXT_COL_WIDTH),
				str(cols[18]).rjust(EXT_COL_WIDTH),
				str(cols[19]).rjust(EXT_COL_WIDTH),
				str(cols[20]).rjust(EXT_COL_WIDTH),
				str(cols[21]).rjust(EXT_COL_WIDTH),
				str(cols[22]).rjust(EXT_COL_WIDTH),
				str(cols[23]).rjust(EXT_COL_WIDTH),
				str(cols[24]).rjust(EXT_COL_WIDTH),
				str(cols[25]).rjust(EXT_COL_WIDTH))
		# 一列样式，即所有预定义的ext合并起来显示一列
		elif style == self.OUTPUT_STYLE_COLUMN:
			fmt += '    %s'

			# 最后的others列
			fmt += '%s'

			logger.info(fmt,
				str(cols[0]).rjust(PROJECT_COL_WIDTH), 
				str(cols[1]).rjust(LINES_COL_WIDTH), 
				str(cols[2]).rjust(PERCENT_COL_WIDTH), 
				str(cols[3]).ljust(EXT_COL_WIDTH * 10), 
				str(cols[4]).rjust(EXT_COL_WIDTH))
		else:
			return

	# 计算final_lines_stat{}中的final lines的总数
	def __sum(self):
		total_lines = 0
		for p in self.__stat:
			# 累计所有项目的final lines
			total_lines += int(self.__stat[p][self.FINAL_LINES_TOTAL])

		return total_lines

	# 格式化打印输出final_lines_stat{}
	# style为'Table'时，中间的ext列，每个ext独立显示一列
	# style为'Column'时，所有的ext合并为一列显示
	def print(self, style=OUTPUT_STYLE_COLUMN):
		# 打印表头
		if style == self.OUTPUT_STYLE_TABLE:
			self.__print_oneline(self.__COLUMNS_TABLE_STYLE, style)
		elif style == self.OUTPUT_STYLE_COLUMN:
			self.__print_oneline(self.__COLUMNS_COLUMN_STYLE, style)
		else:
			return

		# 先统计所有项目的总数，因为要计算百分比
		total_lines = self.__sum()

		# 打印每一行数据
		for p in self.__stat:
			lines_percent = '%.1f' % (self.__stat[p][self.FINAL_LINES_TOTAL] / total_lines * 100)

			# 前三列：project, total lines, percent
			row = [p, self.__stat[p][self.FINAL_LINES_TOTAL], lines_percent]

			# 中间的ext列
			if style == self.OUTPUT_STYLE_TABLE:
				for e in projstat.Project.code_file_ext:
					row += [self.__stat[p][e]]
			elif style == self.OUTPUT_STYLE_COLUMN:
				# 拼接为'.java: 100; .html: 300'的格式
				ext_lines = ''
				for e in projstat.Project.code_file_ext:
					lines = self.__stat[p][e]
					# 不包含代码行数为0的ext
					if lines > 0:
						ext_lines += e + ': ' + str(lines) + '; '
				# 删除尾部的'; '
				ext_lines = ext_lines.strip('; ')
				row += [ext_lines]
			else:
				return

			# 最后的others列
			row += [self.__stat[p][self.FINAL_LINES_OTHERS]]
			self.__print_oneline(row, style)

		# 打印最后的总计行
		logger.info('')
		# 前三列：project, total lines, percent
		last_row = ['total %d projects' % len(self.__stat), total_lines, ' ']

		# 中间的ext列
		if style == self.OUTPUT_STYLE_TABLE:
			for e in projstat.Project.code_file_ext:
				last_row += [' ']
		elif style == self.OUTPUT_STYLE_COLUMN:
			last_row += [' ']
		
		# 最后的others列
		last_row += [' ']
		self.__print_oneline(last_row, style)
		logger.info('')

	# 将final_lines_stat{}写入到文件中
	def write(self, style=OUTPUT_STYLE_TABLE):
		if len(self.__stat) == 0:
			return

		# 构建输出文件名称（位于当前目录下）
		today = datetime.datetime.now().strftime(utils.DATE_FORMAT)
		filename = os.path.join(output_root, 'final_lines_stat_%s.txt' % today)

		logger.info('writing to %s', filename)
		with open(filename, 'w', encoding='utf-8') as f:
			# 写入表头
			if style == self.OUTPUT_STYLE_TABLE:
				headers = self.prepare_to_write(['til'] + self.__COLUMNS_TABLE_STYLE)
			elif style == self.OUTPUT_STYLE_COLUMN:
				headers = self.prepare_to_write(['til'] + self.__COLUMNS_COLUMN_STYLE)
			f.write(headers)

			# 先统计所有项目的总数，因为要计算百分比
			total_lines = self.__sum()

			for p in self.__stat:
				# 打印每一行数据
				lines_percent = '%.1f' % (self.__stat[p][self.FINAL_LINES_TOTAL] / total_lines * 100)

				# 前四列：date, project, total lines, percent
				row = [today, p, self.__stat[p][self.FINAL_LINES_TOTAL], lines_percent]

				# 中间的ext列
				if style == self.OUTPUT_STYLE_TABLE:
					for e in projstat.Project.code_file_ext:
						row += [self.__stat[p][e]]
				elif style == self.OUTPUT_STYLE_COLUMN:
					# 拼接为'.java: 100; .html: 300'的格式
					ext_lines = ''
					for e in projstat.Project.code_file_ext:
						lines = self.__stat[p][e]
						# 不包含代码行数为0的ext
						if lines > 0:
							ext_lines += e + ': ' + str(lines) + '; '
					# 删除尾部的'; '
					ext_lines.strip('; ')
					row += [ext_lines]
				else:
					return

				# 最后的others列
				row += [self.__stat[p][self.FINAL_LINES_OTHERS]]

				line = self.prepare_to_write(row)
				f.write(line)

	# 绘制条形图，X轴是projct，Y轴是final lines
	def draw(self):
		# 调用父类的方法
		super().draw(self.__stat, self.FINAL_LINES_TOTAL)

# 获取一个命令行参数的value
def get_pv(pv):
	v = pv.split(SEP_CMD_PV)
	if len(v) > 1:
		# 对于Mac，命令行参数的末尾会带一个'\r'
		return v[1].strip('\r')
	else:
		return ''

# 获取命令行参数
def get_cmd_params():
	logger.info('cmd: %s', sys.argv)

	# usage提示信息中，各命令行参数的value
	cmd_param = {
		P_PROJECT: '<group>' + SEP_CMD_PROJ + '<project>',
		P_UPDATE_CODES: '',
		P_CREATE_LOG: '',
		P_SINCE: '<yyyy-mm-dd>',
		P_BEFORE: '<yyyy-mm-dd>',
		P_ORIGINAL_AUTHOR: '',
		P_SUBTOTAL: '',
		P_DEBUG: '',
		P_OUTPUT: P_OUTPUT_CONSOLE + '/' + P_OUTPUT_FILE,
		P_STAT_BY_MONTH: '',
		P_STAT_TYPE: P_STAT_TYPE_COMMITS + '/' + P_STAT_TYPE_FINAL_LINES,
		P_CHART: '',
		P_SKIPPED_FILES: '',
		P_NOT_UTF8_FILES: '',
		P_ERROR_FILES: ''
	}

	# 构造usage提示信息
	usage = 'Usage: python ' + sys.argv[0]
	for p in cmd_param:
		if cmd_param[p] != '':
			usage += ' [' + p + SEP_CMD_PV + cmd_param[p] + ']'
		else:
			usage += ' [' + p + ']'

	# 设置各命令行参数的默认值
	cmd_pv = {
		P_PROJECT: '',
		P_UPDATE_CODES: False,
		P_CREATE_LOG: False,
		P_SINCE: '',
		P_BEFORE: '',
		P_ORIGINAL_AUTHOR: False,
		P_SUBTOTAL: False,
		P_DEBUG: False,
		P_OUTPUT: P_OUTPUT_CONSOLE,
		P_STAT_BY_MONTH: False,
		P_STAT_TYPE: '',
		P_CHART: False,
		P_SKIPPED_FILES: False,
		P_NOT_UTF8_FILES: False,
		P_ERROR_FILES: True
	}

	group = ''
	proj = ''
	since = ''
	before = ''
	stat_type = ''
	i = 0
	for a in sys.argv:
		# 跳过第一个参数，即脚本名称自身
		if i == 0:
			i += 1
			continue

		if P_STAT_TYPE in a:
			stat_type = get_pv(a)
			if stat_type == '':
				logger.error('value of %s is null', P_STAT_TYPE)
				logger.error(usage)
				exit()
			elif not (stat_type in [P_STAT_TYPE_COMMITS, P_STAT_TYPE_FINAL_LINES]):
				logger.error('%s format: %s', P_STAT_TYPE, cmd_param[P_STAT_TYPE])
				exit()
			cmd_pv[P_STAT_TYPE] = stat_type
		elif P_PROJECT in a:
			project = get_pv(a)
			if project == '':
				logger.error('value of %s is null', P_PROJECT)
				logger.error(usage)
				exit()
			elif not (SEP_CMD_PROJ in project):
				logger.error('%s format: %s', P_PROJECT, cmd_param[P_PROJECT])
				exit()
			else:
				group = project.split(SEP_CMD_PROJ)[0]
				proj = project.split(SEP_CMD_PROJ)[1]
				if group == '' or proj == '':
					logger.error('%s: group or project is null', a)
					exit()
			cmd_pv[P_PROJECT] = project
		elif P_UPDATE_CODES == a:
			cmd_pv[P_UPDATE_CODES] = True
		elif P_CREATE_LOG == a:
			cmd_pv[P_CREATE_LOG] = True
		elif P_SINCE in a:
			since = get_pv(a)
		elif P_BEFORE in a:
			before = get_pv(a)
		elif P_ORIGINAL_AUTHOR == a:
			cmd_pv[P_ORIGINAL_AUTHOR] = True
		elif P_SUBTOTAL == a:
			cmd_pv[P_SUBTOTAL] = True
		elif P_DEBUG == a:
			cmd_pv[P_DEBUG] = True
		elif P_OUTPUT in a:
			output = get_pv(a)
			if output == '':
				logger.error('value of %s is null', P_OUTPUT)
				logger.error(usage)
				exit()
			elif not (output in [P_OUTPUT_CONSOLE, P_OUTPUT_FILE]):
				logger.error('%s format: %s', P_OUTPUT, cmd_param[P_OUTPUT])
				exit()
			cmd_pv[P_OUTPUT] = output
		elif P_STAT_BY_MONTH == a:
			cmd_pv[P_STAT_BY_MONTH] = True
		elif P_CHART == a:
			cmd_pv[P_CHART] = True
		elif P_SKIPPED_FILES == a:
			cmd_pv[P_SKIPPED_FILES] = True
		elif P_NOT_UTF8_FILES == a:
			cmd_pv[P_NOT_UTF8_FILES] = True
		elif P_ERROR_FILES == a:
			cmd_pv[P_ERROR_FILES] = True
		else:
			logger.error('%s is invalid', a)
			logger.error(usage)
			exit()

	if stat_type == '':
		logger.error('%s is missed', P_STAT_TYPE)
		logger.info(usage)
		exit()

	# 统计commits时，才需要有since、before参数
	if stat_type == P_STAT_TYPE_COMMITS:
		if since == '' and before == '':
			logger.error('%s or %s is missed', P_SINCE, P_BEFORE)
			logger.info(usage)
			exit()

		if not (since == '') and not utils.is_valid_date(since):
			logger.error('value of %s is not a valid date. format: yyyy-mm-dd', P_SINCE)
			logger.info(usage)
			exit()
		if not (before == '') and not utils.is_valid_date(before):
			logger.error('value of %s is not a valid date. format: yyyy-mm-dd', P_BEFORE)
			logger.info(usage)
			exit()

		# 对日期格式进行标准化
		since = utils.normalize_date(since)
		before = utils.normalize_date(before)

		if not (since == '') and not (before == '') and before <= since:
			logger.error('value of %s must > %s', P_BEFORE, P_SINCE)
			logger.info(usage)
			exit()

		cmd_pv[P_SINCE] = since
		cmd_pv[P_BEFORE] = before

	# 如果需要更新代码，则必须重新生成log文件，此时忽略命令行参数
	if cmd_pv[P_UPDATE_CODES]:
		cmd_pv[P_CREATE_LOG] = True

	# 打印命令行参数值
	for pv in cmd_pv:
		logger.info('%s: %s', pv, cmd_pv[pv])
	logger.info('')

	return cmd_pv

# 入口类
class CodeStat(object):
	def __init__(self, cmd_pv):
		self.__pv = cmd_pv
		
		if cmd_pv[P_OUTPUT] == P_OUTPUT_FILE:
			# 如果output目录不存在， 则先创建目录
			if not os.path.exists(output_root):
				os.mkdir(output_root)

		# 获得待处理的project列表
		self.__proj_list = self.__generate_proj_list()

		if cmd_pv[P_STAT_TYPE] == P_STAT_TYPE_COMMITS:
			# 初始化***Month对象
			self.__proj_stat_month = ProjStatMonth('proj_stat', cmd_pv[P_SINCE], cmd_pv[P_BEFORE], cmd_pv[P_STAT_BY_MONTH])
			self.__proj_author_stat_month = ProjAuthorStatMonth('proj_author_stat', cmd_pv[P_SINCE], cmd_pv[P_BEFORE], cmd_pv[P_STAT_BY_MONTH])
			self.__author_stat_month = AuthorStatMonth('author_stat', cmd_pv[P_SINCE], cmd_pv[P_BEFORE], cmd_pv[P_STAT_BY_MONTH])

			# 生成月份列表
			self.__month_list = self.__generate_month_list()

			# 初始化不规范的author清单
			self.__abnormal_authors = {}
		elif cmd_pv[P_STAT_TYPE] == P_STAT_TYPE_FINAL_LINES:
			# 初始化统计对象
			self.__final_lines_stat = FinalLinesStat()

			# 初始化跳过的文件清单、非utf8编码格式的文件清单、读取错误的文件清单
			self.__skipped_files = {}
			self.__not_utf8_files = {}
			self.__error_files = {}

	# 生成月份列表
	def __generate_month_list(self):
		whole_since = self.__pv[P_SINCE]
		whole_before = self.__pv[P_BEFORE]

		since_before = {}
		# 如果按月统计，则拆分月份列表
		if self.__pv[P_STAT_BY_MONTH]:
			# 截止到今天的下一个月
			max_before = utils.get_next_month(datetime.datetime.now().strftime(utils.DATE_FORMAT))
			logger.debug('max before: %s', max_before)

			# 获得起始日期
			since = whole_since
			# 获得下一个月的日期
			next_month = utils.get_next_month(since)
			# 将字符串转换为日期进行比较
			while datetime.datetime.strptime(next_month, utils.DATE_FORMAT) < datetime.datetime.strptime(whole_before, utils.DATE_FORMAT):
				# 截止到当前日期的下一个月
				logger.debug('next month: %s, max month: %s', next_month, max_before)
				if next_month >= max_before:
					logger.debug('max before occured')
					break

				# 添加到列表中
				since_before[since] = next_month
				since = next_month
				next_month = utils.get_next_month(since)

			# 将最后一个月加入到列表中
			since_before[since] = whole_before
			logger.debug(since_before)
		else:
			since_before[whole_since] = whole_before

		return since_before

	# 获得待处理的project列表
	def __generate_proj_list(self):
		cmd_proj = self.__pv[P_PROJECT]
		proj_list = {}

		# 如果命令行参数中指定了project，则只统计这个project
		if cmd_proj != '':
			group = cmd_proj.split(SEP_CMD_PROJ)[0]
			proj = cmd_proj.split(SEP_CMD_PROJ)[1]
			# 添加到待处理的列表中
			proj_list[group] = [proj]
		# 否则，将整个git_proj添加到待处理列表中
		else:
			proj_list = config.git_proj

		return proj_list

	# 获取用户输入的菜单序号及二级参数值
	def __get_input(self, x):
		# 截取出序号及二级参数值
		x_arr = x.split(SEP_MENU)
		menu_no = x_arr[0]
		param_value = ''
		if len(x_arr) > 1:
			param_value = x_arr[1]
		
		return menu_no, param_value

	# 处理commits和added lines
	def __process_commits(self):
		logger.info('processing commits and added lines...')

		n = 1
		total_sb = len(self.__month_list)
		for sb in self.__month_list:
			since = sb
			before = self.__month_list[sb]
			logger.info('%s %s', ('processing [since, before]: ' + since + ', ' + before).ljust(70), (str(n) + '/' + str(total_sb)).rjust(10))

			# 初始化***Stat对象
			proj_stat = ProjStat()
			proj_author_stat = ProjAuthorStat(self.__pv[P_SUBTOTAL])
			author_stat = AuthorStat()

			# 连续生成多个月的统计结果时，只有第一个月时才更新代码（假如命令行参数指定了要更新代码），后面的不再重复更新代码
			update_codes = self.__pv[P_UPDATE_CODES]
			if update_codes:
				if n >= 2:
					update_codes = False	

			# 循环处理proj_list{}中的每一个project
			for group in self.__proj_list:
				logger.info('processing group: %s', group)
				num = 1
				total = len(self.__proj_list[group])
				for proj in self.__proj_list[group]:
					logger.info('%s %s', ('processing project: ' + proj).ljust(70), (str(num) + '/' + str(total)).rjust(10))

					# 统计该项目的added lines和commits
					project = projstat.Project(config.git_host, group, proj)
					project.set_update_codes_need(update_codes)
					project.set_create_log_needed(self.__pv[P_CREATE_LOG])
					project.set_original_author(self.__pv[P_ORIGINAL_AUTHOR])

					if project.stat_commits(since, before):
						proj_stat.add(project)
						proj_author_stat.add(project)
						author_stat.add_sum(project)

						# 添加到abnormal_authors{}中
						the_authors = project.get_abnormal_authors()
						for a in the_authors:
							if a in self.__abnormal_authors:
								# 取出已经添加的commit时间
								last_datetime = self.__abnormal_authors[a][1]
								# 如果这次的时间更新，则更新时间
								the_datetime = the_authors[a][1]
								if the_datetime > last_datetime:
									self.__abnormal_authors[a][1] = the_datetime
									self.__abnormal_authors[a][2] = the_authors[a][2]
									self.__abnormal_authors[a][3] = the_authors[a][3]
							else:
								self.__abnormal_authors[a] = [the_authors[a][0], the_authors[a][1], the_authors[a][2], the_authors[a][3]]

					num += 1
				logger.info('')

			# 输出未变更的项目清单（仅当未指定--project命令行参数时）
			if self.__pv[P_PROJECT] == '':
				logger.info('projects not changed:')
				for group in config.git_proj:
					for proj in config.git_proj[group]:
						if proj in config.proj_merge:
							new_proj = config.proj_merge[proj]
						else:
							new_proj = proj
						if not (new_proj in proj_stat.get_stat()):
							logger.info(proj)
				logger.info('')

			# 将这次since-before周期内的统计结果保存到***_month{}中
			self.__proj_stat_month.add(since, before, proj_stat)
			self.__proj_author_stat_month.add(since, before, proj_author_stat)
			self.__author_stat_month.add(since, before, author_stat)

			# 将统计结果打印到标准输出终端上
			if self.__pv[P_OUTPUT] == P_OUTPUT_CONSOLE:
				logger.info('since=%s, before=%s', since, before)
				# 格式化打印proj_stat{}
				l1, c1 = proj_stat.print()
				# 格式化打印proj_author_stat{}
				proj_author_stat.add_proj_stat(proj_stat)
				l2, c2 = proj_author_stat.print()
				# 格式化打印author_stat{}
				l3, c3 = author_stat.print()

				# 如果三个矩阵统计数据不一致，则打印警告信息
				if [l2, c2] != [l1, c1] or [l3, c3] != [l2, c2]:
					logger.warn('')
					logger.warn('total number in 3 tables is not equal. ')

			n += 1

		# 输出不规范的author清单
		logger.info('abnormal authors:')
		logger.info('%s%s%s' % ('abnormal'.ljust(50), 'normal'.ljust(30), 'last commit'))
		for a in self.__abnormal_authors:
			normal_a = self.__abnormal_authors[a][0]
			last_commit = self.__abnormal_authors[a][1] + ', ' + self.__abnormal_authors[a][2] + ', ' + self.__abnormal_authors[a][3]
			logger.info('%s%s%s' % (a.ljust(50), normal_a.ljust(30), last_commit))
		logger.info('')

		# 将统计结果输出到文件中
		if self.__pv[P_OUTPUT] == P_OUTPUT_FILE:
			self.__proj_stat_month.write()
			self.__proj_author_stat_month.write()
			self.__author_stat_month.write()

	# 绘制commits和added lines的图表
	def __draw_commits(self):
		# 根据键盘输入，绘制图表
		INDEX_TYPE_LINES = 1
		INDEX_TYPE_COMMITS = 2
		proj = ''
		month = ''
		author = ''

		if self.__pv[P_STAT_BY_MONTH]:
			while True:			
				# 打印菜单
				print('\nSelect the menu:\n' + 
				'11: draw [project, added lines] for one month\n' + 
				'12: draw [project, commits] for one month\n' + 
				'13: draw [month, added lines] for one project\n' + 
				'14: draw [month, commits] for one project\n' + 
				'21: draw [author, added lines] for one month\n' + 
				'22: draw [author, commits] for one month\n' +
				'23: draw [month, added lines] for one author\n' +
				'24: draw [month, commits] for one author\n' + 
				'31: draw [author, added lines] for one project and one month\n' + 
				'32: draw [author, commits] for one project and one month\n' +
				'41: show month list\n' +
				'42' + SEP_MENU + 'month: set month\n' +
				'51: show project list\n' +
				'52' + SEP_MENU + 'project: set project\n' +
				'61: show author list\n' +
				'62' + SEP_MENU + 'author: set author\n' +
				'0: quit')

				# 获得键盘输入
				x = input('> ')

				# 截取出序号及二级参数值
				menu_no, param_value = self.__get_input(x)

				if menu_no == '0':
					break
				elif menu_no == '41':
					# 打印month列表
					for m in self.__month_list:
						print(m + SEP_STAT_MONTH_KEY + self.__month_list[m])
				elif menu_no == '42':
					if param_value == '':
						print('month is missed')
						continue
					# 二级参数值是month
					month = param_value
					print('month is set to ' + month)
				elif menu_no == '51':
					# 打印project列表
					for g in self.__proj_list:
						for p in self.__proj_list[g]:
							print(p)
				elif menu_no == '52':
					if param_value == '':
						print('project is missed')
						continue
					# 二级参数值是project
					proj = param_value
					print('project is set to ' + proj)
				elif menu_no == '61':
					# 打印author列表
					for a in self.__author_stat_month.get_author_list():
						print(a)
				elif menu_no == '62':
					if param_value == '':
						print('author is missed')
						continue
					# 二级参数值是author
					author = param_value
					print('author is set to ' + author)
				elif menu_no in ['11', '12', '21', '22']:
					if month == '':
						print('month is not set')
						continue
					
					print('current month: ' + month)
					if menu_no == '11':
						self.__proj_stat_month.draw_proj(INDEX_TYPE_LINES, month)
					elif menu_no == '12':
						self.__proj_stat_month.draw_proj(INDEX_TYPE_COMMITS, month)
					elif menu_no == '21':
						self.__author_stat_month.draw_author(INDEX_TYPE_LINES, month)
					elif menu_no == '22':
						self.__author_stat_month.draw_author(INDEX_TYPE_COMMITS, month)
				elif menu_no in ['13', '14']:
					if proj == '':
						print('project is not set')
						continue
					
					print('current project: ' + proj)
					if menu_no == '13':
						self.__proj_stat_month.draw_month(INDEX_TYPE_LINES, proj)
					elif menu_no == '14':
						self.__proj_stat_month.draw_month(INDEX_TYPE_COMMITS, proj)
				elif menu_no in ['23', '24']:
					if author == '':
						print('author is not set')
						continue
					
					print('current author: ' + author)
					if menu_no == '23':
						self.__author_stat_month.draw_month(INDEX_TYPE_LINES, author)
					elif menu_no == '24':
						self.__author_stat_month.draw_month(INDEX_TYPE_COMMITS, author)
				elif menu_no in ['31', '32']:
					if proj == '':
						print('project is not set')
						continue
					
					if month == '':
						print('month is not set')
						continue
					
					print('current project: ' + proj + ', month: ' + month)
					if menu_no == '31':
						self.__proj_author_stat_month.draw_author(INDEX_TYPE_LINES, proj, month)
					elif menu_no == '32':
						self.__proj_author_stat_month.draw_author(INDEX_TYPE_COMMITS, proj, month)
		else:
			while True:
				# 打印菜单
				print('\nSelect the menu:\n' + 
				'11: draw [project, added lines]\n' + 
				'12: draw [project, commits]\n' + 
				'21: draw [author, added lines]\n' + 
				'22: draw [author, commits]\n' + 
				'31: draw [author, added lines] for one project\n' + 
				'32: draw [author, commits] for one project\n' +
				'51: show project list\n' +
				'52' + SEP_MENU + 'project: set project\n' +
				'0: quit')

				# 获得键盘输入
				x = input('> ')

				# 截取出序号及二级参数值
				menu_no, param_value = self.__get_input(x)

				if menu_no == '0':
					break
				elif menu_no == '51':
					# 打印project列表
					for g in self.__proj_list:
						for p in self.__proj_list[g]:
							print(p)
				elif menu_no == '52':
					if param_value == '':
						print('project is missed')
						continue
					# 二级参数值是project
					proj = param_value
					print('project is set to ' + proj)
				elif menu_no == '11':
					self.__proj_stat_month.draw_proj(INDEX_TYPE_LINES)
				elif menu_no == '12':
					self.__proj_stat_month.draw_proj(INDEX_TYPE_COMMITS)
				elif menu_no == '21':
					self.__author_stat_month.draw_author(INDEX_TYPE_LINES)
				elif menu_no == '22':
					self.__author_stat_month.draw_author(INDEX_TYPE_COMMITS)
				elif menu_no in ['31', '32']:
					if proj == '':
						print('project is not set')
						continue
					
					print('current project: ' + proj)
					if menu_no == '31':
						self.__proj_author_stat_month.draw_author(INDEX_TYPE_LINES, proj)
					elif menu_no == '32':
						self.__proj_author_stat_month.draw_author(INDEX_TYPE_COMMITS, proj)

	# 将proj的src_files{}添加到dest_files{}中
	def __add_files(self, proj, dest_files, src_files):
		for f in src_files:
			dest_files[f] = [proj, src_files[f]]

	# 获得files{}中filename的最大长度
	def __get_max_file_len(self, files):
		max_len = 0
		for f in files:
			if len(f) > max_len:
				max_len = len(f)
		max_len += 5
		return max_len

	# 输出文件清单
	def __print_files(self, files):
		max_file_len = self.__get_max_file_len(files)
		if max_file_len > 150:
			max_file_len = 150
		logger.info('%s%s' % ('file'.ljust(max_file_len), 'reason'))
		for f in files:
			fname = utils.fit_filname(f, 150)
			reason = files[f]
			logger.info('%s%s' % (fname.ljust(max_file_len), reason))
		logger.info('')

	# 处理final lines
	def __process_final_lines(self):
		logger.info('processing final lines...')
		logger.info('dir or file to be skipped: %s', config.skipped_path)
		logger.info('ext to be skipped: %s', config.skipped_file_ext)

		# 循环处理proj_list{}中的每一个project
		for group in self.__proj_list:
			logger.info('processing group: %s', group)
			num = 1
			total = len(self.__proj_list[group])
			for proj in self.__proj_list[group]:
				logger.info('%s %s', ('processing project: ' + proj).ljust(70), (str(num) + '/' + str(total)).rjust(10))

				# 统计该项目的final lines
				project = projstat.Project(config.git_host, group, proj)
				project.set_update_codes_need(self.__pv[P_UPDATE_CODES])
				project.stat_final_lines()
				self.__final_lines_stat.add(project)

				# 添加到skipped_file{}中
				self.__skipped_files.update(project.get_skipped_files())

				# 添加到not_utf8_files{}中
				self.__not_utf8_files.update(project.get_not_utf8_files())
				
				# 添加到error_files{}中
				self.__error_files.update(project.get_error_files())

				num += 1
			logger.info('')

		# 输出跳过的文件清单
		if self.__pv[P_SKIPPED_FILES]:
			logger.info('skipped files:')
			self.__print_files(self.__skipped_files)

		# 输出非utf8编码的文件清单
		if self.__pv[P_NOT_UTF8_FILES]:
			logger.info('not utf-8 files:')
			self.__print_files(self.__not_utf8_files)

		# 输出读取错误的文件清单
		if self.__pv[P_ERROR_FILES]:
			logger.info('error files:')
			self.__print_files(self.__error_files)

		if self.__pv[P_OUTPUT] == P_OUTPUT_CONSOLE:
			# 格式化打印final_lines_stat{}
			self.__final_lines_stat.print()

		# 将统计结果输出到文件中
		if self.__pv[P_OUTPUT] == P_OUTPUT_FILE:
			self.__final_lines_stat.write()

	# 绘制final lines的图表
	def __draw_final_lines(self):
		# 根据键盘输入，绘制图表
		while True:
			# 打印菜单
			print('\nSelect the menu:\n' + 
			'1: draw [project, final lines]\n' + 
			'0: quit')

			# 获得键盘输入
			menu_no = input('> ')

			if menu_no == '0':
				break
			elif menu_no == '1':
				self.__final_lines_stat.draw()

	# 入口函数
	def process(self):
		# 处理added lines和commits
		if self.__pv[P_STAT_TYPE] == P_STAT_TYPE_COMMITS:
			self.__process_commits()
			if self.__pv[P_CHART]:
				self.__draw_commits()
		# 处理final lines
		elif self.__pv[P_STAT_TYPE] == P_STAT_TYPE_FINAL_LINES:
			self.__process_final_lines()
			if self.__pv[P_CHART]:
				self.__draw_final_lines()
	
# 入口函数
def start():
	# 读取命令行参数
	cmd_pv = get_cmd_params()

	# 初始化日志对象
	projstat.Project.logger = logger
	Stat.logger = logger

	# 开始处理
	codestat = CodeStat(cmd_pv)
	codestat.process()

if __name__ == '__main__':
	start()