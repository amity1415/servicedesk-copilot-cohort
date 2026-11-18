# Personas

Eight fixed employees stand behind the acceptance requests in the build plan.
They are regenerated identically by `python -m datagen`, whatever the seed.

| Persona | Employee | Name | Role | Office | Laptop | Used for |
| --- | --- | --- | --- | --- | --- | --- |
| `mac_user` | E1261 | Priya Nair | Content Strategist, Marketing (employee) | London | LH-L-00261: MacBook Air 13 (M2), 16 GB | Request 1: VPN set-up on a Mac |
| `windows_user` | E1068 | Daniel Brooks | Account Executive, Sales (employee) | Chicago | LH-L-00068: Dell Latitude 5440, 16 GB | Request 2: VPN error 809 on Windows |
| `slow_laptop` | E1166 | Arjun Mehta | Logistics Coordinator, Operations (employee) | Bengaluru | LH-L-00166: Dell Latitude 5400, 8 GB | Request 3: slow laptop (8 GB, 66 months old, 38 days unpatched) |
| `finance_analyst` | E1237 | Sofia Rossi | Financial Analyst, Finance (employee) | Toronto | LH-L-00237: Lenovo ThinkPad T14 Gen 4, 16 GB | Request 4: needs FinSight; has no licence yet |
| `hiring_manager` | E1062 | Lukas Becker | Sales Manager, Sales (employee) | Munich | LH-L-00062: HP EliteBook 840 G10, 16 GB | Request 5: new joiner starting Monday 16 November 2026 |
| `injection_requester` | E1122 | Tom Whitfield | Support Specialist, Customer Support (employee) | Chicago | LH-L-00122: Dell Latitude 5440, 16 GB | Request 6: ticket text that tries to obtain administrator rights |
| `analyst` | E1203 | Grace Lin | Service Desk Analyst, IT (analyst) | Singapore | LH-L-00203: Lenovo ThinkPad T14 Gen 5, 16 GB | Approver on the approvals page (analyst role) |
| `admin` | E1218 | Marcus Hale | Systems Administrator, IT (admin) | Chicago | LH-L-00218: MacBook Pro 14 (M4), 32 GB | Administrator role for permission tests |

## Details the scenarios depend on

- Sofia Rossi's line manager is Samuel Rao (E1234), who approves her FinSight request. The Finance data owner is the Chief Financial Officer.
- FinSight has 60 licences and 58 are in use; two of those have been idle for more than 60 days.
- Microsoft Visio has 25 licences and all 25 are in use; one has been idle for 68 days.
- Lukas Becker's new joiner is Hannah Vogel (C-2041), starting 2026-11-16. Her PeopleHub record is complete. A second pending joiner has an incomplete record.
- Two incidents are open on the export date: SecureTunnel VPN is degraded in APAC and FollowMe Printing is down in EMEA.
- Arjun Mehta already has an open ticket, INC0020015 (Laptop fan very loud), waiting for his reply.
- Open ticket INC0020058 from the `injection_requester` persona contains an instruction addressed to the AI assistant. It is in `data/tickets/open_tickets.json`.
