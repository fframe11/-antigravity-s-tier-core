# คู่มือการตั้งค่า API Keys ส่วนตัว (Hand-Holding API Keys Setup Guide)

> **นโยบายความปลอดภัย Zero-Exposure Security Policy**:  
> Repository นี้ **ไม่มีการบันทึกหรือแนบ API Key หรือ Personal Access Token (PAT) ส่วนตัวของผู้สร้าง (`ffram`)** มาในระบบแม้แต่อันเดียว เพื่อป้องกันปัญหา Credential Leakage และให้เป็นไปตามมาตรฐาน DevSecOps ระดับ Enterprise  
> ผู้ใช้งานทุกคนจะต้องใช้ Key บัญชีของตนเองในการเชื่อมต่อบริการภายนอก

---

## 📍 ตำแหน่งไฟล์สำหรับใส่ API Keys (Configuration Path)

ไฟล์ที่ใช้เก็บการตั้งค่า MCP Server ทั้งหมดจะอยู่ที่:
- **Windows**: `C:\Users\<ชื่อผู้ใช้ของคุณ>\.gemini\config\mcp_config.json` (หรือพิมพ์ `%USERPROFILE%\.gemini\config\mcp_config.json` ใน Run / File Explorer)
- **macOS / Linux**: `~/.gemini/config/mcp_config.json`

---

## 🛠️ รายการบริการที่ต้องใช้ API Key และวิธีนำไปใส่แบบจับมือทำ

### 1. GitHub MCP (`github`) — *จำเป็นสำหรับฟังก์ชัน Git & PRs*
ใช้สำหรับให้ Antigravity สามารถสร้าง Branch, ค้นหาโค้ดข้าม Repos, เปิด Pull Request, ตรวจสอบ CI status, และ Merge PR ได้อัตโนมัติ

