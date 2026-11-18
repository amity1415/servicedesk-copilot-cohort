"""Knowledge-base topics: joiners, leavers, remote work and general help."""

from datagen.model import EMAIL, GENERAL, MESSAGING, ONBOARD_TEAM, ONBOARDING, K, T

T(
    "new-joiner-day-one",
    "Your first day: IT checklist for new joiners",
    system="Onboarding",
    category=ONBOARDING,
    subcategory="New joiner",
    kind="how-to",
    summary="On day one you sign in with a temporary access pass, set a password and register your phone; everything else follows from that.",
    steps={
        "any": [
            "Collect your laptop from the Tech Bar or open the delivery box; your manager has your temporary access pass.",
            "Switch on, connect to Wi-Fi and sign in with your work email address and the temporary access pass.",
            "Set your LarkID password: at least 14 characters.",
            "Install LarkID Authenticator on your phone and register it when prompted.",
            "Open App Hub and install the applications listed under Recommended for your team.",
            "Open the LarkID portal to check that the applications your manager requested are there.",
            "Anything missing: ask your manager first, because access requests need their approval.",
        ]
    },
    notes=["The temporary access pass works once and expires 8 hours after it is issued."],
    group=ONBOARD_TEAM,
    policy="POL-009",
    ticket=K(
        shorts=[
            "New starter cannot log in",
            "First day laptop setup",
            "Temporary access pass expired",
            "New joiner missing access",
        ],
        descs=[
            "I started today and my temporary pass does not work on the laptop.",
            "New joiner here. I can sign in but I have no access to the team applications.",
            "My new team member started this morning and cannot sign in.",
        ],
        fixes=[
            "Temporary access pass had expired after 8 hours. Issued a new one after confirming with the manager; user signed in and registered MFA.",
            "Applications had not been requested in the new joiner form. Manager raised access requests.",
        ],
        weight=1.3,
        priority=(0, 18, 67, 15),
    ),
)

T(
    "manager-new-joiner-request",
    "Managers: request IT setup for a new joiner",
    system="Onboarding",
    category=ONBOARDING,
    subcategory="New joiner",
    kind="how-to",
    summary="Submit the new joiner form at least 5 business days before the start date; IT can begin only after HR has created the PeopleHub record.",
    steps={
        "any": [
            "Confirm with HR that the joiner's PeopleHub record exists and shows the correct start date; IT cannot create an account without it.",
            "In HelpHub choose New joiner and select the person from the PeopleHub list.",
            "Choose the laptop: Standard, or Developer with a business reason.",
            "Choose the role profile for the team; it sets the usual applications and access groups.",
            "Add anything beyond the profile as separate access requests; restricted applications still need the data owner.",
            "Say where the laptop goes: a Tech Bar for collection or a home address.",
            "Two business days before the start date you receive the temporary access pass to hand over on day one.",
        ]
    },
    notes=[
        "Requests made less than 5 business days ahead are handled as best effort and the laptop may be a loan device.",
        "Access is set from the role profile, never by copying another person's access.",
    ],
    group=ONBOARD_TEAM,
    policy="POL-009",
    ticket=K(
        shorts=[
            "New joiner starting Monday",
            "Set up new team member",
            "Onboarding request for new hire",
            "Laptop for new starter",
        ],
        descs=[
            "I have a new joiner starting Monday in Sales. Please set them up with a laptop and the usual access.",
            "New hire starts next week and I cannot find them in the new joiner form.",
            "Please arrange accounts and equipment for a contractor joining my team on the 1st.",
        ],
        fixes=[
            "PeopleHub record was missing. HR completed it; new joiner request then submitted and fulfilled before the start date.",
            "Request received 2 business days before start. Issued a loan laptop for week one; standard laptop followed.",
        ],
        weight=1.5,
        priority=(0, 10, 65, 25),
    ),
)

