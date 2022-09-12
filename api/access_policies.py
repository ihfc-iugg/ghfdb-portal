from rest_access_policy import AccessPolicy

# Principal: *, admin, staff, authenticated, anonymous, group:name, id:id

class SiteAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["<safe_methods>"],
            "principal": ["authenticated","anonymous"],
            "effect": "allow"
        },
        {
            # "action": ["*"],
            "action": ["<safe_methods>"],
            "principal": ["admin","staff","group:Reviewer"],
            "effect": "allow"
        },
    ]
