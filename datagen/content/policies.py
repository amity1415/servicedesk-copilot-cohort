"""IT policies. Ten current documents; two also exist in a superseded version.

The superseded versions differ in exactly the clauses listed at the bottom of
this file, so retrieval tests can check that an answer comes from the current
version (for example: 14 characters, not 12).
"""

from datetime import date

from datagen.docmodel import Policy, Section, earlier_version

S = Section

ACCEPTABLE_USE = Policy(
    id="POL-001",
    title="Acceptable Use Policy",
    version="3.0",
    effective=date(2025, 9, 1),
    owner="Chief Information Security Officer",
    purpose="This policy sets out how Larkhaven Group systems, devices and information may be used.",
    scope="Everyone who uses a Larkhaven account or device: employees, contractors, temporary staff and partners.",
    sections=(
        S(
            "General use",
            (
                "Company systems are provided for business purposes. Limited personal use is allowed when it does not interfere with work, add cost or breach this policy.",
                "Each person is responsible for all activity carried out under their account.",
                "Accounts and passwords must not be shared with anyone, including managers, assistants and IT staff.",
                "Screens must be locked when unattended. Devices lock automatically after 5 minutes without activity.",
            ),
        ),
        S(
            "Prohibited use",
            (
                "Storing, sending or viewing material that is illegal, harassing or offensive.",
                "Bypassing or disabling security controls, including the use of anonymisers, personal VPN services or proxy tools not supplied by IT.",
                "Installing software that is not in the software catalogue.",
                "Using personal email accounts or personal cloud storage for company information.",
                "Connecting devices that are not managed by IT to the LarkNet office network.",
                "Using company systems for commercial activity unrelated to Larkhaven Group.",
            ),
        ),
        S(
            "Email and messaging",
            (
                "Business communication takes place in company email and Microsoft Teams.",
                "Automatic forwarding of company email to an external address is prohibited.",
                "Suspicious messages must be reported with the Report phishing button and must not be forwarded.",
            ),
        ),
        S(
            "Artificial intelligence tools",
            (
                "Only the AI assistants listed in the software catalogue may be used with company information.",
                "Confidential and Restricted information must not be entered into any AI service that is not listed in the software catalogue.",
                "Output from an AI assistant must be reviewed by the person who uses it; that person remains accountable for the result.",
            ),
        ),
        S(
            "Monitoring",
            (
                "Larkhaven Group logs and monitors the use of its systems for security, compliance and service quality, in line with local law.",
                "Monitoring data is available only to authorised staff and is kept for 12 months.",
            ),
        ),
    ),
    related=(
        "POL-003 Password and MFA Policy",
        "POL-005 Software Licensing and Installation Policy",
        "POL-007 Data Classification and Handling Policy",
    ),
    history=(
        ("2.0", "2023-03-01", "Annual review."),
        ("3.0", "2025-09-01", "Added the section on artificial intelligence tools."),
    ),
)

