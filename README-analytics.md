helix Analytics Plugin
=============================


Overview
--------

The `helix_analytics` plugin analyzes HAProxy logs to extract usefull information on requested BBoxes, coverages etc.


Installation
------------

Add `helix_analytics` to the list of `ckan.plugins`

Configuration
-------------

The following configuration options are supported:

```ini
ckanext.helix.analytics.logfile_pattern = /var/log/haproxy.log* 
ckanext.helix.analytics.database_url = postgresql://user:pass@localhost:5432/analytics
ckanext.helix.analytics.export_date_format = %Y-%m-%d
ckanext.helix.analytics.ha_proxy_datetime_format = %d/%b/%Y:%H:%M:%S
```

Use
---

Add a cron job to periodically analyze your log files. The analysis is carried out by a
Paster subcommand:

```bash
paster helix --config $CKAN_CONFIG analyze-logs --from 2015-11-29 --to 2015-12-02

```

Note that the above command uses a processing window (granularity) of 1 day.
