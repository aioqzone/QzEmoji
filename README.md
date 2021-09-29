# QzEmoji

Transfer Qzone Emoji to text.

将Qzone表情链接转换为文字.

<div>

<img src="https://img.shields.io/badge/python-3.8%2F3.9-blue">

<a href="https://github.com/JamzumSum/QzEmoji/pulls">
<img src="https://img.shields.io/tokei/lines/github/JamzumSum/QzEmoji?label=rules">
</a>

<a href="https://github.com/JamzumSum/QzEmoji/actions/workflows/python-app.yml">
<img src="https://github.com/JamzumSum/QzEmoji/actions/workflows/python-app.yml/badge.svg">
</a>

</div>

This project is a component of [Qzone2TG][qzone2tg].

## Motivation

Qzone似乎并没有提供表情序号到中文名称的接口. 通过爬虫和观察js代码等等方式也并不能完全获取所有的表情名称. 本仓库试图建立这一转换的查询表.

## Usage

首先通过正则表达式等等方式解析`id`:
~~~ python
>>> from qzemoji import resolve
>>> resolve('http://qzonestyle.gtimg.cn/qzone/em/e400343.gif')
>>> '400343.gif'
~~~

### Python

~~~ python
>>> from qzemoji import query
>>> query('400343.gif')
>>> '🐷'
>>> query(125)
>>> '困'
~~~

#### Specifying Path of Database

给定一个相对路径, 默认在当前目录和包顶级目录(`__init__.py`的父目录)下搜索. 前者应对develop install, 后者应对正常的用户安装. 不支持更改search root, 特殊需求可以使用绝对路径或者修改源码.

在这两个起始位置下, 默认查找的路径是`data/emoji.db`. 通过以下方式修改这个路径:

~~~ python
import qzemoji
query(101, 'tmp/new_download.db')   # specify the path for the first time
query(102)  # the path is saved internally and can be omitted
~~~

#### Update Database

从`0.2`起, 第一次查询前会试图更新数据库.

禁用自动更新:
~~~ python
import qzemoji
qzemoji.DBMgr.enable_auto_update = False
~~~

自动更新每次启动只会运行一次. 提前调用更新以免拖慢您的第一次查询(推荐):
~~~ python
import qzemoji
qzemoji.DBMgr.autoUpdate('data/emoji.db')

# 支持文件大小回调(int->None):
qzemoji.DBMgr.autoUpdate('data/emoji.db', sizebar.update)
~~~

目前从GitHub检查更新. 设置代理:
~~~ python
import qzemoji
qzemoji.DBMgr.proxy = "http://localhost:1234"
~~~

> 使用[AssetsUpdater][updater]获取和下载更新. 其内部使用`requests`, 因此理论上也支持环境变量设置的代理.

### Other Language

下载[emoji.db](https://github.com/JamzumSum/QzEmoji/releases).

使用`sqlite`查询`emoji`表:

~~~ sql
select text from emoji where id=400343;
~~~

## Build Database

~~~ shell
pip install -U yaml
export PYTHONPATH=$(pwd)/src
python script/build.py
~~~

## Contribute

![](https://img.shields.io/github/forks/JamzumSum/QzEmoji?style=social)

本质上这是一个翻译项目. 因此我把它独立出来并希望获得社区的支持. 我们欢迎任何人提交PR, 并将尽快审核.

翻译准则见[Annoucement][principle]

## License

- [MIT](https://github.com/JamzumSum/QzEmoji/blob/main/LICENSE)



[qzone2tg]: https://github.com/JamzumSum/Qzone2TG "Qzone2TG"
[principle]: https://github.com/JamzumSum/QzEmoji/discussions/2 "欢迎分享您的翻译!"
[updater]: https://github.com/JamzumSum/AssetsUpdater "Update assets from network"
