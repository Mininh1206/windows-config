#═══════════════════════════════════════════════════════════════════════════════
#  PowerShell 7 Profile — Daniel
#  Última actualización: 2026-07-20
#═══════════════════════════════════════════════════════════════════════════════

# ─── Cargar Module ───────────────────────────────────────────────────────────
Import-Module -Name Terminal-Icons -ErrorAction SilentlyContinue

# ─── Oh My Posh ──────────────────────────────────────────────────────────────
if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
    oh-my-posh init pwsh --config "$PSScriptRoot\darkside.omp.json" | Invoke-Expression
}

# ─── PSReadLine — Autocompletado, Predicciones y Atajos ──────────────────────
if (Get-Module PSReadLine -ListAvailable) {
    # Tab = Menú interactivo de opciones (estilo zsh / Kali)
    Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete
    Set-PSReadLineKeyHandler -Key Shift+Tab -Function TabCompletePrevious

    # Mostrar descripciones en el menú de autocompletado
    Set-PSReadLineOption -ShowToolTips

    # Habilitar sugerencias predictivas solo si la consola soporta Virtual Terminal y no está redirigida
    if ($Host.UI.SupportsVirtualTerminal -and -not [Console]::IsOutputRedirected) {
        try {
            Set-PSReadLineOption -PredictionSource History -ErrorAction Stop
            Set-PSReadLineOption -PredictionViewStyle ListView -ErrorAction Stop
        }
        catch {
            # Ignorar si el host no soporta la vista predictiva en esta sesión
        }
    }
    # Colores de predicción alineados con Custom Darkside
    Set-PSReadLineOption -Colors @{
        InlinePrediction       = '#7a7a7a'
        ListPrediction         = '#7a7a7a'
        ListPredictionSelected = '#BABABA'
        Command                = '#77B869'
        Parameter              = '#3D97E2'
        Operator               = '#F2D42C'
        Variable               = '#957BBE'
        String                 = '#EFD64B'
        Number                 = '#E05A4F'
        Member                 = '#BABABA'
        Emphasis               = '#E8341C'
        Error                  = '#E05A4F'
        Selection              = '#EFD64B'
    }

    # Flechas ↑/↓ = búsqueda inteligente en historial por lo ya escrito
    Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
    Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward
    Set-PSReadLineOption -HistorySearchCursorMovesToEnd

    # F2 = Alternar entre vista inline y lista de predicciones
    Set-PSReadLineKeyHandler -Key F2 -Function SwitchPredictionView

    # Ctrl+d = Salir de la sesión (como bash/zsh)
    Set-PSReadLineKeyHandler -Key Ctrl+d -Function DeleteCharOrExit
}

# ─── Autocompletado de argumentos para herramientas CLI ──────────────────────
if (Get-Command dotnet -ErrorAction SilentlyContinue) {
    Register-ArgumentCompleter -Native -CommandName dotnet -ScriptBlock {
        param($wordToComplete, $commandAst, $cursorPosition)
        dotnet complete --position $cursorPosition "$commandAst" | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }
}
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Register-ArgumentCompleter -Native -CommandName winget -ScriptBlock {
        param($wordToComplete, $commandAst, $cursorPosition)
        $Local:word = $wordToComplete.Replace('"', '""')
        $Local:ast = $commandAst.ToString().Replace('"', '""')
        winget complete --word="$Local:word" --commandline "$Local:ast" --position $cursorPosition | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }
}

# ─── Funciones Auxiliares ────────────────────────────────────────────────────
function ConvertTo-HumanSize {
    <#
    .SYNOPSIS
        Convierte bytes a un formato legible (KB, MB, GB).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][long]$Bytes
    )
    switch ($Bytes) {
        { $_ -ge 1GB } { return '{0:N1} GB' -f ($_ / 1GB) }
        { $_ -ge 1MB } { return '{0:N1} MB' -f ($_ / 1MB) }
        { $_ -ge 1KB } { return '{0:N1} KB' -f ($_ / 1KB) }
        default { return "$_ B" }
    }
}

