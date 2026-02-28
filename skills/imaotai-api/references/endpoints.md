# i茅台 API 端点参考

> 注意：端点和参数需根据实际抓包结果补充/校正

## 发送验证码
POST /prod/ct/platformgw/moutai/appService/v2/user/send/code
```json
{"mobile": "手机号", "timestamp": 13位时间戳}
```

## 登录
POST /prod/ct/platformgw/moutai/appService/v2/user/login
```json
{"mobile": "手机号", "vCode": "验证码", "deviceId": "设备ID", "timestamp": 13位时间戳}
```
返回：`{"data": {"token": "...", "userId": "..."}}`

## 获取商品列表
GET /prod/ct/platformgw/moutai/appService/v2/shop/list/available

## 获取门店列表
GET /prod/ct/platformgw/moutai/appService/v2/shop/list
参数：`cityCode`（城市编码）

## 申购（核心接口）
POST /prod/ct/platformgw/moutai/appService/v2/act/reservation
```json
{
  "itemId": "商品ID",
  "itemNum": 1,
  "shopId": "门店ID",
  "timestamp": 13位时间戳
}
```

## 旅行
POST /prod/ct/platformgw/moutai/appService/v2/userAct/travel
```json
{"timestamp": 13位时间戳}
```

## 申购结果查询
GET /prod/ct/platformgw/moutai/appService/v2/act/getActAppoint
