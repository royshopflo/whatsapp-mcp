# 🤖 Automated WhatsApp Analysis CRON Setup

## ✅ CRON Job Successfully Configured!

Your WhatsApp group analysis is now **fully automated** and will run **3 times daily**:

- **🌅 10:00 AM IST** - Morning analysis
- **🌆 02:00 PM IST** - Afternoon analysis  
- **🌙 06:00 PM IST** - Evening analysis

## 📁 Files Created

| File | Purpose |
|------|---------|
| `automated_analysis.sh` | Main wrapper script for CRON execution |
| `send_to_whatsapp_group.py` | Python script that performs analysis and sends to WhatsApp |
| `setup_cron.sh` | Script to configure CRON jobs |
| `monitor_logs.sh` | Interactive monitoring script |
| `logs/` | Directory containing daily log files |

## 🎯 What Happens Automatically

Every execution will:

1. **🔍 Analyze** all (OB) WhatsApp groups from the last 5 days
2. **📊 Categorize** groups as:
   - 🚨 **Needs Attention** (critical issues)
   - ⚠️ **At Risk** (monitoring required)
   - ✅ **Stable** (healthy communication)
3. **📱 Send analysis** to `Shopflo onboarding-internal` WhatsApp group
4. **📝 Log results** to daily log files

## 📋 Current CRON Schedule

```bash
# WhatsApp Analysis - Auto-send to Shopflo onboarding-internal
0 10 * * * /Users/macbook/whatsapp-mcp-2/automated_analysis.sh >/dev/null 2>&1
0 14 * * * /Users/macbook/whatsapp-mcp-2/automated_analysis.sh >/dev/null 2>&1
0 18 * * * /Users/macbook/whatsapp-mcp-2/automated_analysis.sh >/dev/null 2>&1
```

## 🔧 Monitoring & Management

### Quick Commands

```bash
# Monitor logs interactively
./monitor_logs.sh

# View today's log
cat logs/analysis_$(date +%Y%m%d).log

# Check cron job status
crontab -l

# Test manual run
./automated_analysis.sh
```

### 📊 Monitor Script Features

Run `./monitor_logs.sh` for interactive menu:

1. **View today's log** - See all activity for today
2. **Tail live log** - Follow logs in real-time
3. **Check cron job status** - Verify scheduled jobs
4. **View recent runs** - See success/failure history
5. **Test manual run** - Run analysis immediately
6. **Remove cron job** - Disable automation

## 📝 Log Files

Logs are stored in `logs/analysis_YYYYMMDD.log` format:

- **Daily rotation** - New file each day
- **Detailed logging** - All steps and results
- **Error tracking** - Failed attempts with reasons
- **Success confirmation** - Message delivery status

### Example Log Entry
```
[2025-06-11 19:05:42 IST] ==========================================
[2025-06-11 19:05:42 IST] STARTING AUTOMATED WHATSAPP ANALYSIS
[2025-06-11 19:05:42 IST] ==========================================
[2025-06-11 19:05:42 IST] ✅ WhatsApp bridge is running
[2025-06-11 19:05:42 IST] ✅ Python script found
[2025-06-11 19:06:58 IST] ✅ SUCCESS: Analysis sent successfully to WhatsApp group
[2025-06-11 19:06:58 IST] 📱 Message delivered to 'Shopflo onboarding-internal' group
```

## ⚠️ Prerequisites & Dependencies

- **WhatsApp Bridge** must be running on `localhost:8080`
- **Python environment** with required packages (handled by `uv`)
- **System permissions** for CRON execution
- **Network connectivity** for API calls

## 🛠️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| CRON not running | Check `crontab -l` and system clock |
| WhatsApp API error | Ensure bridge is running on port 8080 |
| Permission denied | Check script execution permissions |
| Missing logs | Verify `logs/` directory exists |

### Manual Testing

```bash
# Test the full pipeline
./automated_analysis.sh

# Check if WhatsApp API is accessible
curl -s http://localhost:8080/api

# Verify cron job syntax
crontab -l | grep automated_analysis
```

## 🚀 Success Metrics

✅ **Automated Analysis Running**
- 3 daily executions scheduled
- Comprehensive merchant sentiment tracking
- Real-time team notifications
- Detailed logging and monitoring

✅ **Team Benefits**
- **Proactive support** - Identify issues before escalation
- **Data-driven decisions** - Quantified merchant satisfaction
- **Improved response times** - Immediate visibility into problems
- **Consistent monitoring** - Never miss critical merchant concerns

## 📞 Support

- **View logs**: `./monitor_logs.sh`
- **Manual run**: `./automated_analysis.sh`
- **Remove automation**: Use monitor script option 6
- **Edit schedule**: `crontab -e`

---

**🎉 Your WhatsApp analysis is now fully automated!**

The team will receive comprehensive merchant analysis reports 3 times daily, ensuring proactive support and improved customer satisfaction. 