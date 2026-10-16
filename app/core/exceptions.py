from fastapi import HTTPException, status


def invalid_credentials():

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password"
    )


def inactive_user():

    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account is inactive"
    )


def invalid_refresh_token():

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token"
    )


def password_mismatch():

    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Current password is incorrect"
    )