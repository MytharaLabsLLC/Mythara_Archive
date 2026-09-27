# Mythara Engine - Incident Response Playbook

> **Template — customize before use.** This runbook is a deployment template, not an operating procedure for a live organization. Roles (CTO, Tech Lead, Engineering Manager), contact placeholders, notification tools (PagerDuty, Slack), and customer-facing steps assume infrastructure that does not currently exist. An operator must fill every `[placeholder]`, define the on-call roster, and stand up the notification tooling before this runbook can be used for a real deployment.

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

## 🚨 Emergency Response Procedures

### Incident Severity Levels

- **P0 - Critical:** Complete service outage, data loss risk
- **P1 - High:** Major functionality broken, security breach
- **P2 - Medium:** Degraded performance, non-critical features affected
- **P3 - Low:** Minor issues, cosmetic bugs

---

## 📞 Escalation Matrix

| Severity | Response Time | Notification | Escalation Path |
|----------|---------------|--------------|-----------------|
| P0 | Immediate | Page on-call | → Tech Lead → Engineering Manager → CTO |
| P1 | 15 minutes | Slack + Email | → Tech Lead → Engineering Manager |
| P2 | 1 hour | Slack | → Tech Lead |
| P3 | 4 hours | Ticket | Team assignment |

---

## 🔥 P0 - Critical Incidents

### Service Completely Down

**Detection:**
- Uptime monitor alerts
- Health check endpoint returns 5xx
- Customer reports via support

**Immediate Actions:**
1. Acknowledge incident in PagerDuty/Opsgenie
2. Post to #incidents Slack channel
3. Check service status: `curl https://api.yourdomain.com/health`
4. Check logs: Review last 15 minutes in log aggregator
5. Check infrastructure: AWS Console, Railway dashboard

**Common Causes & Fixes:**

| Issue | Diagnostic | Resolution |
|-------|-----------|------------|
| Database down | `psql $DATABASE_URL -c "SELECT 1"` | Restart database, check connection limits |
| Redis down | `redis-cli -u $REDIS_URL ping` | Restart Redis, check memory usage |
| Application crash | Check container logs | Restart application, check OOM errors |
| Rate limit exhausted | Check rate limit metrics | Increase limits temporarily |

**Rollback Procedure:**
```bash
# Railway
railway rollback

# AWS ECS
aws ecs update-service --service mythara --task-definition mythara:PREVIOUS_VERSION

# Docker
docker-compose down
docker-compose up -d mythara:TAG_PREVIOUS
```

---

### Database Connection Failure

**Symptoms:**
- API returns 500 errors
- Logs show "connection refused" or "too many connections"

**Diagnostic Commands:**
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check for long-running queries
SELECT pid, now() - query_start as duration, query 
FROM pg_stat_activity 
WHERE state = 'active' AND now() - query_start > interval '5 minutes';

-- Kill long-running query
SELECT pg_terminate_backend(PID);
```

**Resolution:**
1. Increase connection pool size temporarily
2. Kill long-running queries
3. Restart application to reset connection pool
4. Check for connection leaks in code

---

### Data Loss Risk

**Symptoms:**
- Database corruption warnings
- Filesystem full errors
- Backup failures

**Immediate Actions:**
1. **STOP ALL WRITES** - Enable read-only mode
2. Create emergency backup: `pg_dump $DATABASE_URL > emergency_backup.sql`
3. Check disk space: `df -h`
4. Contact database administrator immediately
5. Assess data integrity: Run consistency checks

---

## 🔴 P1 - High Severity Incidents

### API Error Rate > 5%

**Diagnostic:**
```bash
# Check recent errors in logs
grep -i "error" /var/log/mythara/app.log | tail -n 100

# Check specific endpoint error rates
curl -H "Authorization: Bearer $API_KEY" \
  https://api.yourdomain.com/v1/admin/metrics
```

**Common Causes:**
- Downstream service (ElevenLabs, Stripe) is down
- Rate limiting triggered
- Database connection pool exhausted
- Memory leak causing OOM

**Resolution:**
1. Identify failing endpoint from logs
2. Check downstream service status pages
3. Increase resources if resource-constrained
4. Deploy hotfix if code issue identified

---

### Security Breach Detected

**Symptoms:**
- Unauthorized API access attempts
- Unusual traffic patterns
- Data exfiltration alerts

**IMMEDIATE ACTIONS:**
1. **Rotate all API keys immediately**
2. **Rotate database credentials**
3. **Enable additional logging**
4. Contact security team
5. Document all findings

**Containment:**
```bash
# Block suspicious IP addresses
# Add to firewall rules or WAF

# Revoke compromised API key
# Update API key database

# Force logout all sessions
redis-cli FLUSHDB
```

**Investigation:**
1. Review access logs for unauthorized activity
2. Check for data exfiltration attempts
3. Identify attack vector
4. Document timeline of events
5. Preserve forensic evidence

---

## 🟡 P2 - Medium Severity Incidents

### Slow API Response Times (P95 > 2s)

**Diagnostic:**
```bash
# Check performance metrics
python tests/test_performance.py

