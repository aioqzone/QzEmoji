# QzEmoji

Transfer Qzone Emoji to text.

将Qzone表情链接转换为文字.

<div>

<img src="https://img.shields.io/badge/python-3.8%2F3.9-blue">

<a href="https://github.com/JamzumSum/QzEmoji/pulls">
<img src="https://img.shields.io/tokei/lines/github/JamzumSum/QzEmoji?label=database">
</a>

</div>

This project is a component of [Qzone2TG][qzone2tg].

## Motivation

Qzone似乎并没有提供表情序号到中文名称的接口. 通过爬虫和观察js代码等等方式也并不能完全获取所有的表情名称. 本仓库试图建立这一转换的查询表.

## Usage

首先通过正则表达式等等方式解析`id`:
~~~ python
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

### Other Language

下载`data/emoji.db`. (之后会发布到release)

使用`sqlite`查询`emoji`表.

## Contribute

![](https://img.shields.io/github/forks/JamzumSum/QzEmoji?style=social)

本质上这是一个翻译项目. 因此我把它独立出来并希望获得社区的支持. 我们欢迎任何人提交PR, 并将尽快审核.

翻译准则见[Annoucement][principle]

## License

- [MIT](https://github.com/JamzumSum/QzEmoji/blob/main/LICENSE)



[qzone2tg]: https://github.com/JamzumSum/Qzone2TG "Qzone2TG"
[principle]: https://github.com/JamzumSum/QzEmoji/discussions/2 "欢迎分享您的翻译!"
