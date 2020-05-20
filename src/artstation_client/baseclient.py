import logging
import fake_useragent
#
from aiohttp import ClientSession
from aiohttp import TraceConfig
from aiohttp import ClientTimeout


__all__ = ["BaseClient"]


useragent_generator = fake_useragent.UserAgent()
logger = logging.getLogger('artstation-client')
logger.setLevel(logging.WARNING)


class BaseClient:

    def __init__(
        self,
        headers=None,
        cookies=None,
        raise_for_status=True,
        timeout=60,
        debug=False,
        trace_configs=None,
        **kwargs
    ):
        self._url_base = "https://www.artstation.com"

        headers = headers or {}
        headers.update({
            'User-Agent': useragent_generator.random,
            'Host': 'www.artstation.com',
            'Origin': 'https://www.artstation.com',
            'Referer': 'https://www.artstation.com',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json'
        })

        trace_configs = trace_configs or []

        if debug:
            t_conf = TraceConfig()
            t_conf.on_request_start.append(self.on_debug_req_start)
            t_conf.on_request_end.append(self.on_debug_req_end)
            trace_configs.append(t_conf)

        timeout = ClientTimeout(total=timeout)

        self.session = ClientSession(
            headers = headers,
            cookies = cookies,
            raise_for_status = raise_for_status,
            timeout = timeout,
            trace_configs=trace_configs,
            **kwargs
        )

    @property
    def logger(self):
        return logger

    async def do_request(self, method, url, **kwargs):
        return await (getattr(self.session, method)(url, **kwargs))

    async def get(self, path, **kwargs):
        return await self.do_request("get", f"{self._url_base}" + path, **kwargs)

    async def post(self, path, **kwargs):
        return await self.do_request("post", f"{self._url_base}" + path, **kwargs)

    async def close(self):
        return await self.session.close()

    async def on_debug_req_start(self, ses, trace_conf_ctx, params):
        # TODO: implement on_debug_req_start
        logger.info("Starting request")

    async def on_debug_req_end(self, ses, trace_conf_ctx, params):
        # TODO: implement on_debug_req_end
        logger.info("Ending request")
