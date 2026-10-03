import os
import subprocess
import concurrent.futures

REPOS = [
    # Architecture
    ("system-design-primer", "https://github.com/donnemartin/system-design-primer.git"),
    ("distsys-class", "https://github.com/aphyr/distsys-class.git"),
    ("scalability", "https://github.com/ci-ai/scalability.git"),
    ("architecture-decision-record", "https://github.com/joelparkerhenderson/architecture-decision-record.git"),
    # Integration
    ("camel", "https://github.com/apache/camel.git"),
    # Clean Architecture
    ("python-clean-architecture-codex", "https://github.com/MKToronto/python-clean-architecture-codex.git"),
    ("py-clean-architecture-examples", "https://github.com/CJHwong/py-clean-architecture-examples.git"),
    # Reliability
    ("resilience4j", "https://github.com/resilience4j/resilience4j.git"),
    # Observability
    ("opentelemetry-collector", "https://github.com/open-telemetry/opentelemetry-collector.git"),
    ("opentelemetry-python", "https://github.com/open-telemetry/opentelemetry-python.git"),
    # Performance
    ("SimpleDB", "https://github.com/TheODDYSEY/SimpleDB.git"),
    ("Algorithms", "https://github.com/williamfiset/Algorithms.git"),
    # AI / RAG
    ("haystack", "https://github.com/deepset-ai/haystack.git"),
    ("qdrant", "https://github.com/qdrant/qdrant.git"),
    # Kubernetes
    ("kubernetes", "https://github.com/kubernetes/kubernetes.git"),
    ("kubernetes-website", "https://github.com/kubernetes/website.git"),
    # Security
    ("API-Security-Checklist", "https://github.com/shieldfy/API-Security-Checklist.git"),
    ("CheatSheetSeries", "https://github.com/OWASP/CheatSheetSeries.git"),
    ("PayloadsAllTheThings", "https://github.com/swisskyrepo/PayloadsAllTheThings.git"),
    # Node.js
    ("nodebestpractices", "https://github.com/goldbergyoni/nodebestpractices.git"),
    # IAM
    ("keycloak", "https://github.com/keycloak/keycloak.git"),
    ("keycloak-quickstarts", "https://github.com/keycloak/keycloak-quickstarts.git"),
    # Microservices
    ("microservices-demo", "https://github.com/GoogleCloudPlatform/microservices-demo.git"),
    # AI Infrastructure
    ("daytona", "https://github.com/daytonaio/daytona.git")
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
    # Clone up to 6 repos concurrently to optimize network and speed
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
