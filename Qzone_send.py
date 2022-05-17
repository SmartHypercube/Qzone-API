import requests

import qzone

import config


class Qzone_send(qzone.Qzone):

    def emotion_send(self, emotion):
        url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_publish_v6"
        headers = config.publish_headers
        g_tk = super().gtk
        cookie = qzone.qzone_cookie

        msg_dict={
            "qzreferrer":"https://user.qzone.qq.com/"+config.account,
            "syn_tweet_verson":1,

        }

