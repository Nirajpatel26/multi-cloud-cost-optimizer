# FastAPI Endpoints Specification

## Base URL
`http://localhost:8000/api/v1`

---

## 1. Health Check Endpoints

### GET /health
**Description**: Check API and database health status

**Parameters**: None

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-01-31T10:30:00Z"
}
```

---

## 2. Cost Endpoints

### GET /aws/costs
**Description**: Get cost data with optional filters

**Query Parameters**:
- `start_date` (optional, string): Start date in YYYY-MM-DD format
- `end_date` (optional, string): End date in YYYY-MM-DD format
- `region` (optional, string): AWS region (e.g., "us-east-1")
- `service_name` (optional, string): AWS service name (e.g., "EC2", "S3")

**Response**:
```json
{
  "total_records": 150,
  "costs": [
    {
      "id": 1,
      "service_name": "EC2",
      "cost": 125.50,
      "usage_type": "standard",
      "start_date": "2026-01-01",
      "end_date": "2026-01-31",
      "region": "us-east-1",
      "created_at": "2026-01-31T10:00:00Z"
    }
  ]
}
```

### GET /aws/costs/summary
**Description**: Get aggregated cost summary by service and region

**Query Parameters**:
- `start_date` (optional, string): Start date in YYYY-MM-DD format
- `end_date` (optional, string): End date in YYYY-MM-DD format

**Response**:
```json
{
  "total_cost": 1250.75,
  "period": {
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
  },
  "by_service": [
    {
      "service_name": "EC2",
      "total_cost": 850.25,
      "percentage": 68.0
    },
    {
      "service_name": "S3",
      "total_cost": 200.50,
      "percentage": 16.0
    }
  ],
  "by_region": [
    {
      "region": "us-east-1",
      "total_cost": 900.00,
      "percentage": 72.0
    }
  ]
}
```

---

## 3. Resource Endpoints

### POST /aws/resources/scan
**Description**: Trigger resource scanning across specified regions

**Request Body**:
```json
{
  "regions": ["us-east-1", "us-west-2"],
  "resource_types": ["ec2", "ebs"]
}
```

**Parameters**:
- `regions` (required, array of strings): List of AWS regions to scan
- `resource_types` (optional, array of strings): Types of resources to scan (default: ["ec2", "ebs"])

**Response**:
```json
{
  "scan_id": "scan_20260131_103000",
  "status": "completed",
  "resources_found": {
    "ec2_instances": 15,
    "ebs_volumes": 8
  },
  "regions_scanned": ["us-east-1", "us-west-2"],
  "timestamp": "2026-01-31T10:30:00Z"
}
```

### GET /aws/resources
**Description**: List all resources with optional filters

**Query Parameters**:
- `type` (optional, string): Resource type ("ec2" or "ebs")
- `region` (optional, string): AWS region filter
- `state` (optional, string): Resource state ("running", "stopped" for EC2; "available", "in-use" for EBS)
- `is_idle` (optional, boolean): Filter idle resources (EC2 only)
- `is_attached` (optional, boolean): Filter by attachment status (EBS only)

**Response**:
```json
{
  "total_count": 15,
  "resources": {
    "ec2_instances": [
      {
        "id": 1,
        "instance_id": "i-1234567890abcdef0",
        "instance_type": "t3.medium",
        "state": "running",
        "region": "us-east-1",
        "availability_zone": "us-east-1a",
        "launch_time": "2026-01-15T08:00:00Z",
        "cpu_utilization": 2.5,
        "is_idle": true,
        "tags": [{"Key": "Name", "Value": "WebServer"}]
      }
    ],
    "ebs_volumes": [
      {
        "id": 1,
        "volume_id": "vol-0123456789abcdef0",
        "size": 100,
        "volume_type": "gp3",
        "state": "available",
        "is_attached": false,
        "region": "us-east-1",
        "availability_zone": "us-east-1a"
      }
    ]
  }
}
```

---

## 4. Recommendation Endpoints

### GET /aws/recommendations
**Description**: Get all optimization recommendations

**Query Parameters**:
- `severity` (optional, string): Filter by severity ("LOW", "MEDIUM", "HIGH", "CRITICAL")
- `recommendation_type` (optional, string): Filter by type ("IDLE_INSTANCE", "UNATTACHED_VOLUME", etc.)
- `region` (optional, string): Filter by region
- `min_savings` (optional, float): Minimum potential savings threshold

**Response**:
```json
{
  "total_recommendations": 8,
  "total_potential_savings": 287.50,
  "recommendations": [
    {
      "id": 1,
      "resource_id": "i-1234567890abcdef0",
      "resource_type": "EC2",
      "recommendation_type": "IDLE_INSTANCE",
      "description": "Instance i-1234567890abcdef0 has 2.5% CPU utilization over 7 days",
      "potential_savings": 70.00,
      "severity": "HIGH",
      "region": "us-east-1",
      "created_at": "2026-01-31T10:00:00Z"
    }
  ]
}
```

### GET /aws/recommendations/idle-instances
**Description**: Get list of idle EC2 instances

**Query Parameters**:
- `cpu_threshold` (optional, float): CPU utilization threshold percentage (default: 5.0)
- `region` (optional, string): Filter by region

**Response**:
```json
{
  "total_idle_instances": 3,
  "total_potential_savings": 210.00,
  "idle_instances": [
    {
      "instance_id": "i-1234567890abcdef0",
      "instance_type": "t3.medium",
      "region": "us-east-1",
      "cpu_utilization": 2.5,
      "potential_savings": 70.00,
      "recommendation": "Consider stopping or downsizing this instance"
    }
  ]
}
```

### GET /aws/recommendations/unattached-volumes
**Description**: Get list of unattached EBS volumes

**Query Parameters**:
- `region` (optional, string): Filter by region
- `min_size` (optional, integer): Minimum volume size in GB

**Response**:
```json
{
  "total_unattached_volumes": 5,
  "total_potential_savings": 77.50,
  "unattached_volumes": [
    {
      "volume_id": "vol-0123456789abcdef0",
      "size": 100,
      "volume_type": "gp3",
      "region": "us-east-1",
      "availability_zone": "us-east-1a",
      "monthly_cost": 8.00
    }
  ]
}
```

---

## 5. Analytics Endpoints

### GET /aws/savings
**Description**: Get potential savings summary

**Query Parameters**: None

**Response**:
```json
{
  "total_potential_savings": 287.50,
  "breakdown": {
    "idle_instances_savings": 210.00,
    "unattached_volumes_savings": 77.50
  },
  "recommendations_count": {
    "total": 8,
    "by_severity": {
      "CRITICAL": 0,
      "HIGH": 3,
      "MEDIUM": 3,
      "LOW": 2
    }
  },
  "last_analysis": "2026-01-31T10:00:00Z"
}
```

### POST /aws/analyze
**Description**: Run full cost optimization analysis

**Request Body**:
```json
{
  "regions": ["us-east-1", "us-west-2"],
  "cpu_threshold": 5.0,
  "include_cost_data": true,
  "lookback_days": 30
}
```

**Parameters**:
- `regions` (optional, array of strings): Regions to analyze (default: all configured regions)
- `cpu_threshold` (optional, float): CPU threshold for idle detection (default: 5.0)
- `include_cost_data` (optional, boolean): Include historical cost data (default: true)
- `lookback_days` (optional, integer): Number of days to analyze (default: 30)

**Response**:
```json
{
  "analysis_id": "analysis_20260131_103000",
  "timestamp": "2026-01-31T10:30:00Z",
  "summary": {
    "total_instances": 15,
    "running_instances": 12,
    "idle_instances": 3,
    "unattached_volumes": 5,
    "cost_records": 150
  },
  "total_potential_savings": 287.50,
  "regions_analyzed": ["us-east-1", "us-west-2"],
  "cost_data": {
    "total_cost_30_days": 1250.75,
    "average_daily_cost": 41.69
  },
  "top_recommendations": [
    {
      "resource_id": "i-1234567890abcdef0",
      "resource_type": "EC2",
      "potential_savings": 70.00,
      "severity": "HIGH"
    }
  ]
}
```

---

## Common Response Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Common Error Response Format

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid date format. Expected YYYY-MM-DD",
    "details": {
      "parameter": "start_date",
      "provided_value": "2026-31-01"
    }
  }
}
```
