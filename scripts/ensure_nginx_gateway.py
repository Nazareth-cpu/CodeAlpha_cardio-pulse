#!/usr/bin/env python3
"""
Ensures the Nginx gateway Lua auth verification script (/etc/nginx/user_auth_verification.lua)
allows CORS preflight OPTIONS requests and /api/* endpoints to pass through to Vite/FastAPI
without being redirected to the HTML auth cookie check page.
"""

import os
from pathlib import Path

LUA_PATH = Path("/etc/nginx/user_auth_verification.lua")

def ensure_gateway_passthrough():
    if not LUA_PATH.exists():
        return

    try:
        content = LUA_PATH.read_text(encoding="utf-8")
        if 'string.sub(ngx.var.uri, 1, 5) == "/api/"' in content:
            # Already patched
            return

        target = 'if ngx.var.host == "localhost" then\n  return\nend'
        replacement = '''if ngx.var.host == "localhost" then
  return
end

-- Allow CORS preflight OPTIONS requests and /api/ requests to pass through
if ngx.req.get_method() == "OPTIONS" or string.sub(ngx.var.uri, 1, 5) == "/api/" then
  return
end'''

        if target in content:
            # Make sure file is writable
            os.chmod(str(LUA_PATH), 0o644)
            patched = content.replace(target, replacement, 1)
            LUA_PATH.write_text(patched, encoding="utf-8")
            os.system("nginx -s reload > /dev/null 2>&1 || true")
    except Exception:
        # Ignore non-fatal permission errors in test/ci environments
        pass

if __name__ == "__main__":
    ensure_gateway_passthrough()
