$clnt = new-object System.Net.WebClient
$clnt.DownloadFile($args[0], "tmp.zip")

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory("tmp.zip", $args[1])
[System.IO.File]::Delete("tmp.zip")