T(
    "leaver-return-equipment",
    "Leaving the company: accounts and equipment",
    system="Offboarding",
    category=ONBOARDING,
    subcategory="Leaver",
    kind="how-to",
    summary="Access ends at 18:00 local time on your last working day and equipment must be returned within 5 business days.",
    steps={
        "any": [
            "Your manager raises the leaver request in HelpHub as soon as the leaving date is agreed.",
            "Move work files that colleagues need from your OneDrive to the team's shared folder before your last day.",
            "Remove personal files from the laptop; IT does not recover them afterwards.",
            "Unenrol your personal phone in DeviceCare on your last day.",
            "Return laptop, charger, dock, phone and badge at a Tech Bar, or use the prepaid box sent to home workers.",
            "Your mailbox is kept for 90 days and your manager can ask for access to it.",
        ]
    },
    group=ONBOARD_TEAM,
    policy="POL-009",
    ticket=K(
        shorts=[
            "Leaver equipment return",
            "Employee leaving need account closed",
            "Access to leaver mailbox",
            "Return laptop from home",
        ],
        descs=[
            "A member of my team leaves on Friday. What do I need to do about their laptop and account?",
            "I need access to the mailbox of someone who left last month.",
        ],
        fixes=[
            "Leaver request raised by the manager. Account scheduled to disable at 18:00 on the last day; return box sent.",
            "Manager granted access to the leaver's mailbox for 30 days after HR confirmation.",
        ],
        weight=0.9,
        priority=(0, 5, 55, 40),
    ),
)

T(
    "contractor-accounts",
    "Accounts for contractors and temporary staff",
    system="Onboarding",
    category=ONBOARDING,
    subcategory="Contractor",
    kind="how-to",
    summary="A contractor account needs a Larkhaven sponsor and an end date no more than 6 months ahead.",
    steps={
        "any": [
            "The sponsoring manager chooses New contractor in HelpHub and gives the company, start date and end date.",
            "The end date can be at most 6 months ahead; the sponsor is asked to renew 14 days before it.",
            "Contractors get email, Teams and the applications the sponsor requests; remote access is a separate request.",
            "Contractors use a Larkhaven laptop unless their company's device has passed a security review.",
            "The account is disabled automatically on the end date.",
        ]
    },
    group=ONBOARD_TEAM,
    policy="POL-009",
    ticket=K(
        shorts=[
            "Contractor account extension",
            "New contractor account",
            "Contractor account disabled",
        ],
        descs=[
            "Our contractor's account stopped working this morning, the contract was extended.",
            "I need accounts for three agency staff starting next week.",
        ],
        fixes=[
            "Account had reached its end date. Sponsor renewed for a further 6 months; account re-enabled."
        ],
        weight=0.8,
        priority=(0, 10, 60, 30),
    ),
)

T(
    "remote-work-checklist",
    "Remote work set-up checklist",
    system="Remote work",
    category=GENERAL,
    subcategory="Remote work",
    kind="how-to",
    summary="What to check before your first day working away from the office.",
    steps={
        "any": [
            "Install SecureTunnel from App Hub and connect once while you are still in the office.",
            "Register LarkID Authenticator; remote sign-in always needs it.",
            "Take your charger and headset; docks and screens for home are requested in HelpHub.",
            "Check your home connection gives at least 5 Mbps download.",
            "Lock the screen whenever you step away and do not let family members use the laptop.",
            "Do not print work documents at home; home printers are not supported.",
        ]
    },
    policy="POL-006",
    ticket=K(
        shorts=[
            "Working from home setup",
            "Equipment for home office",
            "Can I get a monitor for home",
        ],
        descs=[
            "I start hybrid working next week. What do I need to set up?",
            "Can I have a second screen and dock for my home office?",
        ],
        fixes=[
            "Shared the remote work checklist. Home equipment request raised for a dock and screen with manager approval."
        ],
        weight=0.6,
        priority=(0, 0, 40, 60),
    ),
)

T(
    "support-hours-contacts",
    "IT support hours and how to reach the service desk",
    system="HelpHub",
    category=GENERAL,
    subcategory="Support information",
    kind="reference",
    summary="The {region_name} service desk is open {support_hours}; priority 1 and lost devices are handled 24 hours a day.",
    steps={
        "any": [
            "Raise and track tickets at https://helphub.larkhaven.example, at any time.",
            "Call {phone} when you cannot work at all, or to report a lost device or a security concern.",
            "Walk-up help is at the Tech Bar: {tech_bar}.",
            "Chat with the assistant in HelpHub for how-to questions; it can raise a ticket for you.",
            "Outside support hours, tickets are picked up the next business day unless they are priority 1.",
        ]
    },
    notes=["Applies to offices in {region_name}."],
    by_region=True,
    ticket=K(
        shorts=["What are the support hours", "Service desk phone number", "Where is the Tech Bar"],
        descs=[
            "What time does the IT service desk open in {office}?",
            "Is there someone I can see in person about my laptop?",
        ],
        fixes=["Shared regional support hours and Tech Bar location."],
        weight=0.6,
        priority=(0, 0, 25, 75),
    ),
)

