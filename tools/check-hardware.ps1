$ram=(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB
$gpus=Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion
Write-Host "=== AI Image Editor hardware check ==="
Write-Host ("RAM: {0:N1} GB" -f $ram)
Write-Host "GPU(s):"
$gpus | Format-Table -AutoSize
Write-Host ""
Write-Host "أرسل لي ناتج هذا الفحص قبل تثبيت نموذج AI كبير، حتى نختار نموذجًا يناسب جهازك."
Read-Host "اضغط Enter"
