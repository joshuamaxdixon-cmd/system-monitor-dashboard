# Production Map

## Domains
- cloudwithjosh.com -> Portfolio
- www.cloudwithjosh.com -> Portfolio
- nexgenhealthapp.com -> NexGEN
- www.nexgenhealthapp.com -> NexGEN

## Load Balancer
- ALB: my-app-alb

## Target Groups
- portfolio-tg -> nexgen-server:5001
- my-app-targets -> nexgen-server:5000
- health-targets -> system-monitor / health route
- logs-targets -> cloud log analyzer route
- file-targets -> log file analyzer route

## Listener Rules

### HTTP :80
- /projects/system-health* -> health-targets
- cloudwithjosh.com, www.cloudwithjosh.com -> portfolio-tg
- nexgenhealthapp.com, www.nexgenhealthapp.com -> my-app-targets
- default -> redirect to HTTPS

### HTTPS :443
- /projects/log-file-analyzer* -> file-targets
- /cloud-log-analyzer -> logs-targets
- /projects/system-health* -> health-targets
- cloudwithjosh.com, www.cloudwithjosh.com -> portfolio-tg
- nexgenhealthapp.com, www.nexgenhealthapp.com -> my-app-targets
- default -> portfolio-tg

## EC2 Services

### nexgen-server
- nexgen.service -> port 5000
- portfolio.service -> port 5001

## Notes
- Portfolio currently runs on the same EC2 instance as NexGEN.
- Long-term goal: move portfolio to its own EC2 instance.