# Check database query performance
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

# Check Redis latency
redis-cli --latency
```

**Resolution:**
1. Identify slow queries in database
2. Add database indexes if needed
3. Optimize slow API endpoints
4. Scale horizontally if traffic increased

---

### Database Disk Usage > 80%

**Diagnostic:**
```sql
-- Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check for dead rows
SELECT 
  schemaname,
  tablename,
  n_dead_tup,
  n_live_tup
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

**Resolution:**
1. Run VACUUM ANALYZE
2. Archive old data
3. Increase disk size
4. Set up automated cleanup jobs

---

## 🟢 P3 - Low Severity Incidents

### Documentation Update Needed

**Process:**
1. Create GitHub issue
2. Assign to documentation owner
3. Update relevant documentation
4. Submit pull request
5. Review and merge

---

## 📊 Post-Incident Process

### Incident Report Template

**Incident Summary:**
- **Date/Time:** [UTC timestamp]
- **Duration:** [X hours, Y minutes]
- **Severity:** [P0/P1/P2/P3]
- **Services Affected:** [List]
- **Users Impacted:** [Estimated number/percentage]

**Timeline:**
- [HH:MM] Incident detected
- [HH:MM] Team notified
- [HH:MM] Root cause identified
- [HH:MM] Fix deployed
- [HH:MM] Service restored
- [HH:MM] Incident closed

**Root Cause:**
[Detailed explanation]

**Resolution:**
[What was done to fix it]

**Action Items:**
- [ ] Prevent recurrence (owner, due date)
- [ ] Improve monitoring (owner, due date)
- [ ] Update documentation (owner, due date)
- [ ] Add automated tests (owner, due date)

**Lessons Learned:**
- What went well?
- What could be improved?
- What surprised us?

---

## 🛠️ Common Debugging Commands

### Check Service Health
```bash
# API health
curl https://api.yourdomain.com/health

# Database health
psql $DATABASE_URL -c "SELECT version();"

# Redis health
redis-cli -u $REDIS_URL ping
```

### Check Resource Usage
```bash
# CPU and memory
top
htop

# Disk usage
df -h
du -sh /var/log/*

# Network connections
netstat -an | grep ESTABLISHED | wc -l
```

### Check Logs
```bash
# Application logs
tail -f /var/log/mythara/app.log

# Error logs only
grep -i "error\|exception\|critical" /var/log/mythara/app.log

# Specific time range
grep "2025-11-19 14:" /var/log/mythara/app.log
```

### Database Queries
```sql
-- Active queries
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- Database size
SELECT pg_size_pretty(pg_database_size('mythara_production'));

-- Table sizes
SELECT 
  schemaname as schema,
  tablename as table,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Lock monitoring
SELECT * FROM pg_locks WHERE NOT granted;
```

---

## 📱 Contact Information

**On-Call Rotation:**
- Week 1: [Name] - [Phone] - [Email]
- Week 2: [Name] - [Phone] - [Email]
- Week 3: [Name] - [Phone] - [Email]
- Week 4: [Name] - [Phone] - [Email]

**Critical Contacts:**
- **CTO:** [Name] - [Phone] - [Email]
- **Tech Lead:** [Name] - [Phone] - [Email]
- **Database Admin:** [Name] - [Phone] - [Email]
- **Security Lead:** [Name] - [Phone] - [Email]
- **Customer Success:** [Name] - [Phone] - [Email]

**External Vendors:**
- **Railway Support:** support@railway.app
- **AWS Support:** [Support plan link]
- **Database Hosting:** [Support contact]

---

## 🔔 Communication Templates

### Status Page Update
```
[Investigating] We are currently investigating elevated error rates 
on our API. We will provide an update within 30 minutes.

[Identified] We have identified the issue as a database connection 
problem. We are working on a fix.

[Monitoring] A fix has been deployed and we are monitoring the 
situation. Services should return to normal shortly.

[Resolved] The issue has been resolved. All systems are operating 
normally. We apologize for any inconvenience.
```

### Customer Notification
```
Subject: Service Disruption Notice - [Date]

Dear Valued Customer,

We experienced a service disruption today from [START_TIME] to 
[END_TIME] UTC. During this time, [DESCRIBE IMPACT].

Root cause: [BRIEF EXPLANATION]

Resolution: [WHAT WE DID TO FIX IT]

We sincerely apologize for any inconvenience this may have caused. 
We have implemented [PREVENTIVE MEASURES] to prevent this from 
happening again.

If you have any questions, please contact support@yourdomain.com.

Best regards,
Mythara Engineering Team
```

---

**Last Updated:** November 19, 2025  
**Version:** 1.0  
**Owner:** Engineering Team

---

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**