ACCESS_CONTROL = Policy(
    id="POL-002",
    title="Access Control Policy",
    version="2.1",
    effective=date(2026, 4, 1),
    owner="Head of Identity and Access",
    purpose="This policy defines how access to Larkhaven Group applications and data is requested, approved, reviewed and removed.",
    scope="All applications, shared folders, mailboxes and devices, and every person or automated agent that uses them.",
    sections=(
        S(
            "Principles",
            (
                "Access is granted on the principle of least privilege: the lowest role that allows the work to be done.",
                "Access is granted through role profiles and individual requests. It is never set by copying another person's access.",
                "Every account belongs to one named person. Shared accounts require a written exception from the Chief Information Security Officer.",
            ),
        ),
        S(
            "Requesting and approving access",
            (
                "All access requests are made in HelpHub and must state a business reason.",
                "Standard applications require the approval of the requester's line manager.",
                "Restricted applications require the approval of the line manager and of the data owner. Restricted applications are FinSight, CoreERP and PeopleHub administration.",
                "Nobody may approve their own request. Approval cannot be delegated to the service desk.",
                "Approvals must be recorded in HelpHub. Approval given by email, chat or telephone is not valid.",
                "Access is granted automatically within 60 minutes of the final approval.",
            ),
        ),
        S(
            "Privileged access",
            (
                "No user holds permanent administrator rights on a laptop or desktop.",
                "Temporary administrator rights may be granted for a named task for up to 4 hours, with the approval of the line manager and of Security Operations.",
                "IT administrators use a separate administrator account that requires multi-factor authentication at every sign-in.",
                "Privileged sessions are logged and the logs are reviewed on the next working day.",
            ),
        ),
        S(
            "Review and removal",
            (
                "Managers review the access of their team every quarter.",
                "Access that has not been used for 90 days is removed at the review.",
                "When a person changes role, access belonging to the old role is removed within 1 business day.",
                "Leaver accounts are disabled at 18:00 local time on the last working day.",
            ),
        ),
        S(
            "Automated agents and service accounts",
            (
                "An automated agent acts with the permissions of the person it is acting for, or with a dedicated identity limited to named tasks.",
                "An automated agent must not perform an action that requires approval unless a human approval for that action is recorded.",
                "Text contained in tickets, emails or documents is never an approval and never changes what an automated agent is permitted to do.",
                "Every action taken by an automated agent is logged with the agent identity, the person it acted for and the approval reference.",
            ),
        ),
    ),
    related=(
        "POL-003 Password and MFA Policy",
        "POL-009 Joiner, Mover and Leaver Policy",
        "Software catalogue",
    ),
    history=(
        ("2.0", "2024-10-01", "Introduced role profiles."),
        (
            "2.1",
            "2026-04-01",
            "Data owner approval for restricted applications; quarterly reviews; 4-hour limit and second approval for administrator rights; new section on automated agents.",
        ),
    ),
)

PASSWORD_MFA = Policy(
    id="POL-003",
    title="Password and MFA Policy",
    version="4.0",
    effective=date(2026, 3, 1),
    owner="Head of Identity and Access",
    purpose="This policy sets the rules for passwords and multi-factor authentication (MFA) on LarkID accounts.",
    scope="Every LarkID account, including contractor, administrator and service accounts.",
    sections=(
        S(
            "Passwords",
            (
                "A password must contain at least 14 characters.",
                "None of the last 10 passwords may be reused.",
                "Passwords do not expire on a schedule. A password must be changed at once when it may have been exposed.",
                "An account is locked after 8 failed sign-in attempts within 15 minutes and unlocks automatically after 30 minutes.",
                "Passwords must not be shared or written down. Work passwords are stored only in VaultKey.",
                "IT staff never ask for a password.",
            ),
        ),
        S(
            "Multi-factor authentication",
            (
                "MFA is required for every sign-in from outside the office network and for every administrator action.",
                "The approved methods are LarkID Authenticator with number matching and FIDO2 security keys.",
                "Codes sent by text message or voice call are not an approved method.",
                "A temporary access pass is single use and valid for at most 60 minutes, or 8 hours when issued for a new joiner.",
            ),
        ),
        S(
            "Resets and recovery",
            (
                "Self-service password reset requires an MFA approval.",
                "A reset assisted by the service desk requires identity verification by an approved method: an Authenticator approval, a video call with the line manager present, or a badge shown at a Tech Bar.",
                "An MFA reset requires the approval of a second Identity and Access analyst.",
                "Disk recovery keys are released only to the verified owner of the device.",
            ),
        ),
        S(
            "Shared and service credentials",
            (
                "Credentials used by a team are stored in a VaultKey shared vault.",
                "Shared and service credentials are changed every 180 days and whenever a person with access leaves the team.",
            ),
        ),
    ),
    related=(
        "POL-002 Access Control Policy",
        "POL-010 Security Incident Reporting and Response Policy",
    ),
    history=(
        ("3.2", "2024-06-01", "Annual review."),
        (
            "4.0",
            "2026-03-01",
            "Minimum length raised to 14; scheduled expiry removed; text-message codes withdrawn; lockout threshold changed to 8 attempts.",
        ),
    ),
)

