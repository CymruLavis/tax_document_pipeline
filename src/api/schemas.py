from pydantic import BaseModel, Field


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str = Field(
        description="The Access Token that can be sent to a Google API."
    )
    expires_in: int = Field(
        description="The lifetime of the Access Token in seconds, relative to the time the token was issued."
    )
    id_token: str = Field(
        description="A JSON Web Token (JWT) that contains identity information about the user. This token is returned during the initial Authorization Code exchange and can also be returned during a Refresh Token request if the openid scope was granted."
    )
    scope: str = Field(
        description="The scopes of access granted by the access_token expressed as a list of space-delimited, case-sensitive strings."
    )
    token_type: str = Field(description="The type of token returned. Always Bearer.")
    refresh_token: str | None = Field(
        description="A token that can be used to obtain new Access Tokens. This field is only returned in the initial exchange of an Authorization Code if access_type=offline was requested.",
        default=None,
    )
    refresh_token_expires_in: int | None = Field(
        description="The remaining lifetime of the Refresh Token in seconds. This value is only set when the user grants time-based access.",
        default=None,
    )


class OAuthError(Exception):
    pass


class OAuthTimeoutError(OAuthError):
    pass


class OAuthRequestError(OAuthError):
    pass


class OAuthStatusError(OAuthError):
    pass
