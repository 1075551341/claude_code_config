---
name: kubernetes
description: 当需要部署Kubernetes集群、编写K8s配置文件、管理容器编排、配置Pod/Service/Deployment时调用此技能。触发词：Kubernetes、K8s、容器编排、kubectl、Pod、Deployment、Service、Kubernetes配置。
---

# Kubernetes 容器编排

## 核心能力

**K8s集群部署、资源配置、容器编排管理。**

---

## 适用场景

- K8s 集群部署
- 容器编排配置
- 资源管理
- 服务部署

---

## 核心概念

| 概念 | 说明 |
|------|------|
| Pod | 最小部署单元，一个或多个容器 |
| Deployment | 管理Pod副本数和更新策略 |
| Service | 服务发现和负载均衡 |
| ConfigMap | 配置数据 |
| Secret | 敏感数据 |
| Namespace | 资源隔离 |
| Ingress | HTTP路由 |

---

## 常用命令

### 集群管理

```bash
# 查看集群信息
kubectl cluster-info

# 查看节点
kubectl get nodes

# 查看资源
kubectl get pods
kubectl get deployments
kubectl get services

# 查看详情
kubectl describe pod <pod-name>

# 查看日志
kubectl logs <pod-name>
kubectl logs -f <pod-name>  # 实时查看
```

### 部署操作

```bash
# 应用配置
kubectl apply -f deployment.yaml

# 删除资源
kubectl delete -f deployment.yaml

# 扩缩容
kubectl scale deployment/app --replicas=3

# 更新镜像
kubectl set image deployment/app container=image:v2

# 回滚
kubectl rollout undo deployment/app

# 查看状态
kubectl rollout status deployment/app
```

---

## Deployment 配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: app
        image: my-app:v1
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        env:
        - name: ENV
          value: "production"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
```

---

## Service 配置

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP  # ClusterIP / NodePort / LoadBalancer
```

---

## Ingress 配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
```

---

## ConfigMap & Secret

```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgres://localhost:5432/db"
  log_level: "info"

---
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: cGFzc3dvcmQxMjM=  # base64编码
```

---

## Helm 包管理

```bash
# 安装Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 添加仓库
helm repo add bitnami https://charts.bitnami.com/bitnami

# 搜索
helm search repo nginx

# 安装
helm install my-nginx bitnami/nginx

# 更新
helm upgrade my-nginx bitnami/nginx

# 卸载
helm uninstall my-nginx
```

---

## 注意事项

```
必须:
- 设置资源限制
- 配置健康检查
- 使用ConfigMap/Secret
- 实现滚动更新

避免:
- 单副本部署
- 无资源限制
- 明文存储敏感信息
- 忽略日志收集
```

---

## 相关技能

- `docker-devops` - Docker 容器化
- `cicd-pipeline` - CI/CD 流水线
- `deploy-script` - 部署脚本