DEVICE = Policy(
    id="POL-004",
    title="Device and Endpoint Policy",
    version="2.3",
    effective=date(2025, 11, 1),
    owner="Head of Workplace Engineering",
    purpose="This policy covers the issue, protection, replacement and return of laptops and desktops.",
    scope="All laptops and desktops owned by Larkhaven Group and the people who use them.",
    sections=(
        S(
            "Standard devices",
            (
                "The supported operating systems are Windows 11 and macOS 15 or later.",
                "Laptops are replaced after 48 months.",
                "A laptop is replaced earlier when the repair cost exceeds 50 percent of the replacement cost, or when IT confirms that its specification is the cause of a performance problem.",
                "Each person has one laptop. Loan devices are returned within 5 business days.",
            ),
        ),
        S(
            "Security baseline",
            (
                "Full-disk encryption with BitLocker or FileVault is mandatory.",
                "EndpointShield must be running with definitions no more than 7 days old.",
                "Security updates are installed within 14 days of release and critical updates within 7 days.",
                "A device more than 30 days behind on updates is blocked from the VPN and from the office network.",
            ),
        ),
        S(
            "Care and loss",
            (
                "A lost or stolen device must be reported within 2 hours of discovery.",
                "Devices must not be left unattended in vehicles or public places.",
                "IT may lock a device at any time. A full wipe requires the approval of the IT duty manager.",
            ),
        ),
        S(
            "Return and disposal",
            (
                "Devices are returned within 5 business days of leaving the company or receiving a replacement.",
                "Returned devices are wiped, then reissued or recycled by a certified disposal partner.",
            ),
        ),
    ),
    related=("POL-006 Remote Work and VPN Policy", "POL-008 Mobile Device and BYOD Policy"),
    history=(
        ("2.2", "2024-11-01", "Annual review."),
        (
            "2.3",
            "2025-11-01",
            "Supported macOS versions updated; early replacement rule clarified.",
        ),
    ),
)

SOFTWARE = Policy(
    id="POL-005",
    title="Software Licensing and Installation Policy",
    version="2.0",
    effective=date(2025, 7, 1),
    owner="IT Asset Manager",
    purpose="This policy ensures that software used at Larkhaven Group is secure, licensed and paid for.",
    scope="All software installed on company devices or used with company information, including browser extensions and web services.",
    sections=(
        S(
            "Approved software",
            (
                "Only software listed in the software catalogue may be installed or used.",
                "Software is installed through App Hub.",
                "Software that is not in the catalogue requires a security and legal review, which takes up to 10 business days.",
                "Open-source software is permitted under permissive licences after the same review.",
            ),
        ),
        S(
            "Licences and approval",
            (
                "Software with an annual charge under USD 300 requires the approval of the line manager.",
                "Software with an annual charge of USD 300 or more requires the approval of the line manager and of the cost-centre owner.",
                "Software that handles Restricted information also requires the approval of the data owner.",
                "A licence is assigned to one named person and must not be shared.",
            ),
        ),
        S(
            "Reclaiming licences",
            (
                "A licence that has not been used for 60 days is reclaimed after a warning sent 7 days before.",
                "Licences held by leavers return to the pool on the last working day.",
            ),
        ),
        S(
            "Prohibited software",
            (
                "Personal licences, trial versions and unlicensed copies must not be installed on company devices.",
                "Unapproved software is removed automatically 5 business days after the user is notified.",
            ),
        ),
    ),
    related=("POL-001 Acceptable Use Policy", "Software catalogue"),
    history=(
        ("1.4", "2023-07-01", "Annual review."),
        (
            "2.0",
            "2025-07-01",
            "Approval thresholds aligned with the software catalogue; 60-day reclaim introduced.",
        ),
    ),
)