T(
    "raise-a-ticket-howto",
    "Raise a good IT ticket",
    system="HelpHub",
    category=GENERAL,
    subcategory="Support information",
    kind="how-to",
    summary="A ticket with the right details is usually solved on the first reply; one without them waits for questions.",
    steps={
        "any": [
            "One problem per ticket.",
            "Say what you were trying to do, what happened instead and the exact error message or code.",
            "Say when it started and whether it worked before.",
            "Say whether colleagues are affected; that sets the priority.",
            "Add a screenshot of the error, not a photo of the whole desk.",
            "Never put a password in a ticket.",
        ]
    },
    notes=[
        "Priority is set by IT from impact and urgency. Writing 'urgent' does not change it; saying how many people are blocked does.",
    ],
    ticket=K(
        shorts=[
            "How do I raise a ticket",
            "Ticket status update",
            "No reply on my ticket",
            "Please escalate my ticket",
        ],
        descs=[
            "I raised a ticket three days ago and have heard nothing.",
            "How do I check the status of my request?",
            "Please escalate, this has been open for a week.",
        ],
        fixes=[
            "Ticket was waiting for the user's reply to a question. User answered; work resumed.",
            "Showed the user My requests in HelpHub. Ticket was within its target time.",
        ],
        weight=0.8,
        priority=(0, 2, 45, 53),
    ),
)

T(
    "teams-calling",
    "Make and receive phone calls in Teams",
    system="Microsoft Teams",
    category=EMAIL,
    subcategory="Teams",
    kind="how-to",
    summary="Desk phones have been replaced by calling in Teams; a direct number is assigned on request.",
    steps={
        "any": [
            "Open Teams and choose Calls; if there is no dial pad, you have no phone number yet.",
            "Request a number in HelpHub under Request telephony; your manager approves.",
            "Set voicemail and call forwarding under Settings, Calls.",
            "Use a certified headset; laptop speakers cause echo for the other side.",
            "Emergency calls from Teams report the address of your registered office, not your home.",
        ]
    },
    group=MESSAGING,
    ticket=K(
        shorts=[
            "No dial pad in Teams",
            "Need a phone number",
            "Cannot call external numbers from Teams",
        ],
        descs=[
            "I cannot call external numbers from Teams, there is no dial pad.",
            "Customers say my number goes straight to voicemail.",
        ],
        fixes=[
            "No calling licence assigned. Telephony request approved by the manager; number assigned and dial pad visible."
        ],
        weight=0.6,
        priority=(0, 5, 60, 35),
    ),
)

T(
    "peoplehub-signin",
    "Problems with PeopleHub, payslips or leave",
    system="PeopleHub",
    category=GENERAL,
    subcategory="HR system",
    kind="how-to",
    summary="PeopleHub is run by HR: IT fixes sign-in problems, and HR answers everything about its contents.",
    steps={
        "any": [
            "If PeopleHub does not open or rejects your sign-in, check that other LarkID applications work, then raise an IT ticket.",
            "For payslips, leave balances, job titles, managers or personal details, contact HR through the Ask HR tile in the LarkID portal.",
            "IT cannot see or change PeopleHub records.",
            "A wrong manager or job title elsewhere, such as in your email signature, is corrected by HR in PeopleHub and follows within 24 hours.",
        ]
    },
    ticket=K(
        shorts=[
            "Payslip not showing",
            "Leave balance wrong in PeopleHub",
            "Wrong manager in system",
            "Cannot open PeopleHub",
        ],
        descs=[
            "My leave balance is wrong in PeopleHub.",
            "I cannot see my payslip for last month.",
            "The org chart shows my old manager.",
        ],
        fixes=[
            "HR data question. Redirected the user to Ask HR and closed the IT ticket.",
            "Sign-in issue confirmed. Cleared the browser session and PeopleHub opened.",
        ],
        weight=1.0,
        priority=(0, 0, 40, 60),
    ),
)