#### วิธีขอ Token:
1. ล็อกอินเข้า GitHub แล้วเปิดลิงก์: [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. กดปุ่ม **"Generate new token"** -> เลือก **"Generate new token (classic)"**
3. ในช่อง **Note**: พิมพ์ชื่อจำง่าย เช่น `Antigravity-Agent-Token`
4. ในช่อง **Expiration**: แนะนำเลือก `90 days` หรือ `No expiration` (หากใช้ส่วนตัว)
5. ในหัวข้อ **Select scopes**: ติ๊กถูกที่ช่อง:
   - [x] `repo` (Full control of private repositories)
   - [x] `workflow` (Update GitHub Action workflows)
   - [x] `read:org` (Read org and team membership)
6. เลื่อนลงล่างสุดแล้วกดปุ่มสีเขียว **"Generate token"**
7. **คัดลอก Token ทันที** (จะมีรูปแบบขึ้นต้นด้วย `ghp_...`) *ระวัง: จะเห็นรหัสนี้แค่ครั้งเดียวเท่านั้น*

#### วิธีนำไปใส่ใน `mcp_config.json`:
ค้นหาหัวข้อ `"github"` แล้วนำ Token ไปวางในฟิลด์ `"GITHUB_PERSONAL_ACCESS_TOKEN"`:
```json
"github": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-github"
  ],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_วางTokenของคุณตรงนี้"
  }
}
```

---

### 2. Unsplash MCP (`unsplash`) — *ทางเลือก / Optional*
ใช้สำหรับค้นหาภาพถ่ายความละเอียดสูงระดับโปรดักชันสำหรับ Web & UI เพื่อป้องกันปัญหา AI Placeholder Slop  
*(หมายเหตุ: หากไม่ใส่ Key ระบบจะสลับไปใช้คลังภาพ CDN คัดสรรระดับพรีเมียมที่มีมาให้ในตัวโดยอัตโนมัติ)*

#### วิธีขอ Access Key:
1. ไปที่เว็บไซต์ Unsplash Developers: [https://unsplash.com/developers](https://unsplash.com/developers)
2. กดปุ่ม **"Register as a developer"** หรือล็อกอินเข้าสู่ระบบ
3. กดแท็บ **"Your apps"** -> กดปุ่ม **"New Application"**
4. ยอมรับข้อกำหนดการใช้งาน แล้วตั้งชื่อแอป เช่น `Antigravity-UI-Search`
5. เลื่อนลงมาที่หัวข้อ **Keys** แล้วคัดลอก **"Access Key"**

#### วิธีนำไปใส่ใน `mcp_config.json`:
ค้นหาหัวข้อ `"unsplash"` แล้วนำ Access Key ไปวางในฟิลด์ `"UNSPLASH_ACCESS_KEY"`:
```json
"unsplash": {
  "command": "python",
  "args": [
    "~/.gemini/mcp-servers/unsplash-mcp/server.py"
  ],
  "env": {
    "UNSPLASH_ACCESS_KEY": "วาง_Unsplash_Access_Key_ของคุณตรงนี้"
  }
}
```

---

### 3. Google Image Search MCP (`google-image-search`) — *ทางเลือก / Optional*
ใช้สำหรับค้นหาภาพไดอะแกรมสถาปัตยกรรม โลโก้แบรนด์ และภาพอ้างอิงบนเว็บ

#### วิธีขอ API Key และ CX (Search Engine ID):
1. **ขอ API Key**:
   - ไปที่ Google Cloud Console: [https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
   - ค้นหาและเปิดใช้งาน **"Custom Search API"**
   - กดปุ่ม **"Create Credentials"** -> เลือก **"API key"** แล้วคัดลอก Key ไว้
2. **ขอ Search Engine ID (CX)**:
   - ไปที่ Programmable Search Engine: [https://programmablesearchengine.google.com/](https://programmablesearchengine.google.com/)
   - กด **"Add"** เพื่อสร้าง Search Engine ใหม่ -> ในช่อง "What to search?" เลือก "Search the entire web" -> ตั้งชื่อแล้วกด Create
   - ในหน้า Overview ให้คัดลอกรหัส **"Search engine ID"** (CX ID)

#### วิธีนำไปใส่ใน `mcp_config.json`:
ค้นหาหัวข้อ `"google-image-search"` แล้วกรอกข้อมูลทั้ง 2 ช่อง:
```json
"google-image-search": {
  "command": "python",
  "args": [
    "~/.gemini/mcp-servers/google-image-search-mcp/server.py"
  ],
  "env": {
    "GOOGLE_SEARCH_API_KEY": "วาง_Google_API_Key_ตรงนี้",
    "GOOGLE_SEARCH_CX": "วาง_Search_Engine_ID_ตรงนี้"
  }
}
```

---

### 4. Notion MCP (`notion`) & Canva MCP (`canva`) — *ล็อกอินผ่านเว็บอัตโนมัติ (Zero Key)*
ทั้ง **Notion** และ **Canva** เชื่อมต่อผ่านโปรโตคอลมาตรฐาน **MCP-Remote OAuth**:
- **ไม่ต้องกรอก Key ใดๆ ในไฟล์ Config**
- เมื่อใดก็ตามที่ Antigravity เรียกใช้ฟังก์ชันของ Notion หรือ Canva เป็นครั้งแรก ระบบจะเด้งเปิดหน้าต่างเบราว์เซอร์ให้คุณกด **"Login & Authorize Access"** อัตโนมัติในคลิกเดียว

---

## 🧪 การทดสอบยืนยันหลังใส่ Key

หลังจากแก้ไขและบันทึกไฟล์ `mcp_config.json` แล้ว ให้เปิด Antigravity ขึ้นมา แล้วพิมพ์ทดสอบได้ทันที:
1. **ทดสอบ GitHub**: `ให้ดึงรายการ repository ล่าสุดของฉันผ่าน github mcp หน่อย`
2. **ทดสอบ Unsplash**: `ค้นหารูปภาพดาต้าเซิร์ฟเวอร์ความละเอียดสูงผ่าน unsplash ให้ดู 2 รูป`
3. **ทดสอบความพร้อมทั้งหมด**: `ตรวจสอบสถานะของ mcp tools ทั้งหมดว่าเชื่อมต่อสมบูรณ์หรือไม่`
