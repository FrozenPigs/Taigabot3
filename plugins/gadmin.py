"""Sieves and commands for global admins."""
# Standard Libs
import asyncio
import itertools
import platform
import time
from datetime import datetime
from sqlite3 import OperationalError

# First Party
from core import db, hook
from util import botu, messaging, user

# Third Party
import psutil


@hook.hook('sieve', ['02-parse-destination-input'])
async def parse_destination_sieve(bot, msg):
    """Is used to parse [channel] destination for gadmin commands."""
    if not msg.user:
        return msg
    if not msg.user.global_admin:
        return msg

    if msg.command is not None:
        commands = bot.plugins['command']
        command = msg.command[1:]
        return_cmds = {'join', 'part', 'cycle', 'say', 'me', 'raw'}

        if command in commands and command not in return_cmds:
            for func in commands[command]:
                adminonly = func.__hook__[1]['admin']
                gadminonly = func.__hook__[1]['gadmin']
                if not adminonly and not gadminonly:
                    return msg

                message = msg.split_message
                try:
                    if message[1][0] == '#':
                        msg.target = message[1]
                        msg.split_message = message.remove(msg.target)
                        msg.message = ' '.join(msg.split_message)
                except IndexError:
                    pass
    return msg


@hook.hook('command', ['gdisable', 'genable'], gadmin=True, autohelp=True)
async def g_genable_gdisable(bot, msg):
    """
    .genable/.gdisable <list/commands/events/sieves> -- Lists, enables or
    disables commands, events and sieves.
    """
    event_vals = list(bot.plugins['event'].values())
    events = [func[0].__name__ for func in (event for event in event_vals)]
    commands = list(bot.plugins['command'])
    sieves = list(bot.plugins['sieve'])
    init = list(bot.plugins['init'])

    nodisable = bot.server_config.no_disable
    gdisabled = bot.server_config.disabled

    message = msg.split_message

    if message[0] == 'list':
        asyncio.create_task(
            botu.cmd_event_sieve_init_lists(bot, msg, gdisabled, nodisable, sieves, events,
                                            commands, init))
        return

    for plugin in message:
        plugin = plugin.lower().strip()
        if await botu.is_cmd_event_sieve_init(plugin, msg, sieves, events, commands, init):
            asyncio.create_task(
                bot.send_notice([msg.nickname], f'{plugin} is not a sieve, command or event.'))
        elif msg.command == 'genable':
            asyncio.create_task(
                botu.remove_from_conf(bot, msg, plugin, gdisabled, f'Genabling {plugin}.',
                                      f'{plugin} is not gdisabled.'))
        elif msg.command == 'gdisable':
            if plugin in nodisable:
                asyncio.create_task(
                    bot.send_notice([msg.nickname], f'You cannot gdisable {plugin}.'))
            else:
                asyncio.create_task(
                    botu.add_to_conf(bot, msg, plugin, gdisabled, f'Gdisabling {plugin}.',
                                     f'{plugin} is already gdisabled.'))


@hook.hook('command', ['gadmins'], gadmin=True, autohelp=True)
async def g_gadmins(bot, msg):
    """
    .gadmins <list/add/del> [user/mask] -- Lists, adds or deletes users or
    masks from gadmins.
    """
    gadmins = bot.server_config.admins
    message = msg.split_message
    print(message[1])
    if message[1] == 'list':
        print('hi')
        asyncio.create_task(bot.send_notice([msg.nickname], 'gadmins are: ' + ', '.join(gadmins)))
        return
    conn = bot.db
    masks = await user.parse_masks(bot, conn, ' '.join(message[1:]))

    for mask in masks:
        if message[1] == 'del':
            asyncio.create_task(
                botu.del_from_conf(bot, msg, mask, gadmins, f'Removing {mask} from gadmins.',
                                   f'{mask} is not a gadmin.'))
        elif message[1] == 'add':
            asyncio.create_task(
                botu.add_to_conf(bot, msg, mask, gadmins, f'Adding {mask} to gadmins..',
                                 f'{mask} is already a gadmin.'))


@hook.hook('command', ['stop', 'restart'], gadmin=True)
async def g_stop_restart(bot, msg):
    """.stop/.restart -- Stops or restarts the bot."""
    print(msg.command)
    if msg.command[1:] == 'stop':
        asyncio.create_task(bot.stop())
    else:
        asyncio.create_task(bot.stop(reset=True))


@hook.hook('command', ['nick'], gadmin=True, autohelp=True)
async def g_nick(bot, msg):
    """.nick <nick> -- Changes the bots nick."""
    new_nick = msg.split_message
    if len(new_nick) > 1:
        asyncio.create_task(bot.notice([msg.nickname], 'Nicknames cannot contain spaces.'))
        return

    asyncio.create_task(bot.send_nick(new_nick))
    bot.server_config.nick = new_nick


