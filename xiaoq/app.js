//app.js
//参考https://github.com/HowName/smart-robot
App({
  onLaunch: function () {
    //调用API从本地缓存中获取数据
    var logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)
  },
  getUserInfo: function (cb) {
    var that = this
    if (this.globalData.userInfo) {
      typeof cb == "function" && cb(this.globalData.userInfo)
    } else {
      //调用登录接口
      wx.login({
        success: function () {
          wx.getUserInfo({
            success: function (res) {
              that.globalData.userInfo = res.userInfo
              typeof cb == "function" && cb(that.globalData.userInfo)
            }
          })
        }
      })
    }
  },
  globalData: {
    userInfo: null
  },
  // Request function
  req: function (method, arg) {
    // let url = 'http://www.tuling123.com/openapi/api', data = { 'key': '651d654e65444901b80aaeb0b0917040' }, dataType = 'json';
    console.log(arg.data);
    let url = 'http://192.168.116.5:8000/search_api/', dataType = 'json', data = '';
    let header = { 'content-type': 'application/x-www-form-urlencoded' };
    if (arg.data) {
      // data = Object.assign(data, arg.data);
      data = arg.data;
    }
    if (arg.header) {
      header = Object.assign(header, arg.header);
    }
    if (arg.dataType) {
      dataType = arg.dataType;
    }

    let request = {
      method: method.toUpperCase(),
      url: url,
      data: data,
      dataType: dataType,
      header: header,
      success: function (resp) {
        console.log('response content:', resp.data);

        let data = resp.data;

        typeof arg.success == "function" && arg.success(data);
      },
      fail: function () {
        wx.showToast({
          title: '请求失败,请稍后再试',
          icon: 'success',
          duration: 2000
        });

        typeof arg.fail == "function" && arg.fail();
      },
      complete: function () {
        typeof arg.complete == "function" && arg.complete();
      }
    };
    console.log(request);
    wx.request(request);
  },
})