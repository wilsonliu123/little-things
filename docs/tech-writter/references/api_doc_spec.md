# API 文檔撰寫規範

## 目錄
1. [端點描述規範](#endpoint)
2. [參數表格規範](#params)
3. [請求/回應範例](#samples)
4. [錯誤碼對照表](#errors)
5. [認證說明](#auth)
6. [版本變更記錄](#changelog)

---

## 1. 端點描述規範 {#endpoint}

每個 API 端點必須包含：

| 項目 | 說明 | 範例 |
|------|------|------|
| HTTP Method | GET/POST/PUT/DELETE/PATCH | `POST` |
| 路徑 | RESTful 風格路徑 | `/api/v1/users/{id}` |
| 簡述 | 一句話描述功能 | 取得指定用戶資料 |
| 詳細說明 | 業務邏輯、前置條件、副作用 | 需要 admin 權限... |
| 狀態標記 | stable / beta / deprecated | `stable` |
| 認證要求 | 是否需要 Token、權限等級 | Bearer Token, role: admin |

### 端點命名規範

```
GET    /api/v1/{resource}          # 列表查詢
GET    /api/v1/{resource}/{id}     # 單筆查詢
POST   /api/v1/{resource}          # 新增
PUT    /api/v1/{resource}/{id}     # 全量更新
PATCH  /api/v1/{resource}/{id}     # 部分更新
DELETE /api/v1/{resource}/{id}     # 刪除
```

---

## 2. 參數表格規範 {#params}

### 請求參數表格格式

| 欄位 | 說明 |
|------|------|
| 參數名稱 | 使用 camelCase 或 snake_case（保持一致） |
| 類型 | string, integer, boolean, array, object, float, date, datetime |
| 必填 | Required / Optional |
| 預設值 | 未傳時的預設值 |
| 約束 | 長度限制、正則、範圍、枚舉值 |
| 說明 | 參數用途描述 |

### 約束描述範例

```
| 參數名稱 | 類型 | 必填 | 約束 | 說明 |
|----------|------|------|------|------|
| username | string | Required | 3-32 chars, ^[a-zA-Z0-9_]+$ | 用戶名稱 |
| age | integer | Optional | 0-150, default: null | 年齡 |
| role | string | Required | enum: ["admin","user","guest"] | 角色 |
| email | string | Required | RFC 5322 format | 電子郵件 |
| tags | array[string] | Optional | max 10 items, each max 50 chars | 標籤列表 |
| metadata | object | Optional | max depth 3, max 50 keys | 自定義元數據 |
```

### 回應參數表格格式

同請求參數，額外包含：
- **巢狀結構**：使用縮排或 `.` 表示法（如 `data.user.name`）
- **分頁資訊**：`total`, `page`, `pageSize`, `hasMore`

---

## 3. 請求/回應範例 {#samples}

每個端點至少提供：
1. **成功請求範例** - 包含完整 headers 和 body
2. **成功回應範例** - 包含 status code 和完整 body
3. **錯誤回應範例** - 至少一個常見錯誤場景

### 範例格式

```
### Request
POST /api/v1/users
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

{
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user"
}

### Response 201 Created
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 12345,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user",
    "createdAt": "2025-01-15T08:30:00Z"
  }
}

### Response 409 Conflict
{
  "code": 40901,
  "message": "Username already exists",
  "details": {
    "field": "username",
    "value": "john_doe"
  }
}
```

### cURL 範例

每個端點提供可直接執行的 cURL 命令：

```bash
curl -X POST https://api.example.com/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user"
  }'
```

---

## 4. 錯誤碼對照表 {#errors}

### 統一錯誤回應格式

```json
{
  "code": 40001,
  "message": "Human-readable error message",
  "details": {}
}
```

### 錯誤碼編碼規則

| 範圍 | 類別 | 說明 |
|------|------|------|
| 0 | 成功 | 請求成功 |
| 400xx | 請求錯誤 | 參數驗證失敗、格式錯誤 |
| 401xx | 認證錯誤 | Token 無效、過期 |
| 403xx | 授權錯誤 | 權限不足 |
| 404xx | 資源不存在 | 找不到指定資源 |
| 409xx | 衝突 | 資源已存在、狀態衝突 |
| 429xx | 限流 | 請求頻率超限 |
| 500xx | 伺服器錯誤 | 內部錯誤 |

---

## 5. 認證說明 {#auth}

文檔應包含：
- 認證方式（Bearer Token / API Key / OAuth2 / Session）
- Token 取得方式和有效期
- 刷新機制
- 權限等級和角色說明
- 各端點所需的最低權限

---

## 6. 版本變更記錄 {#changelog}

### 格式

```
## v2.1.0 (2025-03-15)

### 新增
- POST /api/v1/users/batch - 批量創建用戶

### 變更
- GET /api/v1/users - 新增 `status` 篩選參數

### 棄用
- GET /api/v1/user/{id} - 請改用 /api/v1/users/{id}

### 移除
- DELETE /api/v1/users/purge - 已移除，改用軟刪除

### Breaking Changes
- POST /api/v1/users 回應格式變更：`data.name` → `data.username`
```