@hook.hook('command', ['say', 'me', 'raw'], gadmin=True, autohelp=True)
async def g_say_me_raw(bot, msg):
    """
    .say/.me/.raw <target/rawcmd> <message> -- Say or action to target or
    execute raw command.
    """
    message = msg.split_message
    target = message[0]
    msg = message[1:]
    command = msg.command
    channels = bot.server_config.channels

    if not len(msg) and command != 'raw':
        doc = ' '.join(g_say_me_raw.__doc__.split())
        asyncio.create_task(bot.send_notice([msg.nickname], f'{doc}'))
        return

    if command == 'say':
        if target != '#':
            asyncio.create_task(bot.send_privmsg([target].join(msg)))
        elif target in channels:
            asyncio.create_task(bot.send_privmsg([target], ' '.join(msg)))
    elif command == 'me':
        if target != '#':
            messaging.action(bot, target, ' '.join(msg))
        elif target in channels:
            messaging.action(bot, target, ' '.join(message))
    elif command == 'raw':
        asyncio.create_task(bot.send_line(msg.message.strip()))


# TODO: handle 473: ['arteries', '#wednesday', 'Cannot join channel (+i)']
@hook.hook('command', ['join', 'part', 'cycle'], gadmin=True)
async def g_join_part_cycle(bot, msg):
    """
    .join/.part [#channel] --- Joins or part a list of channels or part current
    channel.
    """
    channels = bot.server_config.channels
    message = [msg.lower() for msg in msg.split_message]
    command = msg.command[1:]
    no_join = bot.server_config.no_channels
    if not message[0]:
        message = [msg.target]

    for channel in message:
        channel = channel

        if channel[0] != '#':
            continue

        if command == 'part' or command == 'cycle':
            if channel not in channels:
                asyncio.create_task(bot.send_notice([msg.nickname], f'Not in {channel}.'))
            else:
                asyncio.create_task(bot.send_part([channel]))
                asyncio.create_task(bot.send_notice([msg.nickname], f'Parting {channel}.'))
                channels.remove(channel)
        time.sleep(0.2)
        if command == 'join' or command == 'cycle':
            if channel not in itertools.chain(channels, no_join):
                channels.append(channel)
                asyncio.create_task(bot.send_join([channel]))
                asyncio.create_task(bot.send_notice([msg.nickname], f'Joining {channel}.'))
            else:
                asyncio.create_task(bot.send_notice([msg.nickname], f'Already in {channel}.'))


async def _list_tables(bot, msg, conn):
    tables = db.get_table_names(conn)
    asyncio.create_task(bot.send_notice([msg.nickname], f'Valid tables are: {", ".join(tables)}.'))


async def _list_columns(bot, msg, conn, table, setting=False, cols=None):
    if not cols:
        columns = db.get_column_names(conn, table)
    else:
        columns = cols

    if bot is not None:
        if not setting:
            asyncio.create_task(
                bot.send_notice([msg.nickname],
                                f'Valid columns to match are: {", ".join(columns)}.'))
        else:
            asyncio.create_task(
                bot.send_notice([msg.nickname], f'Valid columns to set are: {", ".join(columns)}.'))
    return columns


async def _get_match_value(bot, msg, message):
    try:
        match_value = message[2]
        return match_value
    except IndexError:
        asyncio.create_task(bot.send_notice([msg.nickname], 'Need a value to match against.'))
        doc = ' '.join(g_set.__doc__.split())
        asyncio.create_task(bot.send_notice([msg.nickname], f'{doc}'))
        return None


async def _get_set_column(bot, msg, conn, message, table, columns):
    try:
        set_column = message[3]
    except IndexError:
        asyncio.create_task(_list_columns(bot, msg, conn, table, setting=True, cols=columns))
        set_column = ''
        return
    finally:
        if set_column not in columns and set_column != '':
            asyncio.create_task(_list_columns(bot, msg, conn, table, setting=True, cols=columns))
            return None
        return set_column


