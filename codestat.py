# -*- coding: utf-8 -*-

__author__ = 'Jason Zhao <guojiongzhao@139.com>'

import os
import sys
import logging
import datetime
# 需要先安装chardet（执行pip install chardet）
import chardet

import projstat
import config

# git host地址
git_host = config.git_host

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

# 要处理的git项目清单
git_proj = config.git_proj

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
# 日期中年、月、日之间的分隔符，例如：2018-01-01
SEP_DATE = '-'
# 命令行参数中param和value的分隔符，例如：--output=file
SEP_cmd_pv = '='
# output文件中各列之间的分隔符，例如：2018-01-01	2018-02-01	treasury	unknown	23459	25.4	350	25.5
SEP_OUTPUT_FILE_COLUMN = '\t'

# 输出proj_stat{}时的表头列名
metrics = ['added lines', 'lines%', 'commits', 'commits%']
COLUMNS_PROJ_STAT = ['project', 'branch'] + metrics
# 输出proj_author_stat{}时的表头列名
COLUMNS_PROJ_AUTHOR_STAT = ['project', 'branch', 'author'] + metrics
# 输出author_stat{}时的表头列名
COLUMNS_AUTHOR_STAT = ['author'] + metrics
# 输出final_lines_stat{}时的表头列名
FINAL_LINES_TOTAL = projstat.Project.FINAL_LINES_TOTAL
FINAL_LINES_OTHERS = projstat.Project.FINAL_LINES_OTHERS
code_file_ext = projstat.Project.code_file_ext
COLUMNS_FINAL_LINES_STAT = ['project', 'final lines', 'lines%'] + code_file_ext + [FINAL_LINES_OTHERS]

# 日期格式
DATE_FORMAT = '%Y' + SEP_DATE + '%m' + SEP_DATE + '%d'

# 统计基类
class Stat(object):
	# 公共类变量，用于设置所有子类的日志对象
	logger = None

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

# proj_stat{}的统计类
class ProjStat(Stat):
	def __init__(self):
		# __stat{}存储每个项目的统计结果，dict类型，key为project名称，value为统计结果数组[branch, added lines, commits]
		self.__stat = {}
	
	def get_stat(self):
		return self.__stat

	# proj参数类型是Project对象
	def add(self, proj):
		proj_name = proj.get_proj_name()
		self.__stat[proj_name] = proj.get_proj_stat()
	
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
		self.__print_oneline(COLUMNS_PROJ_STAT)

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

# proj_author_stat{}的统计类
class ProjAuthorStat(Stat):
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
		self.__stat[proj_name] = proj.get_author_stat()
	
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
		self.__print_oneline(COLUMNS_PROJ_AUTHOR_STAT, max_author_len)

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

# author_stat{}的统计类
class AuthorStat(Stat):
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
		self.__print_oneline(COLUMNS_AUTHOR_STAT, max_author_len)

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

# ProjStat的月统计类
class ProjStatMonth(StatMonth):
	# 将proj_stat_month{}（即父类中的stat_month{}）写入到文件中
	def write(self):
		if len(self.stat_month) == 0:
			return

		logger.info('writing to %s', self.output_filename)
		with open(self.output_filename, 'w', encoding='utf-8') as f:
			# 写入表头
			line = self.prepare_to_write(['since', 'before'] + COLUMNS_PROJ_STAT)
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

# ProjAuhtorStat的月统计类
class ProjAuthorStatMonth(StatMonth):
	# 将proj_author_stat_month{}（即父类中的stat_month{}）写入到文件中
	def write(self):
		if len(self.stat_month) == 0:
			return
		
		logger.info('writing to %s', self.output_filename)
		with open(self.output_filename, 'w', encoding='utf-8') as f:
			# 写入表头
			line = self.prepare_to_write(['since', 'before'] + COLUMNS_PROJ_AUTHOR_STAT)
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

# AuthorStat的月统计类
class AuthorStatMonth(StatMonth):
	# 将author_stat_month{}（即父类中的stat_month{}）写入到文件中
	def write(self):
		if len(self.stat_month) == 0:
			return

		logger.info('writing to %s', self.output_filename)
		with open(self.output_filename, 'w', encoding='utf-8') as f:
			# 写入表头
			line = self.prepare_to_write(['since', 'before'] + COLUMNS_AUTHOR_STAT)
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

