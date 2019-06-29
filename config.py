# -*- coding: utf-8 -*-

'配置文件'

__author__ = "Jason Zhao <guojiongzhao@139.com>"

# git host地址
git_host = 'git.xuelebj.net'

# 要处理的git项目清单，dict类型，key为group名称，value为project名称
git_proj = {
	'xueledata': [
		'treasury-old', # 2018-04-01 modify
		'treasury-new', # 2018-04-01 add
		'tracking-data-monitor',
		'testkit',
		'dataservice-teach',
		'question-data',
		'dataservice-competition',
		'dataservice-work',
		'dataservice-cwork',
		'dataservice-misc',
		'dataservice-login',
		'dataservice-tfb',
		'dataservice-common',
		'dataservice-exam',
		'content-analyzer',
		'XETL',
		'excercise',
		'kpdiag-stream',
		'act-stream',
		'XStreamCompute',
		'dataservice-kpdiag',
		'exam-flatten',
		'kpdiag-cache',
		'exam-stream',
		'recommend-data',
		'x-storm-kafka',
		'bigdata-xudf',
		'kpdiag-algorithm-kit',
		'xa-server',
		'kpdiag-stat-stream',
		'recommend',
		'xa-sdk-java',
		'log2json',
		'content-extract',
		'dataservice-teach-study',
		'dataservice-interactions',
		'x-zuul',
		'x-eureka',
		'dataservice-cloudteach',
		'KnowledgeGraph',
		'dataservice-users',
		'dataservice-orgs',
		'x-log-monitor',
		'dataservice-questions',
		'dataservice-clouddisk',
		'XAlert',
		'x-mongo-hadoop',
		'dataservice-actions',
		'dataservice-resources',
		'XScheduler',
		'XFlume',
		'question-sim',
		'question-difficulty-estimation',  # 2018-03-06 add
		'kp-estimation',  # 2018-03-06 add
		'bigscreen',  # 2018-03-09 add
		'bigscreen-api',  # 2018-03-09 add
		'kpdiag-autotest',  # 2018-03-12 add
		'modules-cas',  # 2018-04-10 add
		'bigscreen-xstream-autotest',  # 2018-05-09 add
		'dataservice-evaluation',  # 2018-06-06 add
		'metadata-compare',  # 2018-05-16 add
		'edu-data-batch',  # 2018-08-02 add
		'tracking-data-etl',  # 2018-08-04 add
		'dataservice-circle',  # 2018-08-04 add
		'bdmc-web',   # 2018-10-08 add
		'bdmc-api',   # 2018-10-17 add
		'treasury-utils',  # 2018-11-23 add
		'dataservice-trot',  # 2018-12-03 add
		'trot-batch',  # 2018-12-14 add
		'x-datax',  # 2019-03-04 add
		'treasury-pack',  # 2019-03-08 add
		'test-helper',  # 2019-03-08 add
		'treasury-bi',  # 2019-04-11 add
		'dataservice-bi',  # 2019-04-15 add
		'resource-score',  # 2019-06-03 add
	],
	'xueleapp': [
		'classroom',
		'smartclass-web-autotest',
		'smartclass-api',
		'py-convert-manager',
		'ppt-converter',
		'call-convert-machine-mfc',
		'winwisdom',  # 2018-04-12 add
		# 'collaborative-editing' # 2018-04-20 add
		'exam-omr',  # 2018-07-13 add
		'coplan-web',  # 2018-07-17 add
		'coplan-controller',  # 2018-07-17 add
		'coplan-api',  # 2018-07-17 add
		'exam-omr-api',  # 2018-07-27 add
		'x-daisydiff',  # 2018-08-02 add
		'exam-omr-dispatch',  # 2018-09-27 add
		'face-recognition',  # 2018-10-18 add
		'fr-web',  # 2018-10-23 add
		'ocr-old',  # 2018-10-29 add，2019-02-20 modify
		'ocr-new',  # 2019-02-02 add
		'py-utils',  # 2018-11-20 add
		'x-xdocreport',  # 2019-03-06 add
		'classroom-rc-wxmp',  # 2019-04-25 add
		'classroom-rc',  # 2019-04-25 add
		'question-recognition',  # 2019-04-28 add
		'x-cv',  # 2019-05-07 add
	]
}

