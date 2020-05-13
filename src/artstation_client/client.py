import asyncio
from .baseclient import BaseClient


__all__ = ["ArtStation"]


class ArtStation(BaseClient):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._private_csrf_token = None
        self._public_csrf_token = None

    async def load_csrf_tokens(self):
        res = await self.post("/api/v2/csrf_protection/token.json")
        self._public_csrf_token = (await res.json())['public_csrf_token']
        self._private_csrf_token = res.cookies['PRIVATE-CSRF-TOKEN'].value

    async def private_csrf_token(self):
        if self._private_csrf_token is None:
            await self.load_csrf_tokens()
        return self._private_csrf_token

    async def public_csrf_token(self):
        if self._public_csrf_token is None:
            await self.load_csrf_tokens()
        return self._public_csrf_token

    async def get_users(
        self,
        filters,
        page,
        per_page=30,
        pro_first=True,
        query="",
        sorting="followers",
        additional_fields=None
    ):
        assert page > 0
        assert per_page <= 30
        res = await self.post(
            "/api/v2/search/users.json",
            headers = {"PUBLIC-CSRF-TOKEN": await self.public_csrf_token()},
            cookies = {"PRIVATE-CSRF-TOKEN": await self.private_csrf_token()},
            json = {
                "additional_fields": additional_fields or [],
                "filters": filters,
                "page": page,
                "per_page": per_page,
                "pro_first": "1" if pro_first is True else "0",
                "query": query,
                "sorting": sorting 
            }
        )
        return await res.json()

    async def load_users(
        self,
        filters,
        start_page=1,
        end_page=None,
        preload_limit=2,
        errors_limit=0,
        sleep=None,
        **kwargs
    ):
        assert start_page > 0
        assert errors_limit >= 0
        assert (end_page is None) or (end_page >= start_page)

        tasks = None
        page = start_page
        outer_loop_cond = True
        errors_count = 0

        while outer_loop_cond:
            tasks = []
            for _ in range(preload_limit):
                tasks.append(asyncio.create_task(
                    self.get_users(filters, page, **kwargs)
                ))
                page = page + 1
                if end_page is not None and page > end_page:
                    outer_loop_cond = False
                    break

            result = await asyncio.gather(*tasks, return_exceptions=True)

            for r in result:
                if isinstance(r, (AssertionError,)):
                    raise r from None
                if isinstance(r, (Exception,)):
                    errors_count += 1
                    if errors_count > errors_limit:
                        raise r from None

                data = r.get("data", [])

                if data is None or len(data) == 0:
                    return

                for _ in data:
                    yield _

            if sleep:
                await asyncio.sleep(sleep)

    async def get_user_profile(self, username):
        res = await self.get(
            f"/users/{username}.json",
            headers = {"X-CSRF-TOKEN": await self.public_csrf_token()},
            cookies = {"PRIVATE-CSRF-TOKEN": await self.private_csrf_token()}
        )
        return await res.json()

    async def get_user_projects(self, username, page):
        assert page > 0
        res = await self.get(
            f"/users/{username}/projects.json",
            params = {"page": page},
            headers = {"X-CSRF-TOKEN": await self.public_csrf_token()},
            cookies = {"PRIVATE-CSRF-TOKEN": await self.private_csrf_token()}
        )
        return await res.json()

    async def load_user_projects(
        self,
        username,
        start_page=1,
        end_page=None,
        preload_limit=2,
        errors_limit=0,
        sleep=None
    ):
        assert start_page > 0
        assert errors_limit >= 0
        assert (end_page is None) or (end_page >= start_page)

        tasks = None
        page = start_page
        outer_loop_cond = True
        errors_count = 0

        while outer_loop_cond:
            tasks = []
            for _ in range(preload_limit):
                tasks.append(asyncio.create_task(
                    self.get_user_projects(username, page)
                ))
                page = page + 1
                if end_page is not None and page > end_page:
                    outer_loop_cond = False
                    break

            result = await asyncio.gather(*tasks, return_exceptions=True)

            for r in result:
                if isinstance(r, (AssertionError,)):
                    raise r from None
                if isinstance(r, (Exception,)):
                    errors_count += 1
                    if errors_count > errors_limit:
                        raise r from None

                data = r.get("data", [])

                if data is None or len(data) == 0:
                    return

                for _ in data:
                    yield _

            if sleep:
                await asyncio.sleep(sleep)

    async def get_jobs(
        self,
        country_code="",
        offer_relocation=False,
        work_remotely=False,
        query=""
    ):
        res = await self.get(
            "/jobs/search.json",
            params = {
                "country_code": country_code,
                "offer_relocation": "true" if offer_relocation is True else "false",
                "work_remotely": "true" if work_remotely is True else "false",
                "q": query
            },
            headers = {"X-CSRF-TOKEN": await self.public_csrf_token()},
            cookies = {"PRIVATE-CSRF-TOKEN": await self.private_csrf_token()}
        )
        return await res.json()
