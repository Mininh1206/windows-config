# Guía Exhaustiva de Resolución de Fallos en el Pipeline de Validación de Winget

Cuando envías una Pull Request a [`microsoft/winget-pkgs`](https://github.com/microsoft/winget-pkgs), el pipeline de validación automatizada de Azure ejecuta una batería exhaustiva de análisis estático, comprobaciones de esquema, escaneo antivirus e instalaciones en sandbox.

---

## 🏷️ 1. Etiquetas de Estado (Status Labels)

| Etiqueta | Significado | Acción Requerida |
| :--- | :--- | :--- |
| **`Azure-Pipeline-Passed`** | El paquete ha superado todas las validaciones automatizadas de CI. | Ninguna. Esperar la revisión manual o fusión por moderadores. |
| **`Validation-Completed`** | Todas las comprobaciones han concluido con éxito. | El PR se fusionará automáticamente si cumple los criterios de auto-merge. |
| **`Needs-Author-Feedback`** | El equipo de moderación o un bot ha dejado un comentario que requiere tu respuesta. | Responder en el PR antes de 5 días para evitar el cierre por inactividad. |
| **`Needs-CLA`** | No has firmado el Contributor License Agreement de Microsoft. | Acceder a [https://cla.opensource.microsoft.com/microsoft/winget-pkgs](https://cla.opensource.microsoft.com/microsoft/winget-pkgs) y firmar con tu cuenta de GitHub. |
| **`Blocking-Issue`** | Hay un error crítico que impide la revisión del PR. | Resolver el error identificado en las etiquetas adjuntas. |

---

## ⚠️ 2. Errores de Manifiesto y Rutas

### `Manifest-Validation-Error`
- **Causa:** Sintaxis YAML inválida, tipos de datos erróneos o campos obligatorios faltantes según el esquema v1.12.0.
- **Solución:**
  ```powershell
  winget validate --manifest <ruta_a_los_archivos>
  ```
  Corregir indentación (espacios, nunca tabs) y validar que `ManifestType` y `ManifestVersion` concuerden.

### `Manifest-Path-Error`
- **Causa:** La estructura de carpetas o nombres de archivos no coincide exactamente con el `PackageIdentifier`.
- **Estructura estricta obligatoria (Case-Sensitive):**
  ```
  manifests/<primera_letra_publisher_en_minuscula>/<Publisher>/<PackageName>/<PackageVersion>/
  ├── <PackageIdentifier>.installer.yaml
  ├── <PackageIdentifier>.locale.<Locale>.yaml
  └── <PackageIdentifier>.yaml
  ```
  *Ejemplo:* Para `PackageIdentifier: FooBar.SuperApp` v2.1.0 -> `manifests/f/FooBar/SuperApp/2.1.0/`.

### `PullRequest-Error`
- **Causa:** El PR contiene modificaciones en archivos fuera de `manifests/` o incluye más de un paquete / versión en el mismo PR.
- **Solución:** Crear una rama limpia con únicamente los 3 archivos YAML de la versión en cuestión.

---

## 🛡️ 3. Errores de Instalador, Binarios y Antivirus

### `Binary-Validation-Error`
- **Causa:** El instalador falló el escaneo estático de antivirus (Microsoft Defender u otros motores) o fue clasificado como PUA (Potentially Unwanted Application).
- **Solución:**
  1. Si es tu propio software (código abierto), envía el archivo a [Microsoft Defender Security Intelligence](https://www.microsoft.com/wdsi/filesubmission) para solicitar análisis de falso positivo.
  2. Firma digitalmente el binario con un certificado de código válido si es posible.

### `Error-Hash-Mismatch` / `Validation-Hash-Verification-Failed`
- **Causa:** El hash SHA256 declarado en `InstallerSha256` no coincide con el hash del archivo descargado desde `InstallerUrl`.
- **Solución:**
  1. Descarga el archivo desde la URL oficial y calcula el hash:
     ```powershell
     winget hash <ruta_al_archivo>
     ```
  2. Actualiza el valor en `<PackageIdentifier>.installer.yaml` en mayúsculas.
  3. Asegúrate de usar URLs estáticas con tag inmutable en GitHub Releases (evita URLs tipo `/releases/latest/download/...`).

### `Error-Installer-Availability`
- **Causa:** El servidor de hosting bloquea las IPs de Azure Datacenter o requiere cookies/autenticación.
- **Solución:** Alojar el instalador en un CDN público accesible globalmente (GitHub Releases, Cloudflare R2, AWS S3).

---

## ⚙️ 4. Errores de Configuración de Instaladores

### `Manifest-Installer-Validation-Error`
- **Causa:** Discrepancia entre el `InstallerType` declarado y el comportamiento del archivo.
- **Reglas clave:**
  - Binarios `.exe` autónomos (sin instalador): Usar `InstallerType: portable`.
  - Instaladores `.exe` tradicionales: Indicar `Silent` y `SilentWithProgress` switches en `InstallerSwitches`.
  - Paquetes `.zip`: Usar `InstallerType: zip` con `NestedInstallerType: portable` y especificar `NestedInstallerFiles`.
