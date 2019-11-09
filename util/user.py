"""Utils for cheking user related information."""
# Copyright (C) 2019  Anthony DeDominic <adedomin@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Standard Libs
from sqlite3 import Connection
from typing import Any, Dict, List, Optional

# First Party
from core import db


async def is_gadmin(client: Any, server: str, mask: str) -> bool:
    """Is used to check if mask is a gadmin on the server."""
    admins = client.bot.config['servers'][server]['admins']
    return all(mask == nmask for nmask in admins)


async def is_admin(client: Any, conn: Connection, nick: str,
                   mask: str) -> bool:
    """Is used to check if a mask is an admin in the channel."""
    db.add_column(conn, 'channels', 'admins')
    admins = db.get_cell(conn, 'channels', 'admins', 'channel', nick)
    if admins:
        nadmins: Optional[str] = admins[0][0]
        if nadmins:
            if mask in nadmins.split():
                return True
    return False


async def is_ignored(client: Any, conn: Connection, target: str,
                     mask: str) -> bool:
    """Is used to check if a mask is ignored in a channel."""
    db.add_column(conn, 'channels', 'ignored')
    ignores = db.get_cell(conn, 'channels', 'ignored', 'channel', target)
    if ignores:
        nignores: Optional[str] = ignores[0][0]
        if nignores:
            if mask in nignores:
                return True
    return False


async def is_gignored(client: Any, server: str, mask: str) -> bool:
    """Is used to check if a mask is gignored on the server."""
    ignored = client.bot.config['servers'][server]['ignored']
    return all(mask == nmask for nmask in ignored)


async def is_user(client: Any, conn: Connection, nick: str) -> bool:
    """Is used to determain if a user is in db or user dict."""
    db_user = db.get_cell(conn, 'users', 'mask', 'nick', nick)
    if nick not in client.users and not db_user:
        return False
    return True


async def get_mask(client: Any, conn: Connection, nick: str) -> str:
    """Is used to combine user information into a mask."""
    user: Dict[str, str]
    try:
        user = client.users[nick]
    except KeyError:
        db_user = db.get_cell(conn, 'users', 'mask', 'nick', nick)
        if db_user:
            return db_user[0][0]
        else:
            return ''
    mask: str = f'{user["nickname"]}!{user["username"]}@{user["hostname"]}'
    return mask


async def parse_masks(client: Any, conn: Connection, inp: str) -> List[str]:
    """Is used for parsing space seperated lists of users into masks."""
    split_inp: List[str]
    if ' ' in inp:
        split_inp = inp.split(' ')
    else:
        split_inp = [inp]
    print(inp)
    masks: List[str] = [
        await get_mask(client, conn, user)
        for user in split_inp
        if await is_user(client, conn, user)]
    masks.extend(mask for mask in split_inp if '@' in mask)
    return masks
