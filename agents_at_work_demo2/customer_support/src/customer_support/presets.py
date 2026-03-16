"""Canned customer-message presets for Demo 2."""

from __future__ import annotations


PRESETS: dict[str, dict[str, str]] = {
    "billing_lockout": {
        "description": "Finance team blocked from invoices before quarter-end close",
        "customer_name": "Northstar Health",
        "customer_tier": "enterprise",
        "channel": "email",
        "message": (
            "Hi support, after yesterday's login policy change our finance users can no "
            "longer access invoices or billing history. We are closing the quarter "
            "tomorrow morning and need this restored as soon as possible."
        ),
    },
    "sso_failure": {
        "description": "Large-scale Okta SSO failure blocking dozens of users",
        "customer_name": "Acme Manufacturing",
        "customer_tier": "strategic",
        "channel": "chat",
        "message": (
            "We enforced Okta SSO this morning and now about 40 operations users cannot "
            "log in. New hire onboarding is completely stalled and supervisors are asking "
            "for an ETA."
        ),
    },
    "integration_outage": {
        "description": "Slack-to-Jira workflow outage creating manual queue backlog",
        "customer_name": "BluePeak Software",
        "customer_tier": "growth",
        "channel": "email",
        "message": (
            "Since about 8:15 a.m. the Slack integration has stopped creating tickets in "
            "Jira. Our support queue is backing up and agents are manually re-entering "
            "requests to keep up."
        ),
    },
    "double_charge": {
        "description": "Controller reports duplicate billing and missing corrected invoice",
        "customer_name": "Summit Legal",
        "customer_tier": "business",
        "channel": "email",
        "message": (
            "Our controller found that we were billed twice this month, and the corrected "
            "invoice still is not available in the portal. Please fix this before weekly "
            "close on Friday."
        ),
    },
    "unclear_request": {
        "description": "Ambiguous admin-portal issue that could be permissions or a bug",
        "customer_name": "Cedar Grove College",
        "customer_tier": "standard",
        "channel": "web",
        "message": (
            "Something is off in the admin portal after the update. Some staff can still "
            "see records, others cannot, and a few buttons are greyed out. We are not "
            "sure if this is a permissions problem or a product bug."
        ),
    },
    "refund_escalation": {
        "description": "Executive complaint about delayed refund and missing response",
        "customer_name": "Harbor Freight Analytics",
        "customer_tier": "enterprise",
        "channel": "email",
        "message": (
            "I am forwarding this on behalf of our CFO. We requested a refund for the "
            "cancelled workspace two weeks ago and have not received confirmation or a "
            "timeline. Please treat this as urgent."
        ),
    },
    "api_regression": {
        "description": "Production API regression after release affecting customer workflow",
        "customer_name": "Westlake Bank",
        "customer_tier": "strategic",
        "channel": "chat",
        "message": (
            "After today's release our API calls to create onboarding workflows are "
            "returning 500 errors in production. We have already paused customer "
            "activations and need engineering to investigate immediately."
        ),
    },
}


DEFAULT_PRESET = "billing_lockout"


def preset_names() -> list[str]:
    return sorted(PRESETS.keys())
