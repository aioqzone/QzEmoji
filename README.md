# QzEmoji

将Qzone表情链接转换为文字.

[![python](https://img.shields.io/badge/python-3.9%20%7C%203.13-blue)][homepage]
[![Test](https://github.com/aioqzone/QzEmoji/actions/workflows/test.yml/badge.svg)](https://github.com/aioqzone/QzEmoji/blob/beta/.github/workflows/test.yml)
[![rules](https://img.shields.io/endpoint?url=https%3A%2F%2Fghloc.vercel.app%2Fapi%2Faioqzone%2FQzEmoji%2Fbadge%3Ffilter%3Demoji.yml%24&color=green
)](CONTRIBUTING.md)
[![black](https://img.shields.io/badge/code%20style-black-000000)](https://github.com/psf/black)

This project is a component of [Qzone3TG][qzone2tg].

## Motivation

Qzone似乎并没有提供表情序号到中文名称的接口. 通过爬虫和观察js代码等等方式也并不能完全获取所有的表情名称. 本仓库试图建立这一转换的查询表.

## Usage

首先通过正则表达式等等方式解析`id`:

``` python
>>> import qzemoji.utils as qeu
>>> qeu.resolve(url='http://qzonestyle.gtimg.cn/qzone/em/e400343.gif')
400343
>>> qeu.resolve(tag='[em]e400343[/em]')
400343
>>> qeu.resolve('no kwargs specified')
AssertionError
>>> qeu.resolve(tag='[em] e400343[/em]')
ValueError('[em] e400343[/em]')
```

### Query in Python

``` python
>>> import qzemoji as qe        # this will auto update database, so set a proxy in advance.
>>> await qe.query(400343)
'🐷'
```

> [!NOTE]
> 目前，QzEmoji 使用发布在 aioqzone-index 上的数据库。这意味着您可能需要在导入 qzemoji 之前配置代理。
> QzEmoji 将读取 `HTTP_PROXY`, `HTTPS_PROXY`, `WS_PROXY`, `WSS_PROXY`。

#### Auto Update

从`0.2`起, 第一次查询前会试图更新数据库.

禁用自动更新:
``` python
qe.enable_auto_update = False
```

自动更新每次启动只会运行一次. 提前初始化以免拖慢您的第一次查询(推荐):
目前从GitHub检查更新. 您可以按如下方式设置代理:

``` python
>>> await qe.auto_update()
```

#### Customize Your Copy

您可以随意修改`emoji.db`以适应用户的需要. 自定义内容存储在`MyEmoji`表中，与`Emoji`表隔离. 自动更新只会更新`Emoji`表，自定义内容保持不变。自定义内容优先级高于默认（`MyEmoji`优先于`Emoji`）.

~~~ python
>>> qe.set(400343, 'Hello QzEmoji')
>>> qe.query(400343)    # 'Hello QzEmoji' in MyEmoji, '🐷' in Emoji
'Hello QzEmoji'
~~~

#### Export Your Customization

您可以导出您的自定义，从而与他人分享。比如，给此仓库提交PR，从而补充我们的默认表。

``` python
>>> qe.export()
Path('data/emoji.yml')  # default export to data/emoji.yml
```

### Query in SQL

下载[emoji.db](https://github.com/aioqzone/QzEmoji/releases).

使用`sqlite`查询`emoji`表:

|column |description    |
|:-----:|:--------------|
|eid    |Emoji ID       |
|text   |Corresponding text|

~~~ sql
select text from emoji where eid=400343;
~~~

## Build Database

``` shell
# clone and step into this repo
pip install -e .
python script/build.py
```

## Contribute

您可以通过 Python 包提供的 `export` 接口导出完整的数据库，并按[上文](#export-your-customization)所述导出 yml 文件.

See [CONTRIBUTING](CONTRIBUTING.md)

## License

- [MIT](https://github.com/aioqzone/QzEmoji/blob/async/LICENSE)


[qzone2tg]: https://github.com/aioqzone/Qzone2TG "Forward Qzone feeds to telegram"
[principle]: https://github.com/aioqzone/QzEmoji/discussions/2 "欢迎分享!"
[homepage]: https://github.com/aioqzone/QzEmoji "Translate Qzone Emoji link to text."
