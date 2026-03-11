# Source - https://stackoverflow.com/a/46120751
# Posted by Yuval Pruss, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-11, License - CC BY-SA 4.0

import aiohttp
import asyncio
async def close_session():
    session = aiohttp.ClientSession()
    # use the session here
    await session.close()

asyncio.run(close_session())
