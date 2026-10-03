# Git Push Policy: 4-Layer Safety & Verification Architecture

Whenever preparing to push code or update remote repositories:

## Layer 1: Scope & Environment Classification
Prompt the user with the standard intake questions:
1. Scope: "งานที่กำลังทำนี้เป็นงานประเภทใด?"
   - Options: ["งานระดับ Production (ทีม/บริษัท)", "งานตัวเอง (Personal Repo)"]
2. Branch Name: "ชื่อ Branch ที่คุณต้องการ Push ขึ้นไปคืออะไร?"
   - Options: ["กรอกชื่อ Branch ในช่องพิมพ์ข้อความด้านล่าง (Write-in)", "ระบุว่า main หรือ master"]
3. Remote HTTPS URL: "HTTPS URL ของ Repository ปลายทางคืออะไร?"
   - Options: ["กรอก HTTPS URL ในช่องพิมพ์ข้อความด้านล่าง", "เป็นงาน Local เท่านั้น (ไม่มี Remote)"]

## Layer 2: Target Branch Specification
Capture the user's explicit input for the target branch name. Never push to an assumed or default branch without explicit confirmation.

## Layer 3: Remote Repository Verification
Confirm the destination remote repository HTTPS URL to ensure code is delivered to the correct location.

## Layer 4: Critical Intercept Gate (If Target is 'main' or 'master')
If the user selects or inputs `main` or `master`:
1. **NO ONE-CLICK APPROVAL**: Strictly forbid automatic or one-click approval.
2. **MANDATORY TYPED VERIFICATION**: Display the critical alert:
   - *"คุณกำลังสั่ง Push ตรงเข้า Branch หลัก (main/master) คุณแน่ใจหรือไม่ว่าไม่ได้เผลอกด?"*
   - Require the user to type the exact verification phrase: `ยืนยันไม่ได้เผลอ` in the write-in text field.
3. **ABORT ON ANY MISMATCH**: If the input does not match, or if the user cancels, immediately abort the Git push operation.

## Final Approval Gate
Display the synthesized summary (Scope, Branch, Remote URL, Commit count, and Changed files) and obtain final explicit confirmation before running `git push`.
