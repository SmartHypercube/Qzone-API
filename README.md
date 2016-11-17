# QQ空间说说接口

这是一个可以用来访问QQ空间说说详细信息的Python模块，能够为用户解析好有用的信息。

## 用法

首先要通过传入cookies创建一个`Qzone`对象，其次调用它的`emotion_list`方法，可以取得QQ号为`uin`的用户从第`pos`条起的连续`num`条说说（最新的说说为0号）。这个方法的返回值是一个`list`，其中包含若干个`Emotion`对象。

`Emotion`对象表示一条说说，包含以下属性：

- `comments`: 一个`list`，其中包含若干个`Comment`对象，后面会讲到；
- `shortcon`: 说说正文的前面一部分正文；
- `content`: 说说完整正文；
- `ctime`: 说说发布时间，Unix时间戳形式；
- `forwardn`: 被转发的次数；
- `location`: 位置信息，是一个dict；
- `nickname`: 作者昵称或备注；
- `pictures`: 一个`list`，其中包含若干个`Picture`对象，后面会讲到；
- `origin`: 一个`Emotion`对象或`None`，被转发的原说说；
- `forwards`: 一个`list`，其中包含若干个`Emotion`对象，它们都是对这条说说的转发；
- `source`: 发布说说所用的设备或途径名称；
- `tid`: 一个能唯一标识说说的字符串；
- `author`: 作者QQ号；
- `like`: 一个`dict`，键为点赞的人的QQ号，值为二元组`(昵称, 头像Picture对象)`。

**注意**：Emotion中的一些属性，或一些列表的末端几项可能是`qzone.NotLoaded`，表示它们需要额外发一次请求来加载。调用`load()`方法可以把所有信息都加载出来。

`Comment`对象表示一条评论，包含以下属性：

- `content`: 评论正文；
- `ctime`: 发布时间，Unix时间戳形式；
- `nickname`: 作者昵称或备注；
- `tid`: 一个能在其所属的说说内部唯一标识评论的数字；
- `author`: 作者QQ号；
- `replys`: 一个`list`，其中包含若干个`Comment`对象，是对这条评论的评论（根据QQ空间规则，这些评论的评论的`replys`必为空列表）；
- `pictures`: 一个`list`，其中包含若干个`Picture`对象，后面会讲到。

`Picture`对象表示一张图片，没什么特别的，它只有一个`open()`方法，会返回一个类似于文件的对象，可以调用这个对象的`read()`方法来读出图片数据。

## 特别提供的小工具

`qzone.Qzone(**qzone.cookie_str_to_dict('a=1; b=2; c=3'))`可以从cookie字符串创建`Qzone`对象

`qzone.Qzone(**qzone.get_cookie_from_curl("curl --header 'Host: qzone.qq.com' --header 'User-Agent: ...' --header 'Cookie: a=1; b=2; c=3' 'http://qzone.qq.com/' -O -J -L"))`可以从curl命令（在装了相关插件的浏览器上会很容易取得）中提取出cookie部分，创建`Qzone`对象

## 意见与建议

作者已经尽量进行了测试，这个模块没有抛出过异常，应该十分稳定。但毕竟QQ空间构造复杂，如果您在使用时遇到了错误，请在issue中描述清楚出错的说说有什么样的特殊性，最好截图，我将会尽力解决。

如果有任何和QQ空间接口相关的建议或探索进展，也请与我联系，我很乐意继续扩充这个项目的功能！