# final_lines_stat{}的统计类
class FinalLinesStat(Stat):
	def __init__(self):
		# __stat{}保存每个项目的final lines统计结果，dict类型，key为project名称，value为final lines的一个dict类型，其中key为扩展名，value为final lines
		self.__stat = {}
	
	def get_stat(self):
		return self.__stat

	# proj参数类型是Project对象
	def add(self, proj):
		proj_name = proj.get_proj_name()
		self.__stat[proj_name] = proj.get_final_lines_stat()

	# 格式化打印输出final_lines_stat{}的一行
	def __print_oneline(self, cols):
		# 设置各列的宽度
		PROJECT_COL_WIDTH = 30
		LINES_COL_WIDTH = 20
		PERCENT_COL_WIDTH = 10
		EXT_COL_WIDTH = 10

		# 头三列：project, total lines, percentage
		fmt = '%s%s%s'
		# 中间的ext列
		for e in code_file_ext:
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

	# 计算final_lines_stat{}中的final lines的总数
	def __sum(self):
		total_lines = 0
		for p in self.__stat:
			# 累计所有项目的final lines
			total_lines += int(self.__stat[p][FINAL_LINES_TOTAL])

		return total_lines

	# 格式化打印输出final_lines_stat{}
	def print(self):
		# 打印表头
		self.__print_oneline(COLUMNS_FINAL_LINES_STAT)

		# 先统计所有项目的总数，因为要计算百分比
		total_lines = self.__sum()

		# 打印每一行数据
		for p in self.__stat:
			lines_percent = '%.1f' % (self.__stat[p][FINAL_LINES_TOTAL] / total_lines * 100)

			# 前三列：project, total lines, percent
			row = [p, self.__stat[p][FINAL_LINES_TOTAL], lines_percent]
			# 中间的ext列
			for e in code_file_ext:
				row += [self.__stat[p][e]]
			# 最后的others列
			row += [self.__stat[p][FINAL_LINES_OTHERS]]
			self.__print_oneline(row)

		# 打印最后的总计行
		logger.info('')
		# 前三列：project, total lines, percent
		last_row = ['total %d projects' % len(self.__stat), total_lines, ' ']
		# 中间的ext列
		for e in code_file_ext:
			last_row += [' ']
		# 最后的others列
		last_row += [' ']
		self.__print_oneline(last_row)
		logger.info('')

	# 将final_lines_stat{}写入到文件中
	def write(self):
		if len(self.__stat) == 0:
			return

		# 构建输出文件名称（位于当前目录下）
		today = datetime.datetime.now().strftime(DATE_FORMAT)
		filename = os.path.join(output_root, 'final_lines_stat_%s.txt' % today)

		logger.info('writing to %s', filename)
		with open(filename, 'w', encoding='utf-8') as f:
			# 写入表头
			line = self.prepare_to_write(['til'] + COLUMNS_FINAL_LINES_STAT)
			f.write(line)

			# 先统计所有项目的总数，因为要计算百分比
			total_lines = self.__sum()

			for p in self.__stat:
				# 打印每一行数据
				lines_percent = '%.1f' % (self.__stat[p][FINAL_LINES_TOTAL] / total_lines * 100)

				# 前四列：date, project, total lines, percent
				row = [today, p, self.__stat[p][FINAL_LINES_TOTAL], lines_percent]
				# 中间的ext列
				for e in code_file_ext:
					row += [self.__stat[p][e]]
				# 最后的others列
				row += [self.__stat[p][FINAL_LINES_OTHERS]]

				line = self.prepare_to_write(row)
				f.write(line)

# 判断一个字符串是否为有效的日期
def is_valid_date(date_str):
	try:
		date = datetime.datetime.strptime(date_str, DATE_FORMAT)
		return True
	except Exception as e:
		return False

# 标准化日期字符串，变为：yyyy-mm-dd
def normalize_date(date_str):
	# 通过日期格式化方法，比较笨
	# 先转换为日期
	date = datetime.datetime.strptime(date_str, DATE_FORMAT)
	# 然后再对日期进行格式化：yyyy-mm-dd
	return date.strftime(DATE_FORMAT)	

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

