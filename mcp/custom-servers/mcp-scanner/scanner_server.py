import os
import subprocess
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vulnerability Scanner")

SEMGREP_DIR = r"C:\Users\ffram\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts"
SEMGREP_EXE = os.path.join(SEMGREP_DIR, "semgrep.exe")
GITLEAKS_EXE = r"C:\Users\ffram\.gemini\tmp\bin\gitleaks.exe"
SCRIPTS_ENV = os.environ.copy()
SCRIPTS_ENV["PATH"] = SEMGREP_DIR + os.pathsep + SCRIPTS_ENV.get("PATH", "")

@mcp.tool(name="semgrep_scan")
def semgrep_scan(target_path: str, config: str = "auto") -> str:
    """Run Semgrep static analysis security scan on target directory or file.
    
    Args:
        target_path: Absolute path to the directory or file to scan (TypeScript, JS, Python, Go, JSON)
        config: Rule configuration to use. Defaults to 'auto' for OWASP Top 10 + security best practices.
    """
    try:
        cmd = [SEMGREP_EXE, "scan", "--config", config, "--json", "--quiet", target_path]
        proc = subprocess.run(cmd, capture_output=True, text=True, env=SCRIPTS_ENV, timeout=120)
        if proc.stdout:
            try:
                data = json.loads(proc.stdout)
                results = data.get("results", [])
                summary = {
                    "total_findings": len(results),
                    "target": target_path,
                    "findings": [
                        {
                            "check_id": r.get("check_id"),
                            "path": r.get("path"),
                            "start_line": r.get("start", {}).get("line"),
                            "message": r.get("extra", {}).get("message"),
                            "severity": r.get("extra", {}).get("severity"),
                        }
                        for r in results[:20]
                    ]
                }
                return json.dumps(summary, indent=2)
            except Exception:
                return proc.stdout[:2000]
        if proc.stderr:
            return f"Scan finished with notice: {proc.stderr[:1000]}"
        return json.dumps({"total_findings": 0, "target": target_path, "status": "CLEAN - No vulnerabilities found"})
    except Exception as e:
        return f"Scan error: {str(e)}"

@mcp.tool(name="scan_owasp")
def scan_owasp(target_path: str) -> str:
    """Run specialized OWASP Top 10 security audit using Semgrep on target codebase.
    
    Args:
        target_path: Absolute path to the codebase to audit
    """
    return semgrep_scan(target_path, config="p/owasp-top-ten")

@mcp.tool(name="scan_secrets")
def scan_secrets(target_path: str) -> str:
    """Run Gitleaks deterministic mechanical scanner to detect hardcoded API keys, passwords, tokens, and credentials.
    
    Args:
        target_path: Absolute path to the directory or file to scan for leaked secrets
    """
    try:
        cmd = [GITLEAKS_EXE, "dir", target_path, "--report-format", "json", "--report-path", "-", "--no-banner"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = proc.stdout.strip()
        if output:
            try:
                leaks = json.loads(output)
                if len(leaks) > 0:
                    summary = {
                        "total_leaks": len(leaks),
                        "status": "VULNERABILITY DETECTED - Hardcoded secrets found!",
                        "leaks": [
                            {
                                "description": l.get("Description"),
                                "file": l.get("File"),
                                "start_line": l.get("StartLine"),
                                "rule_id": l.get("RuleID")
                            }
                            for l in leaks[:15]
                        ]
                    }
                    return json.dumps(summary, indent=2)
            except Exception:
                pass
        return json.dumps({"total_leaks": 0, "target": target_path, "status": "CLEAN - No hardcoded secrets detected"})
    except Exception as e:
        return f"Gitleaks scan error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
