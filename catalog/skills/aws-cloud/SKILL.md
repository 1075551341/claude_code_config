---
name: aws-cloud
description: 部署AWS云服务、配置AWS资源、编写CloudFormation/IAM策略、使用AWS CLI/SDK
triggers: [AWS, 亚马逊云, EC2, S3, Lambda, RDS, CloudFormation, IAM策略, AWS CLI, AWS SDK, 云服务部署]
---

# AWS 云服务

## 核心能力

**AWS 服务配置、CLI 命令、CloudFormation 模板、IAM 策略编写。**

---

## 适用场景

- AWS 资源部署
- CloudFormation 模板编写
- IAM 策略配置
- S3/EC2/Lambda/RDS 操作
- AWS CLI 命令
- AWS SDK 开发

---

## 常用服务

### 计算

| 服务 | 用途 |
|------|------|
| EC2 | 虚拟服务器 |
| Lambda | 无服务器函数 |
| ECS | 容器服务 |
| EKS | Kubernetes |

### 存储

| 服务 | 用途 |
|------|------|
| S3 | 对象存储 |
| EBS | 块存储 |
| EFS | 文件存储 |

### 数据库

| 服务 | 用途 |
|------|------|
| RDS | 关系数据库 |
| DynamoDB | NoSQL |
| Aurora | 高性能关系库 |

---

## CLI 常用命令

### S3 操作

```bash
# 上传
aws s3 cp file.txt s3://bucket/

# 下载
aws s3 cp s3://bucket/file.txt ./

# 同步
aws s3 sync ./local s3://bucket/

# 列表
aws s3 ls s3://bucket/
```

### EC2 操作

```bash
# 启动实例
aws ec2 run-instances --image-id ami-xxx --instance-type t3.micro

# 列出实例
aws ec2 describe-instances

# 停止/启动
aws ec2 stop-instances --instance-ids i-xxx
aws ec2 start-instances --instance-ids i-xxx
```

### Lambda 操作

```bash
# 创建函数
aws lambda create-function \
  --function-name myFunc \
  --runtime python3.9 \
  --handler index.handler \
  --zip-file fileb://function.zip

# 调用
aws lambda invoke --function-name myFunc output.json
```

---

## CloudFormation 模板

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Web Application Stack

Resources:
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0xxx
      InstanceType: t3.micro
      SecurityGroupIds:
        - !Ref WebSecurityGroup

  WebSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Web Server SG
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

Outputs:
  InstanceId:
    Value: !Ref WebServer
```

---

## IAM 烈策

### 最小权限原则

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::bucket-name/*"
    }
  ]
}
```

### 避免

```
不安全模式：
- 使用 "*" 作为 Action
- 使用 "*" 作为 Resource
- Admin 权限用于应用
```

---

## SDK 使用示例

### Python (boto3)

```python
import boto3

# S3
s3 = boto3.client('s3')
s3.upload_file('file.txt', 'bucket', 'key')

# EC2
ec2 = boto3.resource('ec2')
instances = ec2.instances.all()

# Lambda
lambda_client = boto3.client('lambda')
response = lambda_client.invoke(FunctionName='myFunc')
```

### Node.js

```javascript
const AWS = require('aws-sdk');

// S3
const s3 = new AWS.S3();
await s3.putObject({
  Bucket: 'bucket',
  Key: 'key',
  Body: data
}).promise();

// DynamoDB
const dynamo = new AWS.DynamoDB.DocumentClient();
await dynamo.put({
  TableName: 'table',
  Item: { id: '1', data: 'value' }
}).promise();
```

---

## 注意事项

```
必须：
- 使用最小权限 IAM
- 配置 CloudWatch 监控
- 定期轮换密钥
- 使用参数存储敏感信息

避免：
- 硬编码密钥
- 公开 S3 bucket
- 安全组开放过多端口
- 未配置日志
```

---

## 相关技能

- `deploy-script` - 部署脚本
- `docker-devops` - Docker 配置
- `nginx-config` - 反向代理配置
- `logging-monitoring` - 监控配置