REMOTE_WORK = Policy(
    id="POL-006",
    title="Remote Work and VPN Policy",
    version="1.4",
    effective=date(2025, 5, 1),
    owner="Head of Network Operations",
    purpose="This policy sets the conditions for working away from a Larkhaven Group office.",
    scope="Everyone who connects to company systems from outside an office.",
    sections=(
        S(
            "Remote access",
            (
                "Internal systems are reached only through the SecureTunnel VPN on a company-managed device.",
                "Every VPN connection requires MFA and a device check covering encryption, endpoint protection and updates.",
                "A VPN session ends after 12 hours, or after 30 minutes without activity.",
                "Split tunnelling is used only for approved conferencing traffic.",
            ),
        ),
        S(
            "Networks",
            (
                "Public Wi-Fi may be used only with the VPN connected.",
                "Home routers should use WPA2 or better and a password that is not the factory default.",
            ),
        ),
        S(
            "Working abroad",
            (
                "Travel to a country on the high-risk list requires a travel request at least 5 business days before departure; loan devices are issued.",
                "Working from another country for more than 30 days requires the approval of HR and Legal.",
            ),
        ),
        S(
            "The remote workplace",
            (
                "The laptop must not be used by family members or left unlocked.",
                "Work documents must not be printed at home.",
                "Calls about Confidential or Restricted matters must not be held in public places.",
            ),
        ),
    ),
    related=(
        "POL-004 Device and Endpoint Policy",
        "POL-007 Data Classification and Handling Policy",
    ),
    history=(
        ("1.3", "2024-05-01", "Session limits introduced."),
        ("1.4", "2025-05-01", "Device check extended to update status."),
    ),
)

DATA_CLASSIFICATION = Policy(
    id="POL-007",
    title="Data Classification and Handling Policy",
    version="3.1",
    effective=date(2025, 2, 1),
    owner="Data Protection Officer",
    purpose="This policy defines four classes of information and how each must be handled.",
    scope="All information created, received or held by Larkhaven Group, in any form.",
    sections=(
        S(
            "Classes of information",
            (
                "Public: information approved for release to anyone.",
                "Internal: everyday business information. This is the default class for unlabelled documents.",
                "Confidential: information whose disclosure would harm the company, its customers or its employees, including contracts, pricing and personal data.",
                "Restricted: the most sensitive information, including unpublished financial results, payroll, credentials and security details.",
            ),
        ),
        S(
            "Handling rules",
            (
                "The handling rules for each class are set out in the table below.",
                "Where two rules could apply, the stricter rule applies.",
            ),
            table=(
                ("Class", "Storage", "Sharing outside the company", "Removable media", "Printing"),
                (
                    ("Public", "Any company system", "Allowed", "Allowed", "Allowed"),
                    (
                        "Internal",
                        "Any company system",
                        "With a business reason",
                        "Allowed on encrypted media",
                        "Allowed in the office",
                    ),
                    (
                        "Confidential",
                        "OneDrive, shared folders, approved applications",
                        "SendSafe only",
                        "Approved exception only",
                        "Badge release only",
                    ),
                    (
                        "Restricted",
                        "Named application or folder only",
                        "Data owner's written approval and SendSafe",
                        "Never",
                        "Never",
                    ),
                ),
            ),
        ),
        S(
            "Labelling and ownership",
            (
                "Documents classed Confidential or Restricted carry a label in the header.",
                "The data owner decides the class of the information they are responsible for.",
                "Anyone unsure of the class treats the information as Confidential and asks the data owner.",
            ),
        ),
        S(
            "Exposure",
            (
                "Suspected exposure of Confidential or Restricted information must be reported within 1 hour.",
            ),
        ),
    ),
    related=(
        "POL-001 Acceptable Use Policy",
        "POL-010 Security Incident Reporting and Response Policy",
    ),
    history=(
        ("3.0", "2024-02-01", "Four-class scheme introduced."),
        ("3.1", "2025-02-01", "Handling table extended to printing."),
    ),
)