@hook.hook('command', ['set'], gadmin=True)
async def g_set(bot, msg):
    """
    .set <table> <matchcol> <value> <setcol> <value> -- Changes values in the
    database, and lists valid tables and columns when arguments ommited.
    """
    conn = bot.db

    if not msg.message:
        doc = ' '.join(g_set.__doc__.split())
        asyncio.create_task(bot.send_notice([msg.nickname], f'{doc}'))
        asyncio.create_task(_list_tables(bot, msg, conn))
        return

    message = msg.split_message
    table = message[0]
    columns = await _list_columns(None, msg, conn, table)

    table_exists = db.get_table(conn, table)
    if isinstance(table_exists, OperationalError):
        asyncio.create_task(_list_tables(bot, msg, conn))
        return
    if len(message) == 1:
        asyncio.create_task(_list_columns(bot, msg, conn, table))
        return

    match_col = message[1]
    if match_col not in columns:
        asyncio.create_task(_list_columns(bot, msg, conn, table))
        return

    match_value = await _get_match_value(bot, msg, message)
    if not match_value:
        return

    row_exists = db.get_cell(conn, table, match_col, match_col, match_value)
    if not row_exists:
        asyncio.create_task(bot.send_notice([msg.nickname], f'{match_value} is not in that table.'))
        return

    set_column = await _get_set_column(bot, msg, conn, message, table, columns)
    if not set_column:
        return

    value = ' '.join(message[4:])
    if not value:
        asyncio.create_task(bot.send_notice([msg.nickname], 'Need a value to add.'))
    else:
        conn = bot.db
        asyncio.create_task(bot.send_notice([msg.nickname], f'Setting {set_column} to {value}.'))
        db.set_cell(conn, table, set_column, value, match_col, match_value)


async def _conv_bytes(by, gb=False):
    """Is for converting bytes to mb."""
    mb = by / 1000000
    if gb:
        mb /= 1000
        size = f'{mb:.2f} GB'
    else:
        size = f'{mb:.2f} MB'
    return size


@hook.hook('command', ['system'], gadmin=True)
async def g_system(bot, msg):
    """.system -- Sends notice with system information."""
    # sensors_temperatures, sensors_fans, boot_time, pids
    hostname = platform.node()
    ops = platform.platform()

    architecture = '-'.join(platform.architecture())
    cpu = platform.machine()
    cpus = psutil.cpu_count()
    cpu_per = psutil.cpu_percent()
    general = (f'Hostname: \x02{hostname}\x02, Operating System: '
               f'\x02{ops}\x02, Architecture: \x02{architecture}\x02, '
               f'CPU: \x02{cpu}\x02, Cores: \x02{cpus}\x02, CPU Percent: '
               f'\x02{cpu_per}\x02')
    asyncio.create_task(bot.send_notice([msg.nickname], general))

    mem = psutil.virtual_memory()
    mem_total = await _conv_bytes(mem.total, gb=True)
    mem_used = await _conv_bytes(mem.used, gb=True)
    mem_available = await _conv_bytes(mem.available, gb=True)
    mem_free = await _conv_bytes(mem.free, gb=True)
    mem_per = mem.percent
    memory = (f'Total Memory: \x02{mem_total}\x02, Memory Used: \x02'
              f'{mem_used}\x02, Memory Avaiable: \x02{mem_available}\x02, '
              f'Memory Free: \x02{mem_free}\x02, Memory Percent: \x02{mem_per}\x02')
    asyncio.create_task(bot.send_notice([msg.nickname], memory))

    swap = psutil.swap_memory()
    swap_total = await _conv_bytes(swap.total, gb=True)
    swap_used = await _conv_bytes(swap.used, gb=True)
    swap_free = await _conv_bytes(swap.free, gb=True)
    swap_per = swap.percent

    proc = psutil.Process()
    with proc.oneshot():
        cwd = proc.cwd()
    duseage = psutil.disk_usage(cwd)
    disk_total = await _conv_bytes(duseage.total, gb=True)
    disk_used = await _conv_bytes(duseage.used, gb=True)
    disk_free = await _conv_bytes(duseage.free, gb=True)
    disk_per = duseage.percent
    disk = (f'Total Swap: \x02{swap_total}\x02, Swap Used: \x02{swap_used}\x02, '
            f'Swap Free: \x02{swap_free}\x02, Swap Percent: \x02{swap_per}\x02, '
            f'CWD Disk Total: \x02{disk_total}\x02, CWD Disk Used: \x02'
            f'{disk_used}\x02, CWD Disk Free: \x02{disk_free}\x02, '
            f'CWD Disk Percent: \x02{disk_per}\x02')
    asyncio.create_task(bot.send_notice([msg.nickname], disk))

    net = psutil.net_io_counters()
    net_sent = await _conv_bytes(net.bytes_sent, gb=True)
    net_recv = await _conv_bytes(net.bytes_recv, gb=True)
    connections = len(psutil.net_connections())
    last_boot = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
    total_procs = len(psutil.pids())
    netboot = (f'Network Data Sent: \x02{net_sent}\x02, Network Data Recieved:'
               f' \x02{net_recv}\x02, Total Connections: \x02{connections}\x02, '
               f'Booted: \x02{last_boot}\x02, Total Processes: \x02{total_procs}\x02')
    asyncio.create_task(bot.send_notice([msg.nickname], netboot))


