# AWS and Azure in Practice — chapter exercises

Every chapter of *Defending Tomorrow* from Chapter 1 to Chapter 36 ends its technical content with an **AWS and Azure in Practice** section. It maps the chapter's controls to native AWS and Microsoft Azure services and gives a short exercise that runs on a **free AWS account and a free Azure account**. This folder holds those exercises, so that you can copy commands instead of retyping them from the page.

The book contains no console screenshots. Consoles change every few weeks; commands let you see the real, current result in your own account.

## Before you start

1. Create the accounts and budget alerts described in [docs/free-account-setup.md](../docs/free-account-setup.md).
2. Run [ch00.sh](ch00.sh) once in each shell to create `~/dt-env.sh`.
3. Open the script for the chapter you are reading. Copy the **AWS block** into AWS CloudShell and the **Azure block** into Azure Cloud Shell (Bash). Do not run a file as a single script: read each output, then run the cleanup lines.

## Scripts

| Script | Chapter | Title |
|---|---|---|
| [ch00.sh](ch00.sh) | 0 | Budget alerts and lab environment |
| [ch01.sh](ch01.sh) | 1 | Why Cybersecurity Is Still Losing |
| [ch02.sh](ch02.sh) | 2 | The Evolution of Enterprise Technology |
| [ch03.sh](ch03.sh) | 3 | Security Engineering Principles |
| [ch04.sh](ch04.sh) | 4 | Threat Modeling for Modern Enterprises |
| [ch05.sh](ch05.sh) | 5 | Cloud-Native Reference Architectures |
| [ch06.sh](ch06.sh) | 6 | Identity Is the New Control Plane |
| [ch07.sh](ch07.sh) | 7 | Networkless Security |
| [ch08.sh](ch08.sh) | 8 | Data-Centric Security |
| [ch09.sh](ch09.sh) | 9 | Designing the Enterprise Software Factory |
| [ch10.sh](ch10.sh) | 10 | Git Security Engineering |
| [ch11.sh](ch11.sh) | 11 | Secure CI/CD Architectures |
| [ch12.sh](ch12.sh) | 12 | Infrastructure as Code Security |
| [ch13.sh](ch13.sh) | 13 | Software Supply Chain Security |
| [ch14.sh](ch14.sh) | 14 | Container Security Engineering |
| [ch15.sh](ch15.sh) | 15 | Platform Engineering |
| [ch16.sh](ch16.sh) | 16 | AI-Assisted Software Development |
| [ch17.sh](ch17.sh) | 17 | Policy as Code |
| [ch18.sh](ch18.sh) | 18 | Compliance as Code |
| [ch19.sh](ch19.sh) | 19 | Security Testing at Scale |
| [ch20.sh](ch20.sh) | 20 | Continuous Risk Management |
| [ch21.sh](ch21.sh) | 21 | SOAR and Automated Remediation |
| [ch22.sh](ch22.sh) | 22 | Observability for Security |
| [ch23.sh](ch23.sh) | 23 | Detection Engineering |
| [ch24.sh](ch24.sh) | 24 | Threat Hunting |
| [ch25.sh](ch25.sh) | 25 | Incident Response Engineering |
| [ch26.sh](ch26.sh) | 26 | Cyber Resilience Engineering |
| [ch27.sh](ch27.sh) | 27 | Chaos Security Engineering |
| [ch28.sh](ch28.sh) | 28 | AI for Security Operations |
| [ch29.sh](ch29.sh) | 29 | Securing AI Systems |
| [ch30.sh](ch30.sh) | 30 | RAG Security Engineering |
| [ch31.sh](ch31.sh) | 31 | Agent Security Engineering |
| [ch32.sh](ch32.sh) | 32 | AI Supply Chain Security |
| [ch33.sh](ch33.sh) | 33 | Autonomous Remediation |
| [ch34.sh](ch34.sh) | 34 | Building a Modern Security Program |
| [ch35.sh](ch35.sh) | 35 | Security Metrics That Matter |
| [ch36.sh](ch36.sh) | 36 | Defending Tomorrow |

## Safety and cost

- Use accounts you own that hold nothing else, never an employer's or client's account.
- Each exercise states its cost in the book and ends with cleanup. Every Azure resource goes into the `rg-dt-labs` resource group, so `az group delete --name rg-dt-labs` removes anything you missed.
- On AWS, creating an organisation (Chapter 5) upgrades a free-plan account to the paid plan. Those steps are marked **PAID ACCOUNT PLAN ONLY**.
- Services, prices and free offers change. Nothing here is promised to remain free.

Validation status: every AWS command was checked against the AWS service models (botocore 1.43) and every Azure command against Azure CLI 2.90 help, including parameter names and JMESPath queries. Scripts pass `bash -n`. They have not been executed against live accounts by the maintainer; report problems as issues.