MOBILE = Policy(
    id="POL-008",
    title="Mobile Device and BYOD Policy",
    version="1.2",
    effective=date(2025, 8, 1),
    owner="Head of Workplace Engineering",
    purpose="This policy sets the conditions under which phones and tablets, company-owned or personal, may hold company information.",
    scope="Every phone or tablet used to open company email, Teams or files.",
    sections=(
        S(
            "Enrolment",
            (
                "A phone or tablet must be enrolled in DeviceCare before it can open company information.",
                "The device must run one of the two latest major versions of its operating system.",
                "Rooted or jailbroken devices are blocked.",
                "The device must have a passcode of at least 6 digits and lock after no more than 5 minutes.",
            ),
        ),
        S(
            "Privacy on personal devices",
            (
                "IT can see the device model, operating system version, compliance status and the list of work applications.",
                "IT cannot see personal applications, photos, messages, browsing history or location.",
            ),
        ),
        S(
            "Loss and leaving",
            (
                "The work profile is removed remotely when a device is lost, when it has been non-compliant for 14 days, or when its owner leaves.",
                "A personal device is never wiped completely.",
                "A company-owned phone may be wiped completely with the approval of the IT duty manager.",
            ),
        ),
        S(
            "Costs",
            (
                "Larkhaven Group does not pay for personal devices or personal data plans unless agreed in writing.",
            ),
        ),
    ),
    related=("POL-004 Device and Endpoint Policy",),
    history=(
        ("1.1", "2024-08-01", "Work profile model adopted for Android."),
        ("1.2", "2025-08-01", "Passcode length raised to 6 digits."),
    ),
)

JML = Policy(
    id="POL-009",
    title="Joiner, Mover and Leaver Policy",
    version="2.2",
    effective=date(2026, 1, 15),
    owner="Head of IT Service Management",
    purpose="This policy defines what IT does, and when, as people join, change role and leave.",
    scope="Employees, contractors and temporary staff.",
    sections=(
        S(
            "Joiners",
            (
                "HR creates the PeopleHub record before IT begins any work.",
                "The hiring manager submits the new joiner form at least 5 business days before the start date.",
                "Accounts are created 2 business days before the start date.",
                "Access is set from the role profile of the team.",
                "The temporary access pass is sent to the hiring manager, not to the joiner, and expires 8 hours after it is issued.",
            ),
        ),
        S(
            "Movers",
            (
                "The manager of the new role requests the new role profile.",
                "Access belonging to the old role is removed within 1 business day of the move.",
            ),
        ),
        S(
            "Leavers",
            (
                "The manager raises the leaver request as soon as the leaving date is agreed.",
                "The account is disabled at 18:00 local time on the last working day, or immediately at the request of HR.",
                "Equipment is returned within 5 business days.",
                "The mailbox is kept for 90 days. The manager may be given access on request, after HR confirms.",
            ),
        ),
        S(
            "Contractors",
            (
                "Every contractor account has a Larkhaven sponsor.",
                "A contractor account has an end date no more than 6 months ahead and may be renewed by the sponsor.",
                "The account is disabled automatically on the end date.",
            ),
        ),
    ),
    related=("POL-002 Access Control Policy", "POL-004 Device and Endpoint Policy"),
    history=(
        ("2.1", "2025-01-15", "Role profiles replace copied access."),
        ("2.2", "2026-01-15", "Lead time for the new joiner form set at 5 business days."),
    ),
)