# 获取一个命令行参数的value
def get_pv(pv):
	v = pv.split(SEP_cmd_pv)
	if len(v) > 1:
		return v[1]
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
		P_STAT_TYPE: P_STAT_TYPE_COMMITS + '/' + P_STAT_TYPE_FINAL_LINES
	}

	# 构造usage提示信息
	usage = 'Usage: python ' + sys.argv[0]
	for p in cmd_param:
		if cmd_param[p] != '':
			usage += ' [' + p + SEP_cmd_pv + cmd_param[p] + ']'
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
		P_STAT_TYPE: ''
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

		if not (since == '') and not is_valid_date(since):
			logger.error('value of %s is not a valid date. format: yyyy-mm-dd', P_SINCE)
			logger.info(usage)
			exit()
		if not (before == '') and not is_valid_date(before):
			logger.error('value of %s is not a valid date. format: yyyy-mm-dd', P_BEFORE)
			logger.info(usage)
			exit()

		# 对日期格式进行标准化
		since = normalize_date(since)
		before = normalize_date(before)

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

# 生成月份列表
def get_month_list(whole_since, whole_before, stat_by_month):
	since_before = {}
	# 如果按月统计，则拆分月份列表
	if stat_by_month:
		# 截止到今天的下一个月
		max_before = get_next_month(datetime.datetime.now().strftime(DATE_FORMAT))
		logger.debug('max before: %s', max_before)

		# 获得起始日期
		since = whole_since
		# 获得下一个月的日期
		next_month = get_next_month(since)
		# 将字符串转换为日期进行比较
		while datetime.datetime.strptime(next_month, DATE_FORMAT) < datetime.datetime.strptime(whole_before, DATE_FORMAT):
			# 截止到当前日期的下一个月
			logger.debug('next month: %s, max month: %s', next_month, max_before)
			if next_month >= max_before:
				logger.debug('max before occured')
				break

			# 添加到列表中
			since_before[since] = next_month
			since = next_month
			next_month = get_next_month(since)

		# 将最后一个月加入到列表中
		since_before[since] = whole_before
		logger.debug(since_before)
	else:
		since_before[whole_since] = whole_before

	return since_before

# 获得待处理的project列表
def get_proj_list(cmd_proj):
	proj_list = {}

	# 如果命令行参数中指定了project，则只统计这个project
	if cmd_proj != '':
		group = cmd_proj.split(SEP_CMD_PROJ)[0]
		proj = cmd_proj.split(SEP_CMD_PROJ)[1]
		# 添加到待处理的列表中
		proj_list[group] = [proj]
	# 否则，将整个git_proj添加到待处理列表中
	else:
		proj_list = git_proj

	return proj_list

