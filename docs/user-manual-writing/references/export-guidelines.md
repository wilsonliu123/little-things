# HTML / PDF 導出指引

這份參考檔專門處理手冊在 HTML / PDF 導出時最容易踩到的兩類問題：

1. 字體亂碼或方框問號
2. 截圖沒有出現在最終文件裡

## 一、先理解兩個常見根因

### 1. 方框問號通常不是「PDF 不支援中文」

更常見的原因是：

- 把中文 UI 文案包在反引號裡，導致它進入 code font
- 匯出時套用的 code font 沒有對應的 CJK 字形
- 手冊裡混入 emoji 或特殊符號，但匯出時沒有對應字體

### 2. 截圖消失通常不是「PDF 不支援圖片」

更常見的原因是：

- Markdown 圖片語法 `![alt](path)` 在轉 HTML 時沒有被正確轉成 `<img>`
- HTML 裡用了相對路徑，但匯出時 base path 不對
- 產圖檔案存在，但 HTML / PDF 根本沒有引用到它

## 二、寫作時就先避免的坑

### 中文 UI 名稱不要放進反引號

對中文 UI 文案，優先用粗體，不要用反引號。

推薦：

- **記憶控制台**
- **重新載入 Skills**
- **顯示記憶**

不要這樣寫：

- `記憶控制台`
- `重新載入 Skills`

反引號優先留給這些內容：

- ASCII 路徑，例如 `/mcp`
- URL
- 檔名
- API 名稱
- 變數名 / 環境變數

### PDF 版避免 emoji

若最終目標是 PDF，盡量不要使用 emoji 或特殊圖示字元。它們最容易在不同機器上變成方框問號。

推薦：

- 使用「聊天工作台」而不是 💬 Chat
- 使用「技能庫」而不是 🧠 Skills

## 三、導出 HTML / PDF 的正確方式

如果最終要輸出 HTML 或 PDF，優先使用：

- `scripts/render_manual.py`

不要直接依賴一個你尚未確認是否支援圖片語法的隨機 Markdown 轉換器。

這個腳本除了處理圖片，還會做一個保底修正：

- 如果反引號裡含有中文，會把它當成 UI 標籤渲染，改用正文字體，而不是硬套 code font

這不能取代你把來源稿寫乾淨，但能避免最常見的方框問號問題。

### 推薦命令

只輸出 HTML：

```bash
python3 scripts/render_manual.py /path/to/manual.md --html /path/to/manual.html
```

同時輸出 HTML 和 PDF：

```bash
python3 scripts/render_manual.py /path/to/manual.md \
  --html /path/to/manual.html \
  --pdf /path/to/manual.pdf
```

如果你想在最終交付前嚴格攔截風險，使用：

```bash
python3 scripts/render_manual.py /path/to/manual.md \
  --html /path/to/manual.html \
  --pdf /path/to/manual.pdf \
  --fail-on-warning
```

## 四、導出前檢查什麼

至少檢查以下四件事：

1. Markdown 裡每一張圖片的檔案都存在
2. 生成的 HTML 真的含有 `<img>` 標籤
3. 生成腳本沒有報 emoji / 中文 code span 警告
4. 最終 PDF 至少抽查 2 到 3 個頁面，確認：
   - 沒有方框問號
   - 截圖真的出現
   - 沒有殘留 `!圖片說明` 這種文字

## 五、交付前最低驗收標準

如果你要把 HTML / PDF 當正式交付，最低要達成：

- 中文正文正常顯示
- 中文 UI 名稱不出現方框問號
- 每張重要截圖都能看到
- 沒有把 Markdown 圖片語法原文漏到成品裡
