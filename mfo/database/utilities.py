def find_primary_profile(user):
    primary = None
    for profile in user.profiles:
        for u in profile.users:
            if u.id == user.id:
                primary = profile
    return primary

def find_primary_user(profile):
    primary = None
    for user in profile.users:
        for p in user.profiles:
            if p.id == user.id:
                primary = user
    return primary