# 圖表撰寫指南

## 目錄
1. [Mermaid 圖表類型](#mermaid)
2. [SVG 動態流程圖](#svg-flow)
3. [數據庫 ER 圖](#er-diagram)
4. [使用場景對照](#usage)

---

## 1. Mermaid 圖表類型 {#mermaid}

### 流程圖 (Flowchart) - 業務邏輯流程

```mermaid
flowchart TD
    A[接收請求] --> B{驗證 Token}
    B -->|有效| C[解析參數]
    B -->|無效| D[返回 401]
    C --> E{參數驗證}
    E -->|通過| F[執行業務邏輯]
    E -->|失敗| G[返回 400]
    F --> H{操作成功?}
    H -->|是| I[返回 200]
    H -->|否| J[返回 500]
```

### 時序圖 (Sequence) - API 調用流程

```mermaid
sequenceDiagram
    participant C as Client
    participant G as Gateway
    participant A as Auth Service
    participant S as Business Service
    participant D as Database

    C->>G: POST /api/v1/orders
    G->>A: 驗證 Token
    A-->>G: Token 有效
    G->>S: 轉發請求
    S->>D: INSERT order
    D-->>S: 返回 order_id
    S-->>G: 201 Created
    G-->>C: 返回訂單資料
```

### 狀態圖 (State) - 資源狀態流轉

```mermaid
stateDiagram-v2
    [*] --> Draft: 創建
    Draft --> Pending: 提交審核
    Pending --> Approved: 審核通過
    Pending --> Rejected: 審核拒絕
    Rejected --> Draft: 重新編輯
    Approved --> Published: 發布
    Published --> Archived: 歸檔
    Archived --> [*]
```

### 類圖 (Class) - 數據模型

```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string email
        +string role
        +datetime createdAt
        +Create()
        +Update()
        +Delete()
    }
    class Order {
        +int id
        +int userId
        +string status
        +float totalAmount
        +Submit()
        +Cancel()
    }
    User "1" --> "*" Order: places
```

---

## 2. SVG 動態流程圖 {#svg-flow}

僅限 HTML 格式文檔使用。用於展示數據流動、請求路徑等。

### 基本動態箭頭模板

```html
<svg width="600" height="200" viewBox="0 0 600 200">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7"
            refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
    </marker>
  </defs>

  <!-- 節點 -->
  <rect x="20" y="70" width="120" height="60" rx="10"
        fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="80" y="105" text-anchor="middle"
        font-family="sans-serif" font-size="14" fill="#1e293b">Client</text>

  <rect x="240" y="70" width="120" height="60" rx="10"
        fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="300" y="105" text-anchor="middle"
        font-family="sans-serif" font-size="14" fill="#1e293b">Server</text>

  <rect x="460" y="70" width="120" height="60" rx="10"
        fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="520" y="105" text-anchor="middle"
        font-family="sans-serif" font-size="14" fill="#1e293b">Database</text>

  <!-- 動態箭頭 -->
  <line x1="140" y1="100" x2="240" y2="100"
        stroke="#2563eb" stroke-width="2" marker-end="url(#arrowhead)"
        stroke-dasharray="10 5">
    <animate attributeName="stroke-dashoffset"
             from="0" to="-20" dur="1s" repeatCount="indefinite"/>
  </line>

  <line x1="360" y1="100" x2="460" y2="100"
        stroke="#2563eb" stroke-width="2" marker-end="url(#arrowhead)"
        stroke-dasharray="10 5">
    <animate attributeName="stroke-dashoffset"
             from="0" to="-20" dur="1s" repeatCount="indefinite"/>
  </line>

  <!-- 標籤 -->
  <text x="190" y="90" text-anchor="middle"
        font-family="sans-serif" font-size="11" fill="#64748b">HTTP Request</text>
  <text x="410" y="90" text-anchor="middle"
        font-family="sans-serif" font-size="11" fill="#64748b">SQL Query</text>
</svg>
```

### 雙向數據流模板

```html
<svg width="600" height="250" viewBox="0 0 600 250">
  <defs>
    <marker id="arrow-right" markerWidth="10" markerHeight="7"
            refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
    </marker>
    <marker id="arrow-left" markerWidth="10" markerHeight="7"
            refX="0" refY="3.5" orient="auto">
      <polygon points="10 0, 0 3.5, 10 7" fill="#22c55e"/>
    </marker>
  </defs>

  <!-- 請求方向（藍色） -->
  <line x1="140" y1="90" x2="240" y2="90"
        stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-right)"
        stroke-dasharray="10 5">
    <animate attributeName="stroke-dashoffset"
             from="0" to="-20" dur="1s" repeatCount="indefinite"/>
  </line>

  <!-- 回應方向（綠色） -->
  <line x1="240" y1="110" x2="140" y2="110"
        stroke="#22c55e" stroke-width="2" marker-end="url(#arrow-left)"
        stroke-dasharray="10 5">
    <animate attributeName="stroke-dashoffset"
             from="0" to="20" dur="1s" repeatCount="indefinite"/>
  </line>
</svg>
```

---

## 3. 數據庫 ER 圖 {#er-diagram}

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        datetime created_at
        datetime updated_at
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int id PK
        int user_id FK
        string status
        float total_amount
        datetime created_at
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        float unit_price
    }
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
    PRODUCT {
        int id PK
        string name
        string description
        float price
        int stock
    }
```

---

## 4. 使用場景對照 {#usage}

| 場景 | 推薦圖表 | 格式支持 |
|------|----------|----------|
| API 請求流程 | Sequence Diagram | HTML, MD |
| 業務邏輯判斷 | Flowchart | HTML, MD |
| 資源狀態流轉 | State Diagram | HTML, MD |
| 數據模型關係 | ER Diagram / Class Diagram | HTML, MD |
| 數據流動方向 | SVG 動態圖 | 僅 HTML |
| 系統架構總覽 | Flowchart + SVG | HTML, MD(靜態) |
| 微服務調用鏈 | Sequence Diagram | HTML, MD |
| 部署架構 | Flowchart (subgraph) | HTML, MD |