# ─── Get-NativeDir — Listado estilo dir con tamaños e iconos ─────────────────
function Get-NativeDir {
    <#
    .SYNOPSIS
        Listado de directorio con tamaños de carpeta (Everything) e iconos NF.
    .PARAMETER Path
        Ruta a listar.
    .PARAMETER Force
        Incluir archivos y carpetas ocultos.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Position = 0)]
        [string]$Path = ".",
        [switch]$Force,
        
        [Alias('o')]
        [switch]$Output,
        
        [Alias('s', 'Sort')]
        [string]$Order = "Name"
    )

    # Resolver la ruta
    $ResolvedPath = (Resolve-Path $Path -ErrorAction SilentlyContinue).Path
    if (-not $ResolvedPath) { $ResolvedPath = $Path }

    # Consultar tamaños de carpetas a Everything (es.exe)
    $folderSizes = @{}
    if (Get-Command es.exe -ErrorAction SilentlyContinue) {
        $esOutput = es.exe -parent "$ResolvedPath" -size -no-header 2>$null
        foreach ($line in $esOutput) {
            $line = $line.Trim()
            if ($line -match '^\s*([\d.,]+)\s+(.+)$') {
                $sizeStr = $matches[1] -replace '\.', '' -replace ',', ''
                $folderSizes[$matches[2].TrimEnd('\')] = [long]$sizeStr
            }
        }
    }

    $gciParams = @{ Path = $ResolvedPath; Force = $Force }
    $Items = Get-ChildItem @gciParams

    # Construir objetos para ordenar/listar
    $displayItems = foreach ($Item in $Items) {
        $size = $null
        if ($Item.PSIsContainer) {
            $pathKey = $Item.FullName.TrimEnd('\')
            if ($folderSizes.ContainsKey($pathKey)) {
                $size = $folderSizes[$pathKey]
            }
        }
        else {
            $size = $Item.Length
        }

        [PSCustomObject]@{
            Name          = $Item.Name
            LastWriteTime = $Item.LastWriteTime
            Length        = $size
            Mode          = $Item.Mode
            PSIsContainer = $Item.PSIsContainer
            Attributes    = $Item.Attributes
            FullName      = $Item.FullName
        }
    }

    if ($Order) {
        $displayItems = $displayItems | Sort-Object $Order
    }

    if ($Output) {
        return $displayItems
    }

    Write-Host ""
    Write-Host "    Directory: " -NoNewline
    Write-Host "$ResolvedPath" -ForegroundColor Cyan
    Write-Host ""

    # Mapas de iconos Nerd Font
    $iconMap = @{
        '.ps1'  = @{ Icon = ''; Color = 'Cyan' }
        '.js'   = @{ Icon = ''; Color = 'Yellow' }
        '.ts'   = @{ Icon = ''; Color = 'Cyan' }
        '.py'   = @{ Icon = ''; Color = 'Green' }
        '.md'   = @{ Icon = ''; Color = 'White' }
        '.json' = @{ Icon = ''; Color = 'Yellow' }
        '.xml'  = @{ Icon = '󰗀'; Color = 'Yellow' }
        '.yaml' = @{ Icon = ''; Color = 'Yellow' }
        '.yml'  = @{ Icon = ''; Color = 'Yellow' }
        '.exe'  = @{ Icon = ''; Color = 'Red' }
        '.dll'  = @{ Icon = ''; Color = 'Red' }
        '.zip'  = @{ Icon = ''; Color = 'Yellow' }
        '.rar'  = @{ Icon = ''; Color = 'Yellow' }
        '.7z'   = @{ Icon = ''; Color = 'Yellow' }
        '.png'  = @{ Icon = ''; Color = 'Magenta' }
        '.jpg'  = @{ Icon = ''; Color = 'Magenta' }
        '.jpeg' = @{ Icon = ''; Color = 'Magenta' }
        '.gif'  = @{ Icon = ''; Color = 'Magenta' }
        '.mp3'  = @{ Icon = ''; Color = 'Cyan' }
        '.wav'  = @{ Icon = ''; Color = 'Cyan' }
        '.mp4'  = @{ Icon = ''; Color = 'Red' }
        '.mkv'  = @{ Icon = ''; Color = 'Red' }
        '.doc'  = @{ Icon = '󰈬'; Color = 'Blue' }
        '.docx' = @{ Icon = '󰈬'; Color = 'Blue' }
        '.pdf'  = @{ Icon = ''; Color = 'Red' }
        '.xlsx' = @{ Icon = '󰈙'; Color = 'Green' }
        '.csv'  = @{ Icon = '󰈙'; Color = 'Green' }
        '.txt'  = @{ Icon = ''; Color = 'White' }
        '.html' = @{ Icon = ''; Color = 'Red' }
        '.css'  = @{ Icon = ''; Color = 'Blue' }
    }

    $folderIconMap = @{
        '.vscode'   = @{ Icon = ''; Color = 'DarkGray' }
        'Desktop'   = @{ Icon = ''; Color = 'Cyan' }
        'Documents' = @{ Icon = '󰈙'; Color = 'Blue' }
        'Downloads' = @{ Icon = '󰉍'; Color = 'Green' }
        'Music'     = @{ Icon = '󰎆'; Color = 'Yellow' }
        'Pictures'  = @{ Icon = '󰉏'; Color = 'Magenta' }
        'Videos'    = @{ Icon = '󰕧'; Color = 'Red' }
        'github'    = @{ Icon = ''; Color = 'DarkGray' }
        '.git'      = @{ Icon = ''; Color = 'DarkGray' }
    }

    foreach ($Item in $displayItems) {
        $sizeDisplay = ""
        if ($null -ne $Item.Length -and $Item.Length -is [long]) {
            $sizeDisplay = ConvertTo-HumanSize -Bytes $Item.Length
        }

        $mode = $Item.Mode.PadRight(10)
        $date = $Item.LastWriteTime.ToString("dd/MM/yyyy     HH:mm")
        $sizeCol = $sizeDisplay.PadLeft(12)
        $name = $Item.Name

        # Seleccionar icono y color
        $nameColor = 'White'
        $icon = ''
        $iconColor = 'White'

        if ($Item.PSIsContainer) {
            $nameColor = 'Cyan'
            $icon = ''
            $iconColor = 'Cyan'
            if ($folderIconMap.ContainsKey($name)) {
                $icon = $folderIconMap[$name].Icon
                $iconColor = $folderIconMap[$name].Color
            }
        }
        else {
            if ($Item.Attributes -band [IO.FileAttributes]::Hidden) {
                $nameColor = 'DarkGray'
            }
            $ext = [System.IO.Path]::GetExtension($name).ToLower()
            if ($iconMap.ContainsKey($ext)) {
                $icon = $iconMap[$ext].Icon
                $iconColor = $iconMap[$ext].Color
            }
        }

        Write-Host "  $mode  " -NoNewline
        Write-Host "$date  " -NoNewline
        Write-Host "$sizeCol  " -NoNewline -ForegroundColor DarkYellow
        Write-Host "$icon " -NoNewline -ForegroundColor $iconColor
        Write-Host "$name" -ForegroundColor $nameColor
    }
    Write-Host ""
}

# ─── Aliases de Listado ─────────────────────────────────────────────────────
foreach ($alias in @('ls', 'll')) {
    if (Get-Alias $alias -ErrorAction SilentlyContinue) {
        Remove-Item -Path Alias:\$alias -Force -ErrorAction SilentlyContinue
    }
    Set-Alias -Name $alias -Value Get-NativeDir -Scope Global -Force
}

function Invoke-ListAll {
    [CmdletBinding()]
    param([Parameter(Position = 0)][string]$Path = ".")
    Get-NativeDir -Path $Path -Force
}
Set-Alias -Name la -Value Invoke-ListAll -Scope Global -Force

# ─── Aliases de Git ──────────────────────────────────────────────────────────
function Get-GitStatus { git status }
Set-Alias gits Get-GitStatus

function Invoke-GitAdd { git add . }
Set-Alias gita Invoke-GitAdd

function Invoke-GitCommit {
    param([Parameter(Mandatory, Position = 0)][string]$Message)
    git commit -m $Message
}
Set-Alias gitc Invoke-GitCommit

function Invoke-GitPush { git push }
Set-Alias gitp Invoke-GitPush

function Get-GitLog { git log --oneline -15 }
Set-Alias gitl Get-GitLog

# ─── Alias para OpenCode ────────────────────────────────────────────────────
if (Get-Command opencode -ErrorAction SilentlyContinue) {
    Set-Alias oc opencode
}

# ─── Navegación y Productividad ─────────────────────────────────────────────
function Set-ParentLocation { Set-Location .. }
Set-Alias '..' Set-ParentLocation

function Set-ProjectLocation { Set-Location "A:\Proyectos" }
Set-Alias dev Set-ProjectLocation

function New-DirectoryAndEnter {
    param([Parameter(Mandatory, Position = 0)][string]$Name)
    New-Item -ItemType Directory -Name $Name | Out-Null
    Set-Location $Name
}
Set-Alias mkcd New-DirectoryAndEnter

function New-EmptyFile {
    param([Parameter(Mandatory, Position = 0)][string]$Name)
    if (Test-Path $Name) {
        (Get-Item $Name).LastWriteTime = Get-Date
    }
    else {
        New-Item -ItemType File -Name $Name | Out-Null
    }
}
Set-Alias touch New-EmptyFile

function Get-CommandLocation {
    param([Parameter(Mandatory, Position = 0)][string]$Name)
    Get-Command $Name -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
}
Set-Alias which Get-CommandLocation

function ConvertTo-Base64 {
    param([Parameter(Mandatory, Position = 0)][string]$Text)
    $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    [Convert]::ToBase64String($Bytes)
}

function ConvertFrom-Base64 {
    param([Parameter(Mandatory, Position = 0)][string]$Base64)
    $Bytes = [Convert]::FromBase64String($Base64)
    [System.Text.Encoding]::UTF8.GetString($Bytes)
}

function Invoke-ProfileReload {
    . $PROFILE
    Write-Host "  ✓ Perfil recargado" -ForegroundColor Green
}
Set-Alias reload Invoke-ProfileReload

function Get-EnvironmentPath {
    $env:PATH -split ';' | Where-Object { $_ } | ForEach-Object -Begin { $i = 1 } -Process {
        $color = if ($i % 2 -eq 0) { 'Gray' } else { 'White' }
        Write-Host ("  {0,3}  {1}" -f $i, $_) -ForegroundColor $color
        $i++
    }
}
Set-Alias path Get-EnvironmentPath

# ─── Utilidades de Ciberseguridad ────────────────────────────────────────────
function Get-FileHash256 {
    param([Parameter(Mandatory, Position = 0)][string]$Path)
    $hash = Get-FileHash -Path $Path -Algorithm SHA256
    Write-Host "  SHA-256: " -NoNewline -ForegroundColor Cyan
    Write-Host $hash.Hash
    Write-Host "  File:    " -NoNewline -ForegroundColor Cyan
    Write-Host $hash.Path
}

function Get-ListeningPort {
    Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Sort-Object LocalPort |
    ForEach-Object {
        $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        [PSCustomObject]@{
            Port    = $_.LocalPort
            Address = $_.LocalAddress
            PID     = $_.OwningProcess
            Process = if ($proc) { $proc.ProcessName } else { '—' }
        }
    } | Format-Table -AutoSize
}

function Get-PublicIP {
    try {
        $ip = Invoke-RestMethod -Uri 'https://ifconfig.me/ip' -TimeoutSec 5
        Write-Host "  Public IP: " -NoNewline -ForegroundColor Cyan
        Write-Host $ip.Trim()
    }
    catch {
        Write-Host "  ✗ No se pudo obtener la IP pública" -ForegroundColor Red
    }
}

function Test-DnsLookup {
    param([Parameter(Mandatory, Position = 0)][string]$Domain)
    Resolve-DnsName -Name $Domain -ErrorAction SilentlyContinue |
    Format-Table Name, Type, TTL, @{
        Label      = 'Data'
        Expression = {
            if ($_.QueryType -eq 'A' -or $_.QueryType -eq 'AAAA') { $_.IPAddress }
            elseif ($_.QueryType -eq 'CNAME') { $_.NameHost }
            elseif ($_.QueryType -eq 'MX') { $_.NameExchange }
            else { $_.ToString() }
        }
    } -AutoSize
}

function Find-FileEverywhere {
    param(
        [Parameter(Mandatory, Position = 0)]
        [string]$Query,
        [int]$MaxResults = 25
    )
    if (-not (Get-Command es.exe -ErrorAction SilentlyContinue)) {
        Write-Host "  ✗ es.exe no encontrado" -ForegroundColor Red
        return
    }
    es.exe -no-header -n $MaxResults $Query
}
Set-Alias search Find-FileEverywhere

function Get-WhoIs {
    param([Parameter(Mandatory, Position = 0)][string]$Domain)
    try {
        Invoke-RestMethod "https://rdap.org/domain/$Domain" | ConvertTo-Json -Depth 10 | Out-String
    }
    catch {
        Write-Host "  ✗ Fallo al consultar RDAP/WhoIs" -ForegroundColor Red
    }
}

function Test-PortScan {
    param(
        [Parameter(Mandatory, Position = 0)]
        [string]$HostName,
        [int[]]$Ports = @(21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080)
    )
    Write-Host "  Escaneando puertos en $HostName..." -ForegroundColor Cyan
    foreach ($Port in $Ports) {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $ar = $tcp.BeginConnect($HostName, $Port, $null, $null)
        $wait = $ar.AsyncWaitHandle.WaitOne(500, $false)
        if ($wait) {
            try {
                $tcp.EndConnect($ar)
                Write-Host "    [+] Puerto $Port abierto" -ForegroundColor Green
            }
            catch {}
        }
        $tcp.Close()
    }
}

# ─── Show-ProfileHelp — Cheat Sheet ─────────────────────────────────────────
function Show-ProfileHelp {
    [CmdletBinding()]
    param()

    $c = 'Cyan'
    $y = 'Yellow'
    $g = 'DarkGray'
    $w = 'White'
    $sep = '  ─────────────────────────────────────────────────────────────────'

    function Write-Cmd([string]$Cmd, [string]$Desc) {
        Write-Host "    " -NoNewline
        Write-Host $Cmd.PadRight(38) -NoNewline -ForegroundColor $y
        Write-Host $Desc -ForegroundColor $w
    }

    function Write-Example([string]$Ex) {
        Write-Host "      " -NoNewline
        Write-Host $Ex -ForegroundColor $g
    }

    Write-Host ""
    Write-Host "  ⚡ PowerShell Profile — Cheat Sheet" -ForegroundColor $c
    Write-Host $sep -ForegroundColor $g

    # ── Navegación y Archivos ──
    Write-Host ""
    Write-Host "  🗂️  Navegación y Archivos" -ForegroundColor $c
    Write-Host ""
    Write-Cmd  "ls [ruta]"                     "Listar directorio con iconos y tamaños (Everything)"
    Write-Cmd  "ls -Sort Length"               "Ordenar por tamaño (Name, Length, LastWriteTime)"
    Write-Cmd  "ls -o"                         "Devolver objetos puros (para pipelines)"
    Write-Cmd  "la [ruta]"                     "Listar incluyendo archivos ocultos"
    Write-Host ""
    Write-Cmd  "mkcd <nombre>"                 "Crear carpeta y entrar (mkdir + cd)"
    Write-Cmd  "touch <archivo>"               "Crear archivo vacío o actualizar fecha"
    Write-Cmd  "which <comando>"               "Mostrar la ruta completa de un ejecutable"
    Write-Host ""
    Write-Cmd  "dev"                           "Ir a A:\Proyectos"
    Write-Cmd  "path"                          "Mostrar PATH línea a línea, numerado"
    Write-Cmd  "search <query>"                "Buscar archivos con Everything CLI"

    # ── Git & IA ──
    Write-Host ""
    Write-Host "  💻 Desarrollo e IA" -ForegroundColor $c
    Write-Host ""
    Write-Cmd  "gits"                          "Git Status"
    Write-Cmd  "gita"                          "Git Add todo"
    Write-Cmd  "gitc `"mensaje`""              "Git Commit con mensaje"
    Write-Cmd  "gitp"                          "Git Push"
    Write-Cmd  "gitl"                          "Git Log (últimos 15 commits)"
    Write-Host ""
    Write-Cmd  "oc"                            "Abrir OpenCode (AI coding agent)"

    # ── Ciberseguridad ──
    Write-Host ""
    Write-Host "  🔒 Ciberseguridad" -ForegroundColor $c
    Write-Host ""
    Write-Cmd  "Get-FileHash256 <archivo>"     "Hash SHA-256 de un archivo"
    Write-Cmd  "Get-ListeningPort"             "Puertos TCP en LISTEN con proceso"
    Write-Cmd  "Test-DnsLookup <dominio>"      "Resolución DNS completa (A, CNAME, MX...)"
    Write-Cmd  "Get-WhoIs <dominio>"           "Información WHOIS vía RDAP"
    Write-Cmd  "Test-PortScan <ip>"            "Escaneo rápido de top 20 puertos TCP comunes"
    Write-Cmd  "ConvertTo-Base64 <texto>"      "Codificar texto en Base64"
    Write-Cmd  "ConvertFrom-Base64 <texto>"    "Decodificar texto Base64"

    # ── Utilidades ──
    Write-Host ""
    Write-Host "  🛠️  Utilidades y Atajos" -ForegroundColor $c
    Write-Host ""
    Write-Cmd  "Tab"                           "Menú de autocompletado interactivo con tooltips"
    Write-Cmd  "↑ / ↓"                         "Buscar en historial de comandos"
    Write-Cmd  "F2"                            "Alternar predicciones: inline ↔ lista"
    Write-Cmd  "Ctrl+d"                        "Salir de la terminal"
    Write-Host ""
    Write-Cmd  "reload"                        "Recargar este perfil de PowerShell"

    Write-Host ""
    Write-Host $sep -ForegroundColor $g
    Write-Host ""
}
Set-Alias tips Show-ProfileHelp

# ─── Banner de Bienvenida ────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ⚡ " -NoNewline -ForegroundColor Yellow
Write-Host "PowerShell $($PSVersionTable.PSVersion.Major).$($PSVersionTable.PSVersion.Minor)" -NoNewline -ForegroundColor White
Write-Host " │ " -NoNewline -ForegroundColor DarkGray
Write-Host "Escribe " -NoNewline -ForegroundColor DarkGray
Write-Host "tips" -NoNewline -ForegroundColor Cyan
Write-Host " para ver los comandos disponibles" -ForegroundColor DarkGray
Write-Host ""