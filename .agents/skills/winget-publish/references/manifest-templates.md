# Plantillas Oficiales de Manifiestos Winget (Esquema v1.12.0)

Utiliza estas plantillas multi-archivo para estructurar paquetes en el formato oficial requerido por `microsoft/winget-pkgs`.

---

## 📦 Plantilla 1: Aplicación Portable (.exe autónomo)

### `<PackageIdentifier>.yaml` (Versión)
```yaml
# yaml-language-server: $schema=https://aka.ms/winget-manifest.version.1.12.0.schema.json

PackageIdentifier: Publisher.AppName
PackageVersion: 1.0.0
DefaultLocale: en-US
ManifestType: version
ManifestVersion: 1.12.0
```

### `<PackageIdentifier>.installer.yaml` (Instalador Portable)
```yaml
# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.1.12.0.schema.json

PackageIdentifier: Publisher.AppName
PackageVersion: 1.0.0
InstallerType: portable
Commands:
- appname
Installers:
- Architecture: x64
  InstallerUrl: https://github.com/Publisher/Repo/releases/download/v1.0.0/appname.exe
  InstallerSha256: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
ManifestType: installer
ManifestVersion: 1.12.0
```

### `<PackageIdentifier>.locale.en-US.yaml` (Metadatos / Localización)
```yaml
# yaml-language-server: $schema=https://aka.ms/winget-manifest.defaultLocale.1.12.0.schema.json

PackageIdentifier: Publisher.AppName
PackageVersion: 1.0.0
PackageLocale: en-US
Publisher: Publisher Name
PublisherUrl: https://publisher.example.com
PublisherSupportUrl: https://github.com/Publisher/Repo/issues
Author: Author Name
PackageName: App Name
PackageUrl: https://github.com/Publisher/Repo
License: MIT
LicenseUrl: https://github.com/Publisher/Repo/blob/main/LICENSE
Copyright: Copyright (c) 2026 Author Name
ShortDescription: Short concise description of the application.
Description: |-
  Detailed multi-line description explaining the features,
  architecture, and usage of the application.
Moniker: appname
Tags:
- utilities
- tools
- windows11
ReleaseNotesUrl: https://github.com/Publisher/Repo/releases/tag/v1.0.0
ManifestType: defaultLocale
ManifestVersion: 1.12.0
```

---

## 🗜️ Plantilla 2: Paquete Comprimido ZIP Portable

### `<PackageIdentifier>.installer.yaml`
```yaml
# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.1.12.0.schema.json

PackageIdentifier: Publisher.AppName
PackageVersion: 1.0.0
InstallerType: zip
NestedInstallerType: portable
NestedInstallerFiles:
- RelativeFilePath: appname.exe
  PortableCommandAlias: appname
Installers:
- Architecture: x64
  InstallerUrl: https://github.com/Publisher/Repo/releases/download/v1.0.0/appname-portable.zip
  InstallerSha256: BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
ManifestType: installer
ManifestVersion: 1.12.0
```

---

## ⚙️ Plantilla 3: Instalador Tradicional (.exe Inno / NSIS / WiX / MSI)

### `<PackageIdentifier>.installer.yaml`
```yaml
# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.1.12.0.schema.json

PackageIdentifier: Publisher.AppName
PackageVersion: 1.0.0
InstallerType: inno # inno | nullsoft | wix | burn | msi | exe
Scope: machine # user | machine
InstallerSwitches:
  Silent: /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
  SilentWithProgress: /SILENT /SUPPRESSMSGBOXES /NORESTART
Installers:
- Architecture: x64
  InstallerUrl: https://github.com/Publisher/Repo/releases/download/v1.0.0/setup.exe
  InstallerSha256: CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
ManifestType: installer
ManifestVersion: 1.12.0
```
