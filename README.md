# QQ空间说说接口

这是一个可以用来访问QQ空间说说详细信息的Python模块，能够为用户解析出有用的信息。

## 用法

首先要通过传入cookies创建一个`Qzone`对象，其次调用它的`emotion_list`方法，可以取得QQ号为`uin`的用户从第`pos`条起的连续`num`条说说（最新的说说为0号）。这个方法的返回值是一个`list`，其中包含若干个`Emotion`对象。

`Emotion`对象表示一条说说，包含以下属性：

- `tid`: 一个能唯一标识说说的字符串；
- `author`: 作者QQ号；
- `nickname`: 作者昵称或备注；
- `ctime`: 说说发布时间，Unix时间戳形式；
- `shortcon`: 说说正文的前面一部分正文；
- `content`: 说说完整正文；
- `pictures`: 一个`list`，其中包含若干个`Media`对象，用来表示说说中的附图和视频，后面会讲到；
- `origin`: 一个`Emotion`对象或`None`，被转发的原说说；
- `location`: 位置信息，是一个dict；
- `source`: 发布说说所用的设备或途径名称；
- `forwardn`: 被转发的次数；
- `like`: 一个`dict`，键为点赞的人的QQ号，值为二元组`(昵称, 头像Picture对象)`。
- `comments`: 一个`list`，其中包含若干个`Comment`对象，后面会讲到；
- `forwards`: 一个`list`，其中包含若干个`Emotion`对象，它们都是对这条说说的转发；

**注意**：Emotion中的一些属性，或一些列表的末端几项可能是`qzone.NotLoaded`，表示它们需要额外发一次请求来加载。调用`load()`方法可以把所有信息都加载出来。

`Comment`对象表示一条评论，包含以下属性：

- `tid`: 一个能在其所属的说说内部唯一标识评论的数字；
- `author`: 作者QQ号；
- `nickname`: 作者昵称或备注；
- `ctime`: 发布时间，Unix时间戳形式；
- `content`: 评论正文；
- `pictures`: 一个`list`，其中包含若干个`Media`对象，后面会讲到。
- `replys`: 一个`list`，其中包含若干个`Comment`对象，是对这条评论的评论（根据QQ空间规则，这些评论的评论的`replys`必为空列表）；

`Media`对象表示一个媒体，包含以下属性或方法：
 - `url`：图片(或视频缩略图)；
 - `type`：媒体类型，为`Video`或`Image`；
 - `video_url`：视频url __（请注意视频URL随cookie失效而失效，要及时下载）__；
 - `open`：会返回一个类似于文件的对象，可以调用这个对象的`read()`方法来读出图片数据；
 - `open_video()`：第一个返回值为类似于文件的对象，可以调用这个对象的`read()`方法读出视频数据；第二个返回值为请求时返回的错误(str型)。

## 特别提供的小工具

`qzone.Qzone(**qzone.cookie_str_to_dict('a=1; b=2; c=3'))`可以从cookie字符串创建`Qzone`对象

`qzone.Qzone(**qzone.get_cookie_from_curl("curl --header 'Host: qzone.qq.com' --header 'User-Agent: ...' --header 'Cookie: a=1; b=2; c=3' 'http://qzone.qq.com/' -O -J -L"))`可以从curl命令（在装了相关插件的浏览器上会很容易取得）中提取出cookie部分，创建`Qzone`对象

不妨试试`print(一个emotion)`？