@hook.hook('command', ['bot'], gadmin=True)
async def g_binfo(bot, msg):
    """.memory -- Shows the current memory usage."""
    proc = psutil.Process()
    with proc.oneshot():
        pid = proc.pid
        cmdline = proc.cmdline()
        cwd = proc.cwd()
        username = proc.username()

        mem = proc.memory_full_info()
        rss = await _conv_bytes(mem.rss)
        vms = await _conv_bytes(mem.vms)
        heap = await _conv_bytes(mem.data)
        stack = await _conv_bytes(mem.stack)
        memper = proc.memory_percent()
        counter = proc.io_counters()
        read = await _conv_bytes(counter.read_count)
        write = await _conv_bytes(counter.write_count)
        files = len(proc.open_files())

        connections = len(proc.connections())
        percent = proc.cpu_percent()
        threads = proc.num_threads()
        nice = proc.nice()
        aff = proc.cpu_affinity()
        num = proc.cpu_num()

    general = (f'Username: \x02{username}\x02, PID: \x02{pid}\x02, cmdline: '
               f'\x02{" ".join(cmdline)}\x02, cwd: \x02{cwd}\x02')
    asyncio.create_task(bot.send_notice([msg.nickname], general))
    mem = (f'Real Memory: \x02{rss}\x02, Allocated Memory: \x02{vms}\x02, '
           f'Stack Size: \x02{stack}\x02, Heap Size: \x02{heap}\x02, '
           f'Memory Percent: \x02{memper:.2f}\x02')
    asyncio.create_task(bot.send_notice([msg.nickname], mem))
    disk = (f'Total Disk Read: \x02{read}\x02, Total Disk Write: \x02{write}\x02, '
            f'Open Files: \x02{files}\x02, Open Net Connections: '
            f'\x02{connections}\x02')
    asyncio.create_task(bot.send_notice([msg.nickname], disk))
    aff = ' '.join([str(cpu) for cpu in aff])
    cpu = (f'Bot CPU Percent: \x02{percent}\x02, Used Threads: '
           f'\x02{threads}\x02, Niceness: \x02{nice}\x02, '
           f'CPU Affinity: \x02{aff}\x02, Current Core: \x02{num}\x02')
    asyncio.create_task(bot.send_notice([msg.nickname], cpu))


@hook.hook('command', ['ctcp'], gadmin=True, autohelp=True)
async def g_ctcp(bot, msg):
    """
    .ctcp <target> <command> [message] -- Sends CTCP command to the target,
     with optional message.
    """
    message = msg.split_message
    if len(message) <= 1:
        doc = ' '.join(g_ctcp.__doc__.split())
        asyncio.create_task(bot.send_notice([msg.nickname], f'{doc}'))
        return
    if len(message) == 2:
        ctcp = f'\x01ACTION {message[1]}\x01'
        asyncio.create_task(bot.send_notice([message[0]], ctcp))
    elif len(message) == 3:
        ctcp = f'\x01ACTION {message[1]} {" ".join(message[2:])}\x01'
        asyncio.create_task(bot.send_notice([message[0]], ctcp))
    else:
        doc = ' '.join(g_ctcp.__doc__.split())
        asyncio.create_task(bot.send_notice([bot.nickname], f'{doc}'))
        return


@hook.hook('command', ['dbcache'], gadmin=True)
async def dbcache(bot, msg):
    """
    .dbcache -- Lists all the get caches for the db, order is hits,
    misses, currsize.
    """
    cell = db.get_cell.cache_info()
    cell = f'{cell.hits}, {cell.misses}, {cell.currsize}'
    row = db.get_row.cache_info()
    row = f'{row.hits}, {row.misses}, {row.currsize}'
    row = db.get_row.cache_info()
    row = f'{row.hits}, {row.misses}, {row.currsize}'
    column = db.get_column.cache_info()
    column = f'{column.hits}, {column.misses}, {column.currsize}'
    column_names = db.get_column_names.cache_info()
    column_names = (f'{column_names.hits}, {column_names.misses}, ' f'{column_names.currsize}')
    table = db.get_table.cache_info()
    table = f'{table.hits}, {table.misses}, {table.currsize}'
    table_names = db.get_table_names.cache_info()
    table_names = (f'{table_names.hits}, {table_names.misses}, ' f'{table_names.currsize}')
    add_column = db.add_column.cache_info()
    add_column = (f'{add_column.hits}, {add_column.misses}, ' f'{add_column.currsize}')

    message = (f'Cell: \x02{cell}\x02, Row: \x02{row}\x02 Columns: '
               f'\x02{column}\x02, Column Names: \x02{column_names}\x02, '
               f'Tables: \x02{table}\x02, Table Names: \x02{table_names}\x02, '
               f'Add Column: \x02{add_column}\x02')
    asyncio.create_task(bot.sent_notice([msg.nickname], message))
