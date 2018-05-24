//index.js

var app = getApp();
var that;
var chatListData = [];

Page({
  data: {
    askWord: '',
    userInfo: {},
    chatList: [],
  },
  onLoad: function () {
    that = this;
    //获取用户信息
    app.getUserInfo(function (userInfo) {
      that.setData({
        userInfo: userInfo
      });
    });
  },
  onReady: function () {
    //问候语
    setTimeout(function () {
      that.addChat('Hi，我是小Q，精通水稻各种知识，欢迎向我提问', 'l');
    }, 1000);
  },
  sendChat: function (e) {

    let word = e.detail.value.ask_word ? e.detail.value.ask_word : e.detail.value;//支持两种提交方式
    that.addChat(word, 'r');
    console.log(word);
    //请求api获取回答
    app.req('post', {
      //'data': { 'info': word },
      'data': { 'search_for': word },
      'success': function (resp) {
        console.log('resp: ', resp);
        that.addChat(resp, 'l');
        if (resp.url) {
          that.addChat(resp.url, 'l');
        }
      },
    });

    //清空输入框
    that.setData({
      askWord: ''
    });
  },
  //新增聊天列表
  addChat: function (word, orientation) {
    let ch = { 'text': word, 'time': new Date().getTime(), 'orientation': orientation };
    chatListData.push(ch);
    that.setData({
      chatList: chatListData
    });
  }
})