# 统计final lines时要跳过的文件扩展名
skipped_file_ext = [
	# IDEA项目文件
	".iml", 
	# VC项目文件
	".vcxproj", 
	# 备份文件
	".bak", 
	# 二进制文件
	".jar", ".zip", ".gz", ".7z", ".tar", ".war", ".class", ".exe", ".dat", ".swp", ".keystore", ".jks", ".aps",
	".png", ".gif", ".jpg", ".bmp", ".ico", ".cur", ".mp3", ".wav", ".m4a", ".flac", ".wma", ".wmv", ".mp4", ".flv",
	".otf", ".eot", ".ttf", ".woff", ".swf", ".crc", ".psd", ".ogg",
	".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pages", ".numbers", ".key", ".vsd",
	".pyc", ".ipynb",
	".dll", ".lib", ".bin", ".pak",
	# 其它数据文件
	".out", ".txt", ".log", ".dic", ".csv", 
	".avro"]

# 统计final lines时要跳过的目录或文件
skipped_path = [
	# git目录
	'.git', 
	# svn目录
	'.svn', 	
	# IDEA目录
	'.idea', 
	# VSCode目录
	'.vscode',
	# Python目录
	'__pycache__',
	# Mac
	'.DS_Store',
	# Java编译后输出
	'target',
	# bigscreen需要过滤的第三方js等文件, 2018-04-10 added
	'coordinate.js', 'echarts-all.js', 'UK_geo.json', 'flipclock.js',
	# C++ Debug目录
	'Debug',

	# winwisdom的一些目录（全目录）
	'./git/winwisdom/third_party',

	# coplan-web的一些目录（全目录）
	'./git/coplan-web/app/third-lib',
	'./git/coplan-web/mobile/third-lib',
]

# 特殊author email的映射，dict结构，key为不规范的email，value为规范的email
author_mapping = {
	'xl123456': 'wenhuanhuan@xueleyun.com',
	'wenhuanhuan@task1-sandbox.xuele.net': 'wenhuanhuan@xueleyun.com',

	'chongfq@qq.com': 'chongfaqin@xueleyun.com',
	'pengxiuzhao@task1-sandbox.xuele.net': 'pengxiuzhao@xueleyun.com',
	'18210507492@126.com': 'qindongliang@xueleyun.com',

	'15901206690@139.com': 'lvnan@xueleyun.com',
	'lvnan@xuele.com': 'lvnan@xueleyun.com',
	'lvnan@task1-sandbox.xuele.net': 'lvnan@xueleyun.com',

	'王子美@home': 'wangzimei@xueleyun.com',
	'王子美': 'wangzimei@xueleyun.com',

	'hwwweb@163.com': 'huoweiwei@xueleyun.com',
	'bigdata@task1-sandbox.xuele.net': 'bigdata',
	'yue': 'guiqiuyue@xueleyun.com',
	'lianxiaolei@hqyxjy.com': 'lianxiaolei@xueleyun.com',

	'476143560@qqcom': 'chenliang@xueleyun.com',
	'chenliang@xuele.com': 'chenliang@xueleyun.com',

	'zhouming@task1-sandbox.xuele.net': 'zhouming@xueleyun.com',
	'zhouming@SANDBOX-HADOOP-04.xuele.net': 'zhouming@xueleyun.com',

	'12345678': 'zoutao@xueleyun.com',
	'ixciel@ixciel.com': 'malvcheng@xueleyun.com',

	'Xl123456': 'yangchao@xueleyun.com',
	'332938647@qq.com': 'yangchao@xueleyun.com',

	'837755145@qq.com': 'liushuang@xueleyun.com',

	'zhuxu@SANDBOX-HADOOP-04.xuele.net': 'zhuxu@xueleyun.com',

	'wenhuanhuan@SANDBOX-HADOOP-04.xuele.net': 'wenhuanhuan@xueleyun.com',

	'liuyuqing@SANDBOX-HADOOP-04.xuele.net': 'liuyuqing@xueleyun.com',

	'jiangchongluck@163.com': 'jiangchong@xueleyun.com',

    'leihailong@task1-sandbox.xuele.net': 'leihailong@xueleyun.com',
    'leihailong@SANDBOX-HADOOP-04.xuele.net': 'leihailong@xueleyun.com',
    'leihailong@xueleun.com': 'leihailong@xueleyun.com',

	'http://git.xuelebj.net': 'wanggaoliang@xueleyun.com',
    'guojiongzhao@139.com': 'zhaoguojiong@xueleyun.com',
    'yuanwei@hzlzedu.com.cn': 'yuanwei@xueleyun.com',
}

