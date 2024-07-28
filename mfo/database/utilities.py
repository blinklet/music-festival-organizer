def find_primary_profile(user):
    return user.primary_profile

def find_primary_user(profile):
    return profile.user if profile.primary else None

def set_primary_profile(user, profile):
    # Unset the current primary profile if it exists
    if user.primary_profile:
        user.primary_profile.primary = False
    
    # Set the new primary profile
    profile.primary = True
    user.primary_profile = profile
    user.primary_profile_id = profile.id

    return user, profile