# 处理commits和added lines
def process_commits(cmd_pv):
	logger.info('processing commits and added lines...')

	# 初始化***Month对象
	proj_stat_month = ProjStatMonth('proj_stat', cmd_pv[P_SINCE], cmd_pv[P_BEFORE], cmd_pv[P_STAT_BY_MONTH])
	proj_author_stat_month = ProjAuthorStatMonth('proj_author_stat', cmd_pv[P_SINCE], cmd_pv[P_BEFORE], cmd_pv[P_STAT_BY_MONTH])
	author_stat_month = AuthorStatMonth('author', cmd_pv[P_SINCE], cmd_pv[P_BEFORE], cmd_pv[P_STAT_BY_MONTH])

	# 生成月份列表
	since_before = get_month_list(cmd_pv[P_SINCE], cmd_pv[P_BEFORE], cmd_pv[P_STAT_BY_MONTH])

	n = 1
	total_sb = len(since_before)
	for sb in since_before:
		since = sb
		before = since_before[sb]
		logger.info('%s %s', ('processing [since, before]: ' + since + ', ' + before).ljust(70), (str(n) + '/' + str(total_sb)).rjust(10))

		# 初始化***Stat对象
		proj_stat = ProjStat()
		proj_author_stat = ProjAuthorStat(cmd_pv[P_SUBTOTAL])
		author_stat = AuthorStat()

		# 连续生成多个月的统计结果时，只有第一个月时才更新代码（假如命令行参数指定了要更新代码），后面的不再重复更新代码
		update_codes = cmd_pv[P_UPDATE_CODES]
		if update_codes:
			if n >= 2:
				update_codes = False	

		# 获得待处理的project列表
		proj_list = get_proj_list(cmd_pv[P_PROJECT])

		# 循环处理proj_list{}中的每一个project
		for group in proj_list:
			logger.info('processing group: %s', group)
			num = 1
			total = len(proj_list[group])
			for proj in proj_list[group]:
				logger.info('%s %s', ('processing project: ' + proj).ljust(70), (str(num) + '/' + str(total)).rjust(10))

				# 统计该项目的added lines和commits
				project = projstat.Project(git_host, group, proj)
				project.set_update_codes_need(update_codes)
				project.set_create_log_needed(cmd_pv[P_CREATE_LOG])
				project.set_original_author(cmd_pv[P_ORIGINAL_AUTHOR])

				if project.stat_commits(since, before):
					proj_stat.add(project)
					proj_author_stat.add(project)
					author_stat.add_sum(project)

				num += 1
			logger.info('')

		# 输出未变更的项目清单（仅当未指定--project命令行参数时）
		if cmd_pv[P_PROJECT] == '':
			logger.info('projects not changed:')
			for group in git_proj:
				for proj in git_proj[group]:
					if not (proj in proj_stat.get_stat()):
						logger.info(proj)
			logger.info('')

		# 将这次since-before周期内的统计结果保存到***_month{}中
		proj_stat_month.add(since, before, proj_stat)
		proj_author_stat_month.add(since, before, proj_author_stat)
		author_stat_month.add(since, before, author_stat)

		# 将统计结果打印到标准输出终端上
		if cmd_pv[P_OUTPUT] == P_OUTPUT_CONSOLE:
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

	# 将统计结果输出到文件中
	if cmd_pv[P_OUTPUT] == P_OUTPUT_FILE:
		proj_stat_month.write()
		proj_author_stat_month.write()
		author_stat_month.write()

# 处理final lines
def process_final_lines(cmd_pv):
	# 初始化统计对象
	final_lines_stat = FinalLinesStat()

	logger.info('processing final lines...')
	logger.info('dir or file to be skipped: %s', projstat.Project.skipped_path)
	logger.info('ext to be skipped: %s', projstat.Project.skipped_file_ext)

	# 获得待处理的project列表
	proj_list = get_proj_list(cmd_pv[P_PROJECT])

	# 循环处理proj_list{}中的每一个project
	for group in proj_list:
		logger.info('processing group: %s', group)
		num = 1
		total = len(proj_list[group])
		for proj in proj_list[group]:
			logger.info('%s %s', ('processing project: ' + proj).ljust(70), (str(num) + '/' + str(total)).rjust(10))

			# 统计该项目的final lines
			project = projstat.Project(git_host, group, proj)
			project.set_update_codes_need(cmd_pv[P_UPDATE_CODES])
			project.stat_final_lines()
			final_lines_stat.add(project)

			num += 1
		logger.info('')

	if cmd_pv[P_OUTPUT] == P_OUTPUT_CONSOLE:
		# 格式化打印final_lines_stat{}
		final_lines_stat.print()

	# 将统计结果输出到文件中
	if cmd_pv[P_OUTPUT] == P_OUTPUT_FILE:
		final_lines_stat.write()

# 入口函数
def start():
	# 读取命令行参数
	cmd_pv = get_cmd_params()

	# 如果output目录不存在， 则先创建目录
	if not os.path.exists(output_root):
		os.mkdir(output_root)

	# 初始化日志对象
	projstat.Project.logger = logger
	Stat.logger = logger

	# 处理commits和added lines
	if cmd_pv[P_STAT_TYPE] == P_STAT_TYPE_COMMITS:
		process_commits(cmd_pv)
	# 处理final lines
	elif cmd_pv[P_STAT_TYPE] == P_STAT_TYPE_FINAL_LINES:
		process_final_lines(cmd_pv)

if __name__ == '__main__':
	start()