INCIDENT = Policy(
    id="POL-010",
    title="Security Incident Reporting and Response Policy",
    version="2.0",
    effective=date(2025, 10, 1),
    owner="Chief Information Security Officer",
    purpose="This policy ensures that security incidents are reported quickly and handled consistently.",
    scope="Everyone who uses Larkhaven Group systems, and every suspected or confirmed security incident.",
    sections=(
        S(
            "Reporting",
            (
                "Anyone who suspects a security incident must report it within 1 hour of noticing it.",
                "Incidents are reported by telephone to the service desk or, for suspicious email, with the Report phishing button.",
                "A lost or stolen device must be reported within 2 hours.",
                "Nobody is penalised for reporting their own mistake in good faith.",
            ),
        ),
        S(
            "Severity",
            (
                "Security Operations assigns a severity when the incident is confirmed, using the table below.",
            ),
            table=(
                ("Severity", "Meaning", "Acknowledged within"),
                (
                    (
                        "1",
                        "Restricted information exposed, or several systems compromised",
                        "15 minutes",
                    ),
                    (
                        "2",
                        "One account or device compromised, or Confidential information exposed",
                        "1 hour",
                    ),
                    ("3", "An attack was blocked, or a control failed without loss", "4 hours"),
                    ("4", "A policy breach with no sign of attack", "1 business day"),
                ),
            ),
        ),
        S(
            "Response",
            (
                "Security Operations may isolate a device or disable an account without notice.",
                "Users must not switch off, wipe or attempt to clean an affected device.",
                "Communication during an incident is led by the incident manager.",
            ),
        ),
        S(
            "Review",
            (
                "A review is completed within 5 business days of every severity 1 or severity 2 incident.",
            ),
        ),
    ),
    related=(
        "POL-004 Device and Endpoint Policy",
        "POL-007 Data Classification and Handling Policy",
    ),
    history=(
        ("1.3", "2024-10-01", "Annual review."),
        ("2.0", "2025-10-01", "Severity table and acknowledgement times introduced."),
    ),
)

ACCESS_CONTROL_V2_0 = earlier_version(
    ACCESS_CONTROL,
    version="2.0",
    effective=date(2024, 10, 1),
    changes={
        "Restricted applications require the approval of the line manager and of the data owner. Restricted applications are FinSight, CoreERP and PeopleHub administration.": "Restricted applications require the approval of the line manager. Restricted applications are FinSight, CoreERP and PeopleHub administration.",
        "Approvals must be recorded in HelpHub. Approval given by email, chat or telephone is not valid.": "Approvals should be recorded in HelpHub. An email from the approver may be attached to the request as evidence of approval.",
        "Temporary administrator rights may be granted for a named task for up to 4 hours, with the approval of the line manager and of Security Operations.": "Temporary administrator rights may be granted for up to 8 hours with the approval of the line manager.",
        "Managers review the access of their team every quarter.": "Managers review the access of their team twice a year.",
    },
    drop_sections=("Automated agents and service accounts",),
)

PASSWORD_MFA_V3_2 = earlier_version(
    PASSWORD_MFA,
    version="3.2",
    effective=date(2024, 6, 1),
    changes={
        "A password must contain at least 14 characters.": "A password must contain at least 12 characters, including a number and a symbol.",
        "None of the last 10 passwords may be reused.": "None of the last 5 passwords may be reused.",
        "Passwords do not expire on a schedule. A password must be changed at once when it may have been exposed.": "Passwords expire every 90 days.",
        "An account is locked after 8 failed sign-in attempts within 15 minutes and unlocks automatically after 30 minutes.": "An account is locked after 5 failed sign-in attempts and unlocks automatically after 30 minutes.",
        "MFA is required for every sign-in from outside the office network and for every administrator action.": "MFA is required for remote access through the VPN.",
        "Codes sent by text message or voice call are not an approved method.": "Codes sent by text message may be used as a backup method.",
        "An MFA reset requires the approval of a second Identity and Access analyst.": None,
    },
)

CURRENT = (
    ACCEPTABLE_USE,
    ACCESS_CONTROL,
    PASSWORD_MFA,
    DEVICE,
    SOFTWARE,
    REMOTE_WORK,
    DATA_CLASSIFICATION,
    MOBILE,
    JML,
    INCIDENT,
)
SUPERSEDED = (ACCESS_CONTROL_V2_0, PASSWORD_MFA_V3_2)
ALL = CURRENT + SUPERSEDED
