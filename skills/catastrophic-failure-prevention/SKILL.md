---
name: catastrophic-failure-prevention
description: Prevents destructive filesystem commands, protects project workspaces with local Git time-machine checkpoints, enforces atomic backups before modifying critical configs, and guarantees full root-cause logging.
---

# Catastrophic Failure Prevention & Root-Cause Logging

## 🎯 Objective
- Prevent the AI agent from accidentally deleting, overwriting, or destroying local project repositories.
- Guarantee instant 1-second recovery via local Git checkpoints and offline snapshots.
- Ensure every application failure emits an un-swallowed, actionable Stack Trace for instant Root-Cause Analysis.

---

## 🚫 Destructive Command Prohibition (Non-Negotiable)

1. **No Mass Deletion**:
   You are strictly FORBIDDEN from executing destructive filesystem commands (`rm -rf`, `Remove-Item -Recurse -Force`, `del /s /q`) on:
   - Any directory above the current workspace root
   - Core source folders (`./src`, `./public`, `./backend`, `./frontend`, `./prisma`)
   - The `.git` repository folder

2. **Atomic Pre-Modification Backups**:
   Before modifying or replacing any critical configuration or schema file (`.env`, `package.json`, `tsconfig.json`, `docker-compose.yml`, `schema.prisma`), you MUST create a local backup copy (e.g., `.env.bak`, `package.json.bak`).

3. **Pre-Flight Git Status Check**:
   Before executing major refactors, migrations, or destructive cleanups, run `git status`. If dirty changes exist, commit them (`git commit -m "checkpoint: before refactor"`) so that changes can be reverted instantly via `git reset --hard HEAD` and `git clean -fd`.

---

## 🔬 Root-Cause Logging Invariant

1. **Zero Empty Catch Blocks**:
   Never write empty `catch (err) {}` or generic `catch (e) { console.log("error") }`.
   Every catch block must either:
   - Re-throw the exception after enrichment
   - Or write to `./logs/error.log` with full Stack Trace, ISO Timestamp, and Context Payload.

2. **NestJS Production Root-Cause Filter (`all-exceptions.filter.ts`)**:
```typescript
import { ExceptionFilter, Catch, ArgumentsHost, HttpException, HttpStatus } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const request = ctx.getRequest();

    const status = exception instanceof HttpException
      ? exception.getStatus()
      : HttpStatus.INTERNAL_SERVER_ERROR;

    const errorPayload = {
      timestamp: new Date().toISOString(),
      path: request.url,
      method: request.method,
      status,
      traceId: request.headers['x-request-id'] || 'N/A',
      error: exception instanceof Error ? exception.message : 'Unknown exception',
      stack: exception instanceof Error ? exception.stack : null,
    };

    // 1. Root-Cause Local File Logging
    const logsDir = path.resolve(process.cwd(), 'logs');
    if (!fs.existsSync(logsDir)) fs.mkdirSync(logsDir, { recursive: true });
    fs.appendFileSync(
      path.join(logsDir, 'error.log'),
      JSON.stringify(errorPayload) + '\n',
      'utf8'
    );

    // 2. Safe client response (no internal leak)
    response.status(status).json({
      statusCode: status,
      timestamp: errorPayload.timestamp,
      path: request.url,
      message: status === 500 ? 'Internal Server Error' : errorPayload.error,
    });
  }
}
```

---

## 💾 1-Second Disaster Recovery Commands

If an agent or script ever damages the workspace, execute these instant recovery steps:

```powershell
# 1. Discard all uncommitted modifications in tracked files
git reset --hard HEAD

# 2. Remove all untracked files and accidental directories created by scripts
git clean -fd

# 3. Restore critical configuration from atomic backup
Copy-Item .env.bak .env -Force
```
