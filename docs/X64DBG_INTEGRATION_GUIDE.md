# x64dbg MCP Integration & Offline Transport Safety Guide

เอกสารฉบับนี้จัดทำขึ้นเพื่อบันทึกสาเหตุปัญหาการแครชของ Antigravity IDE จากการเชื่อมต่อ Debugger Transport และขั้นตอนการเปิดใช้งาน `x64dbg-mcp` อย่างถูกต้องเมื่อต้องการใช้งานจริง

---

## 1. สาเหตุของปัญหาที่เคยเกิดขึ้น (Root Cause & Post-Mortem)

1. **In-Process Lifecycle**: ปลั๊กอิน `x64dbg-MCP-Server.dp64` ทำงานแบบ In-Process ภายในโปรแกรม `x64dbg.exe` (x64) เท่านั้น ไม่ได้เป็น Background Service อิสระ พอร์ต `9094` จึงจะเปิดทำงานก็ต่อเมื่อเปิดโปรแกรม x64dbg ขึ้นมา
2. **Fatal Transport Refusal**: หากมีการลงทะเบียนบล็อก `"x64dbg"` ไว้ใน `mcp_config.json` ผ่าน SSE (`http://localhost:9094/sse`) แต่ไม่ได้เปิดโปรแกรม x64dbg ไว้ เมื่อ Antigravity IDE เริ่มต้นหรือเรียก Agent ระบบจะพยายาม Handshake ทันที ส่งผลให้ Windows ปฏิเสธการเชื่อมต่อ:
   ```text
   connectex: No connection could be made because the target machine actively refused it.
   Agent execution terminated due to error.
   ```
3. **การแก้ไขในระดับ Core Template**: เพื่อป้องกันปัญหานี้ไม่ให้เกิดกับผู้ใช้งานทั่วไป บล็อก `x64dbg` จึงถูกถอดออกจากเทมเพลตเริ่มต้น (`mcp/mcp_config.template.json`) เรียบร้อยแล้ว

---

## 2. ขั้นตอนการเปิดใช้งาน x64dbg MCP อย่างปลอดภัย (On-Demand Activation)

หากต้องการทำ Reverse Engineering หรือ Agentic Native Debugging ร่วมกับ x64dbg ให้ปฏิบัติตามลำดับ 4 ขั้นตอนนี้เสมอ:

### ขั้นตอนที่ 1: เปิดโปรแกรม x64dbg ขึ้นมาก่อนเสมอ
เปิดโปรแกรม `x64dbg.exe` (x64) และตรวจสอบว่าเมนู `Plugins > x64dbg-MCP Server` เริ่มทำงานเรียบร้อยแล้ว

### ขั้นตอนที่ 2: ตรวจสอบสถานะ Port 9094
เปิด PowerShell และตรวจสอบว่าพอร์ต 9094 เปิดรับการเชื่อมต่อแล้ว:
```powershell
Get-NetTCPConnection -LocalPort 9094 -ErrorAction SilentlyContinue
```
*(ต้องพบสถานะ `Listen` ก่อนดำเนินการต่อ)*

### ขั้นตอนที่ 3: เพิ่มคอนฟิกใน `~/.gemini/config/mcp_config.json`
เพิ่มบล็อกคอนฟิกเข้าไปในส่วน `"mcpServers"`:
```json
"x64dbg": {
    "serverUrl": "http://localhost:9094/sse",
    "headers": {
        "Authorization": "Bearer f7c8a4d2e1b39058ac46d7e2f1839b20"
    }
}
```

### ขั้นตอนที่ 4: ปลดคอนฟิกออกเมื่อใช้งานเสร็จ
เมื่อเสร็จสิ้นการดีบั๊กหรือต้องการปิดโปรแกรม x64dbg ให้นำบล็อก `"x64dbg"` ออกจาก `mcp_config.json` ทุกครั้ง เพื่อป้องกันไม่ให้ Antigravity IDE แครชในเซสชันถัดไปที่ไม่ได้เปิดตัวดีบั๊กเกอร์

---

## 3. กฎการทำงานอัตโนมัติของ AI (Autonomous Zero-Manual-Auth Rule)

ในระบบ Antigravity S-Tier มีการกำหนดกฎเหล็กเพื่อไม่ให้เป็นภาระแก่ผู้ใช้งาน (`Autonomous Lifecycle Invariant`):
* **AI ตรวจสอบและเชื่อมต่อเอง**: เมื่อผู้ใช้สั่งให้ดีบั๊กหรือวิเคราะห์ไบนารี AI จะรันคำสั่งเช็คพอร์ต `9094` และเขียนบล็อกคอนฟิก `x64dbg` พร้อม Token เข้า `mcp_config.json` ให้โดยอัตโนมัติ (ผู้ใช้ไม่ต้องเปิดไฟล์แก้ไขเอง)
* **AI คืนสถานะอัตโนมัติ**: เมื่อเสร็จสิ้นกระบวนการวิเคราะห์ AI จะทำการลบคอนฟิก `x64dbg` ออกจาก `mcp_config.json` ทันที เพื่อรับประกันว่าในการเปิด Antigravity IDE ครั้งถัดไปจะไม่มีข้อผิดพลาดการเชื่อมต่อหลงเหลืออยู่
