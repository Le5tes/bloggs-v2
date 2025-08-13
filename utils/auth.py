import json
import jwt
import requests
from jwt.algorithms import RSAAlgorithm

class CognitoAuth:
    def __init__(self, user_pool_id, region='eu-west-2'):
        self.user_pool_id = user_pool_id
        self.region = region
        self.issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
        self.jwks_url = f"{self.issuer}/.well-known/jwks.json"
        self._jwks = None
    
    def get_jwks(self):
        """Get the JSON Web Key Set from Cognito"""
        if not self._jwks:
            response = requests.get(self.jwks_url)
            self._jwks = response.json()
        return self._jwks
    
    def verify_token(self, token):
        """
        Verify a JWT token from Cognito
        Returns the decoded token payload if valid, None if invalid
        """
        try:
            # Decode the header to get the key ID
            header = jwt.get_unverified_header(token)
            kid = header['kid']
            
            # Find the matching key in JWKS
            jwks = self.get_jwks()
            key = None
            for jwk in jwks['keys']:
                if jwk['kid'] == kid:
                    key = RSAAlgorithm.from_jwk(json.dumps(jwk))
                    break
            
            if not key:
                return None
            
            # Verify and decode the token
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                issuer=self.issuer,
                options={'verify_aud': False}  # We'll verify audience manually if needed
            )
            
            return payload
            
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None
