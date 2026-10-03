import os
import subprocess
import concurrent.futures

REPOS = [
    # Agent Evaluation
    ("deepeval", "https://github.com/confident-ai/deepeval.git"),
    ("promptfoo", "https://github.com/promptfoo/promptfoo.git"),
    ("ragas", "https://github.com/explodinggradients/ragas.git"),
    # Supply Chain Security
    ("trivy", "https://github.com/aquasecurity/trivy.git"),
    ("syft", "https://github.com/anchore/syft.git"),
    ("cosign", "https://github.com/sigstore/cosign.git"),
    # Policy
    ("opa", "https://github.com/open-policy-agent/opa.git"),
    ("kyverno", "https://github.com/kyverno/kyverno.git"),
    # GitOps
    ("argo-cd", "https://github.com/argoproj/argo-cd.git"),
    ("helm", "https://github.com/helm/helm.git"),
    # Infrastructure as Code
    ("opentofu", "https://github.com/opentofu/opentofu.git"),
    ("terraform", "https://github.com/hashicorp/terraform.git"),
    # Chaos Engineering
    ("litmus", "https://github.com/litmuschaos/litmus.git"),
    # API Gateway / Networking
    ("envoy", "https://github.com/envoyproxy/envoy.git"),
    ("kong", "https://github.com/Kong/kong.git"),
    # Production Agent Evaluation Reference
    ("agent-eval-pipeline", "https://github.com/MFD3000/agent-eval-pipeline.git")
]

BASE_DIR = os.path.expanduser(r"~\security_repos")

def clone_repo(name, url):
    target_path = os.path.join(BASE_DIR, name)
    if os.path.exists(target_path) and os.listdir(target_path):
        print(f"[SKIP] {name} already exists and is not empty.")
        return f"{name}: SKIPPED"
    
    print(f"[START] Cloning {name} from {url}...")
    try:
        # Use shallow clone to save massive bandwidth and time
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, target_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print(f"[SUCCESS] Cloned {name}.")
        return f"{name}: SUCCESS"
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to clone {name}: {e.stderr}")
        return f"{name}: FAILED - {e.stderr}"

def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    # Clone up to 6 repos concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(clone_repo, name, url): name for name, url in REPOS}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                res = future.result()
                print(f"[RESULT] {res}")
            except Exception as exc:
                print(f"[EXCEPTION] {name} generated an exception: {exc}")

if __name__ == "__main__":
    main()