# 某月、某个项目需要剔除的added lines
proj_stat_fix = {
	'2018-03-01':{
		'question-difficulty-estimation': {
			'chongfaqin@xueleyun.com': -561210 # data文件
		},
		'kp-estimation': {
			'chongfaqin@xueleyun.com': -2091003 # data文件
		},
		'treasury-new': {
			'zhuxu@xueleyun.com': -353586 # 从treasury-old迁移而来
		},
		'bigscreen': {
			'chenliang@xueleyun.com': -61383 # 第三方js（coordinate.js: 3482；echarts-all.js: 49884；UK_geo.json: 5232；flipclock.js: 2785）
		}
	},
	'2018-04-01':{
		'content-analyzer': {
			'chongfaqin@xueleyun.com': -276029 # dic文件
		}
	},
	'2018-05-01':{
		'content-analyzer': {
			'lianxiaolei@xueleyun.com': -992611 # dic文件
		},
		'winwisdom': {
			'zoutao@xueleyun.com': -43611 # 第三方DuiLib代码
		}
	},
	'2018-06-01':{
		'kp-estimation': {
			'lianxiaolei@xueleyun.com': -520438 # dic、txt等data文件
		}
	},
	'2018-07-01':{
		'coplan-web': {
			'yangchao@xueleyun.com': -127285 # 第三方库ueditor的第一次上传（后面的修改没有剔除）
		}
	},
	'2018-08-01':{
		'coplan-web': {
			'yangchao@xueleyun.com': -151642 # 第三方库的第一次上传（后面的修改没有剔除）、打包编译后的dist下的文件
		}
	},
	'2018-10-01':{
		'bdmc-web': {
			'yangwenhai@xueleyun.com': -8451, # package-lock.json、地图数据（*.json）等
			'yangchao@xueleyun.com': -7276, # yarn.lock
			'liufangfang@xueleyun.com': -10079, # package-lock.json等
			'weipengda@xueleyun.com': -9987, # 地图数据（*.json）、第三方js等
		},
		'fr-web': {
			'jiangchong@xueleyun.com': -10194 # package-lock.json
		},
	},
	'2018-11-01':{
		'ocr': {
			'lianxiaolei@xueleyun.com': -15955 # *.ipynb
		}
	},
	'2018-12-01':{
		'winwisdom': {
			'yangwenhai@xueleyun.com': -17567, # 实际上是王国涛提交的代码（因为本机git user配置成了杨文海）
		}
	},
	'2019-01-01':{
		'winwisdom': {
			'yangwenhai@xueleyun.com': -10788, # 实际上是王国涛提交的代码（因为本机git user配置成了杨文海）
		}
	},
	'2019-02-01':{
		'ocr-old': {
			'lianxiaolei@xueleyun.com': -11972, # *.ipynb
		},
		'ocr-new': {
			'lianxiaolei@xueleyun.com': -21103, # 从ocr-old迁移而来的初始代码
		},
		'winwisdom': {
			'yangwenhai@xueleyun.com': -6255, # 实际上是王国涛提交的代码（因为本机git user配置成了杨文海）
		}
	},
	'2019-03-01':{
		'x-xdocreport': {
			'lvnan@xueleyun.com': -207240, # 开源项目的初始代码
		},
	},
	'2019-05-01':{
		'question-recognition': {
			'qindongliang@xueleyun.com': -64524, # 临时的前端代码（bootstrap、jquery等）
		},
		'classroom-rc': {
			'yuanwei@xueleyun.com': -8952 # package-lock.json
		},
	},
}

# 需要合并的项目（因为新旧项目迁移）
# value数组中的第二个元素：如果是1，则表示新项目；如果是0，则表示旧项目（不统计final lines）
proj_merge = {
	'treasury-old': ['treasury', 0],
	'treasury-new': ['treasury', 1],
	
	'ocr-old': ['ocr', 0],
	'ocr-new': ['ocr', 1],
}