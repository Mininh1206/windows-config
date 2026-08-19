// Nilesoft Shell — Configuración Básica Moderna
settings
{
	priority = 1
	theme.solarized()
	show.delay = 150
	modify.all.commands = false
}

import 'imports/theme.nss'
import 'imports/images.nss'
import 'imports/modify.nss'

menu(type='*' title='Desarrollo y Terminales' image=\uE193)
{
	item(title='Abrir PowerShell 7 aquí' image=\uE193 cmd='pwsh.exe' args='-NoExit -Command Set-Location -LiteralPath "%L"')
	item(title='Abrir en VS Code' image=\uE194 cmd='code.cmd' args='"%L"')
	item(title='Abrir en Windows Terminal' image=\uE193 cmd='wt.exe' args='-d "%L"')
}
