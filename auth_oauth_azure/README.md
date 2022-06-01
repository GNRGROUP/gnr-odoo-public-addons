# Auth OAuth Azure

enable azure ad login support on odoo 14

## Config

1. Create new azure ad application with implicit flow.
2. Create new azure odoo provider  
2.1 Client ID: App Client ID  
2.2 Allowed: [x]  
2.3 Azure AD: [x]   
2.4 Authorization URL: `https://login.microsoftonline.com/.../v2.0/authorize`  
2.4 Scope: openid email  
2.5 Userinfo Url: `https://graph.microsoft.com/oidc/userinfo`
3. Config user to use azure provider with email as `OAuth User ID`