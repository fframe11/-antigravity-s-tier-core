---
name: input-validation-dto
description: Use when implementing input validation, designing DTOs, configuring class-validator pipes, or sanitizing user input in NestJS APIs. Covers validation decorators, custom validators, whitelist stripping, and file upload validation.
---
# Input Validation & DTO Patterns (NestJS)

## When to Use
- Creating or modifying API request DTOs
- Adding validation to new endpoints
- Reviewing input handling for security
- Implementing custom validation logic

## Global Validation Pipe Setup

```typescript
// main.ts — MUST be configured globally
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,              // Strip unknown properties
  forbidNonWhitelisted: true,   // Throw on unknown properties
  transform: true,              // Auto-transform payloads to DTO instances
  transformOptions: {
    enableImplicitConversion: true,
  },
}));
```

### Why Each Option Matters
| Option | Without It | Attack Vector |
|---|---|---|
| `whitelist: true` | Extra fields pass through | Mass assignment (user sends `{ role: "admin" }`) |
| `forbidNonWhitelisted: true` | Unknown fields silently ignored | Client doesn't know their request is wrong |
| `transform: true` | Query params stay as strings | Type mismatch bugs (`"1" + "2" = "12"`) |

## DTO Design Patterns

### Create vs Update DTOs
```typescript
// create-user.dto.ts
export class CreateUserDto {
  @IsString()
  @IsNotEmpty()
  @MinLength(2)
  @MaxLength(100)
  name: string;

  @IsEmail()
  email: string;

  @IsString()
  @MinLength(8)
  @Matches(/^(?=.*[A-Z])(?=.*[0-9])/, {
    message: 'Password must contain uppercase letter and number',
  })
  password: string;
}

// update-user.dto.ts — All fields optional
export class UpdateUserDto extends PartialType(CreateUserDto) {}
```

### Query Parameter DTOs
```typescript
export class PaginationDto {
  @IsOptional()
  @IsInt()
  @Min(1)
  @Max(100)
  limit?: number = 20;

  @IsOptional()
  @IsString()
  cursor?: string;

  @IsOptional()
  @IsEnum(SortOrder)
  sort?: SortOrder = SortOrder.DESC;
}
```

## Security Validation Rules

### Mandatory for Every DTO
1. **String lengths** — Always set `@MaxLength()` to prevent memory exhaustion
2. **Array limits** — Use `@ArrayMaxSize(100)` on array fields
3. **Enum values** — Use `@IsEnum()` not `@IsString()` for constrained values
4. **UUID format** — Use `@IsUUID()` for ID parameters, never trust raw strings
5. **Sanitize HTML** — Use `@Transform(({ value }) => sanitizeHtml(value))` if accepting rich text

### File Upload Validation
```typescript
@UseInterceptors(FileInterceptor('file', {
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB max
  fileFilter: (req, file, cb) => {
    const allowed = ['image/jpeg', 'image/png', 'application/pdf'];
    if (!allowed.includes(file.mimetype)) {
      cb(new BadRequestException('Invalid file type'), false);
    }
    cb(null, true);
  },
}))
```

## Anti-Patterns
- ❌ Using `@Body() body: any` — Always type with a DTO class
- ❌ Validating inside service methods — Validate at controller boundary
- ❌ Missing `@MaxLength()` on strings — Memory bomb via 10MB string
- ❌ Trusting `Content-Type` header for file type — Check magic bytes

## Verification
- [ ] Every POST/PUT/PATCH endpoint has a typed DTO
- [ ] Global ValidationPipe is configured with `whitelist` + `forbidNonWhitelisted`
- [ ] All string fields have `@MaxLength()`
- [ ] All array fields have `@ArrayMaxSize()`
- [ ] ID parameters use `@IsUUID()` or `@IsInt()`
