---
name: gitops-delivery
description: Use when designing or configuring continuous delivery (CD) GitOps workflows, managing Helm charts, or synchronizing application state in Kubernetes using Argo CD. Mapped to local repositories argo-cd and helm.
metadata:
  tags: "gitops, argocd, helm, kubernetes, CD, continuous-delivery, deployment"
  category: "infrastructure"
---
# GitOps Delivery — Argo CD, Helm & Continuous Deployment

## 1. Core GitOps Principles
- **Git is the single source of truth**: All desired state (K8s manifests, Helm values, Kustomize overlays) lives in Git
- **Declarative over imperative**: Define WHAT the system should look like, not HOW to get there
- **Automated reconciliation**: The GitOps operator continuously compares desired state (Git) vs actual state (cluster) and auto-corrects drift
- **Pull-based deployment**: The cluster pulls changes from Git (Argo CD) rather than CI pushing to the cluster

## 2. Repository Structure

### Option A: Monorepo (App + Infra)
```
my-app/
├── src/                    # Application source code
├── Dockerfile
├── helm/                   # Helm chart for this app
│   ├── Chart.yaml
│   ├── values.yaml         # Default values
│   ├── values-staging.yaml # Staging overrides
│   ├── values-prod.yaml    # Production overrides
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       └── hpa.yaml
└── .github/workflows/
    └── ci.yaml             # Build, test, push image, update image tag in values
```

### Option B: Separate Config Repo (Recommended for multi-service)
```
# App Repo: my-app (CI builds image, updates tag in config repo)
# Config Repo: my-app-config (Argo CD watches this)
my-app-config/
├── base/                   # Shared manifests
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   └── service.yaml
├── overlays/
│   ├── staging/
│   │   ├── kustomization.yaml
│   │   └── patch-replicas.yaml
│   └── production/
│       ├── kustomization.yaml
│       └── patch-replicas.yaml
└── argocd/
    └── application.yaml    # Argo CD Application manifest
```

## 3. Argo CD Application Configuration
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app-production
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/my-app-config.git
    targetRevision: main
    path: overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
  syncPolicy:
    automated:
      prune: true        # Delete resources removed from Git
      selfHeal: true      # Auto-correct manual kubectl changes
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true    # Prune after all other resources synced
    retry:
      limit: 3
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 1m
```

## 4. Helm Chart Best Practices

### Values Structure
```yaml
# values.yaml — sensible defaults
replicaCount: 1
image:
  repository: gcr.io/my-project/my-app
  tag: latest  # Overridden by CI
  pullPolicy: IfNotPresent
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilization: 80
env: []
```

### Template Patterns
```yaml
# deployment.yaml
spec:
  {{- if .Values.autoscaling.enabled }}
  replicas: {{ .Values.autoscaling.minReplicas }}
  {{- else }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  template:
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.service.port }}
          livenessProbe:
            httpGet:
              path: /health
              port: {{ .Values.service.port }}
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /health/ready
              port: {{ .Values.service.port }}
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

## 5. Deployment Strategies

### Blue-Green
- Deploy new version alongside old version
- Switch traffic via service selector or ingress update
- Instant rollback by switching back
- **Use when**: Zero-downtime is critical, database schema is backward-compatible

### Canary (Progressive Delivery)
```yaml
# Argo Rollouts canary strategy
spec:
  strategy:
    canary:
      steps:
        - setWeight: 10    # 10% traffic to new version
        - pause: { duration: 5m }
        - setWeight: 30
        - pause: { duration: 5m }
        - setWeight: 60
        - pause: { duration: 10m }
        - setWeight: 100   # Full rollout
      canaryMetadata:
        annotations:
          role: canary
```
- **Use when**: Gradual validation needed, monitoring in place

### Rolling Update (Default K8s)
- Replace pods one-by-one
- `maxUnavailable: 0, maxSurge: 1` for zero-downtime
- **Use when**: Standard deployments, stateless services

## 6. CI → GitOps Bridge
```yaml
# GitHub Actions: After image build, update tag in config repo
- name: Update image tag
  run: |
    cd config-repo
    yq e ".image.tag = \"${{ github.sha }}\"" -i overlays/staging/values.yaml
    git add .
    git commit -m "chore: update my-app image to ${{ github.sha }}"
    git push
```

**Key rules**:
- CI pushes image to registry + updates tag in config repo
- Argo CD detects config repo change and syncs cluster
- Never `kubectl apply` from CI — always go through Git

## 7. Rollback Procedure
1. **Git revert**: `git revert HEAD` in config repo → Argo CD auto-syncs to previous state
2. **Argo CD UI**: Click "History" → select previous revision → "Rollback"
3. **Emergency**: `argocd app rollback my-app-production <revision>`

## 8. Monitoring & Alerts
- **Sync Status**: Alert if app stays `OutOfSync` > 5 minutes
- **Health Status**: Alert if app health is `Degraded` or `Missing`
- **Drift Detection**: Alert if manual `kubectl` changes detected (selfHeal will fix, but log it)
