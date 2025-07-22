"""
Service layer for GoHighLevel (GHL) integration.
Handles OAuth flows, API interactions, and webhook processing.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import httpx
from pydantic import HttpUrl, ValidationError

from .models import (
    GHLAccount,
    GHLAccountStatus,
    GHLSubaccount,
    GHLWebhookEvent,
    GHLWebhookEventType,
)
from .exceptions import (
    GHLAPIError,
    GHLConnectionError,
    GHLAuthorizationError,
    GHLValidationError,
    GHLWebhookError,
)

logger = logging.getLogger(__name__)

# GHL API endpoints
GHL_API_BASE = "https://services.leadconnectorhq.com"
GHL_AUTH_URL = "https://marketplace.gohighlevel.com/oauth/chooselocation"
GHL_TOKEN_URL = "https://services.leadconnectorhq.com/oauth/token"
GHL_API_VERSION = "2021-07-28"


class GHLService:
    """Service for interacting with GoHighLevel API."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        api_version: str = GHL_API_VERSION,
        timeout: int = 30,
    ):
        """Initialize the GHL service with OAuth credentials.
        
        Args:
            client_id: GHL OAuth client ID
            client_secret: GHL OAuth client secret
            redirect_uri: OAuth redirect URI
            api_version: GHL API version to use
            timeout: Request timeout in seconds
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.api_version = api_version
        self.timeout = timeout
        self._http_client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self._http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def get_authorization_url(
        self, 
        user_id: str,
        scopes: Optional[List[str]] = None,
        state: Optional[str] = None,
    ) -> str:
        """Generate the GHL OAuth authorization URL.
        
        Args:
            user_id: Internal user ID for state tracking
            scopes: List of OAuth scopes to request
            state: Optional custom state string
            
        Returns:
            str: The full authorization URL
        """
        if scopes is None:
            scopes = [
                "conversations/message.readonly",
                "conversations/message.write",
                "contacts.readonly",
                "contacts.write",
                "calendars/events.readonly",
                "calendars/events.write",
                "calendars/events.free-busy",
                "calendars/settings.readonly",
                "calendars/settings.write",
                "users/account.readonly",
                "users/account.write",
                "users/account.manage",
            ]
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state or user_id,
            "user_type": "Location",
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{GHL_AUTH_URL}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange an authorization code for an access token.
        
        Args:
            code: OAuth authorization code
            
        Returns:
            Dict containing access token, refresh token, and expiration
            
        Raises:
            GHLAPIError: If the token exchange fails
            GHLConnectionError: If there's a network error
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        
        try:
            response = await self._http_client.post(
                GHL_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GHL token exchange failed: {e.response.text}")
            raise GHLAPIError(
                f"Failed to exchange code for token: {e.response.text}",
                status_code=e.response.status_code,
                response=e.response.json()
            )
        except httpx.RequestError as e:
            logger.error(f"GHL connection error during token exchange: {str(e)}")
            raise GHLConnectionError(f"Failed to connect to GHL: {str(e)}")

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token.
        
        Args:
            refresh_token: The refresh token from the initial OAuth flow
            
        Returns:
            Dict containing new access token and expiration
            
        Raises:
            GHLAPIError: If the token refresh fails
            GHLAuthorizationError: If the refresh token is invalid or expired
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        
        try:
            response = await self._http_client.post(
                GHL_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 400:
                error_data = response.json()
                if error_data.get("error") == "invalid_grant":
                    raise GHLAuthorizationError("Refresh token is invalid or expired")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"GHL token refresh failed: {e.response.text}")
            raise GHLAPIError(
                f"Failed to refresh token: {e.response.text}",
                status_code=e.response.status_code,
                response=e.response.json()
            )
        except httpx.RequestError as e:
            logger.error(f"GHL connection error during token refresh: {str(e)}")
            raise GHLConnectionError(f"Failed to connect to GHL: {str(e)}")

    async def get_account_info(self, access_token: str) -> Dict[str, Any]:
        """Get information about the authenticated GHL account.
        
        Args:
            access_token: Valid GHL access token
            
        Returns:
            Dict containing account information
            
        Raises:
            GHLAPIError: If the request fails
            GHLAuthorizationError: If the access token is invalid
        """
        try:
            response = await self._http_client.get(
                f"{GHL_API_BASE}/v1/users/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Version": self.api_version,
                    "Accept": "application/json",
                }
            )
            
            if response.status_code == 401:
                raise GHLAuthorizationError("Invalid or expired access token")
                
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get GHL account info: {e.response.text}")
            raise GHLAPIError(
                f"Failed to get account info: {e.response.text}",
                status_code=e.response.status_code,
                response=e.response.json()
            )
        except httpx.RequestError as e:
            logger.error(f"GHL connection error getting account info: {str(e)}")
            raise GHLConnectionError(f"Failed to connect to GHL: {str(e)}")

    async def get_location_info(self, access_token: str, location_id: str) -> Dict[str, Any]:
        """Get information about a specific location.
        
        Args:
            access_token: Valid GHL access token
            location_id: GHL location ID
            
        Returns:
            Dict containing location information
            
        Raises:
            GHLAPIError: If the request fails
            GHLAuthorizationError: If the access token is invalid
        """
        try:
            response = await self._http_client.get(
                f"{GHL_API_BASE}/v1/locations/{location_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Version": self.api_version,
                    "Accept": "application/json",
                }
            )
            
            if response.status_code == 401:
                raise GHLAuthorizationError("Invalid or expired access token")
                
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get GHL location info: {e.response.text}")
            raise GHLAPIError(
                f"Failed to get location info: {e.response.text}",
                status_code=e.response.status_code,
                response=e.response.json()
            )
        except httpx.RequestError as e:
            logger.error(f"GHL connection error getting location info: {str(e)}")
            raise GHLConnectionError(f"Failed to connect to GHL: {str(e)}")

    async def process_webhook_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None,
        secret: Optional[str] = None,
    ) -> GHLWebhookEvent:
        """Process a webhook event from GHL.
        
        Args:
            event_type: Type of webhook event
            payload: Raw webhook payload
            signature: Optional signature for verification
            secret: Optional webhook secret for verification
            
        Returns:
            GHLWebhookEvent: The processed webhook event
            
        Raises:
            GHLWebhookError: If the webhook is invalid or processing fails
            GHLValidationError: If the webhook data is invalid
        """
        try:
            # Verify signature if secret is provided
            if secret and signature:
                self._verify_webhook_signature(payload, signature, secret)
            
            # Parse the event type
            try:
                event_type_enum = GHLWebhookEventType(event_type)
            except ValueError:
                raise GHLValidationError(f"Unknown webhook event type: {event_type}")
            
            # Extract common fields
            location_id = payload.get("locationId")
            if not location_id:
                raise GHLValidationError("Missing required field: locationId")
                
            resource_id = payload.get("resourceId") or payload.get("id")
            if not resource_id:
                raise GHLValidationError("Missing required field: resourceId or id")
            
            # Create and return the webhook event
            return GHLWebhookEvent(
                event_type=event_type_enum,
                ghl_account_id=payload.get("accountId", ""),
                location_id=location_id,
                resource_id=str(resource_id),
                payload=payload,
            )
            
        except Exception as e:
            logger.error(f"Failed to process GHL webhook: {str(e)}", exc_info=True)
            if isinstance(e, (GHLWebhookError, GHLValidationError)):
                raise
            raise GHLWebhookError(
                f"Failed to process webhook: {str(e)}",
                event_data=payload
            )
    
    def _verify_webhook_signature(
        self, 
        payload: Dict[str, Any], 
        signature: str, 
        secret: str
    ) -> bool:
        """Verify the webhook signature.
        
        Args:
            payload: The webhook payload
            signature: The signature to verify
            secret: The webhook secret
            
        Returns:
            bool: True if the signature is valid
            
        Raises:
            GHLWebhookError: If the signature is invalid
        """
        # TODO: Implement signature verification
        # This should verify the signature using HMAC-SHA256
        # For now, we'll just log a warning and continue
        logger.warning(
            "Webhook signature verification not implemented. "
            "Please implement _verify_webhook_signature in production."
        )
        return True
