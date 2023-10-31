from typing import Callable, Optional
from pydantic import conint
from starlette.requests import Request
from starlette.responses import Response
from redis.exceptions import NoScriptError

from limiter import CoreRateLimiter


class RateLimiter:
    def __init__(
        self,
        times: conint(ge=0) = 1,
        milliseconds: conint(ge=-1) = 0,
        seconds: conint(ge=-1) = 0,
        minutes: conint(ge=-1) = 0,
        hours: conint(ge=-1) = 0,
        identifier: Optional[Callable] = None,
        callback: Optional[Callable] = None,
    ) -> None:
        self.times = times
        self.milliseconds = milliseconds + 1000 * seconds + 60000 * minutes + 3600000 * hours
        self.identifier = identifier
        self.callback = callback

    async def _check(self, key):
        redis = CoreRateLimiter.redis
        pexpire = await redis.evalsha(
            CoreRateLimiter.lua_sha, 1, key, str(self.times), str(self.milliseconds)
        )
        return pexpire
    
    async def __call__(self, request: Request, response: Response):
        if not CoreRateLimiter.redis:
            raise Exception("You must call CoreRateLimiter.init in startup event of fastapi!")
        route_index = 0
        dep_index = 0
        for i, route in enumerate(request.app.routes):
            if route.path == request.scope["path"] and request.method in route.methods:
                route_index = i
                for j, dependency in enumerate(route.dependencies):
                    if self is dependency.dependency:
                        dep_index = j
                        break

        identifier = self.identifier or CoreRateLimiter.identifier
        callback = self.callback or CoreRateLimiter.http_callback
        rate_key = await identifier(request)
        key = f"{CoreRateLimiter.prefix}:{rate_key}:{route_index}:{dep_index}"
        try:
            pexpire = await self._check(key)
        except NoScriptError:
            CoreRateLimiter.lua_sha = await CoreRateLimiter.redis.script_load(
                CoreRateLimiter.lua_script
            )
            pexpire = await self._check(key)
        if pexpire != 0:
            return await callback(request, response, pexpire)
