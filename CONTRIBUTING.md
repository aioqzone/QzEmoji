## Contribute

[![](https://img.shields.io/github/forks/aioqzone/QzEmoji?style=social&label=opening%20fork)](https://github.com/aioqzone/QzEmoji/pulls)
[![rules](https://img.shields.io/tokei/lines/github/aioqzone/QzEmoji?label=rules)](CONTRIBUTING.md)

### 提交PR

1. 使用`qe.export()`导出您的`emoji.yml`。
2. 在GitHub web上打开公有的[emoji.yml](../data/emoji.yml)
3. 点击修改图标，替换为您的文件内容。
4. 提交您的修改。

### 如何解决冲突

当同一`eid`有多个不同翻译时，符合下列原则的优先：

- Unicode emoji 优于文字, 如译为🐷要比译为文字更传神:D
- 如果多个平台上的 emoji 存在语义冲突，以 IOS emoji 为准
