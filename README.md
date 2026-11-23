# rdiskinfo-bin

Pacote AUR (Arch User Repository) com os binários oficiais pré-compilados do **[RDiskInfo](https://github.com/yurinogueira/RDiskInfo)** — visualizador de saúde S.M.A.R.T. e diagnóstico de discos para Linux (ATA/SATA, NVMe, SCSI/SAS/USB), desenvolvido em Rust com interface gráfica `egui`/`eframe` e suporte a CLI/JSON.

---

## Estrutura do Pacote no Arch Linux

Este pacote utiliza o artefato oficial publicado nas releases do GitHub (`rdiskinfo-v<pkgver>-x86_64-linux.tar.gz`):

1. **Binário Principal**: `/usr/bin/rdiskinfo`
2. **Integração com Desktop e Wayland/X11**:
   - `/usr/share/applications/rdiskinfo.desktop` (`StartupWMClass=rdiskinfo`)
   - `/usr/share/icons/hicolor/512x512/apps/rdiskinfo.png` e `/usr/share/pixmaps/rdiskinfo.png`
3. **Política Polkit (`pkexec`)**:
   - `/usr/share/polkit-1/actions/io.github.yurinogueira.rdiskinfo.policy` para o subprocesso privilegiado `--privileged-helper` utilizado na leitura de atributos S.M.A.R.T., envio de comandos ioctl brutos e execução de autotestes.
4. **Documentação e Licença**:
   - `/usr/share/doc/rdiskinfo/README.md`
   - `/usr/share/licenses/rdiskinfo-bin/LICENSE` (`GPL-3.0-or-later`)

### Dependências

- **Obrigatórias (`depends`)**: `smartmontools`, `util-linux` (`lsblk`), `polkit` (`pkexec`), `fontconfig`, `libglvnd`, `libxkbcommon`, `hicolor-icon-theme`, `gcc-libs`, `glibc`.
- **Opcionais (`optdepends`)**: `wayland`, `libx11`, `libxcursor`, `libxi`, `libxkbcommon-x11`, `xdg-desktop-portal` (diálogos nativos de arquivo), `zenity` (fallback de diálogos).

---

## Instalação

### Arch Linux / CachyOS / Manjaro — Via AUR Helper (`paru` ou `yay`)

```bash
paru -S rdiskinfo-bin
# ou
yay -S rdiskinfo-bin
```

### Arch Linux — Manualmente via `makepkg`

```bash
git clone https://aur.archlinux.org/rdiskinfo-bin.git
cd rdiskinfo-bin
makepkg -si
```

### Ubuntu / Kubuntu / Linux Mint / Pop!_OS 22.04+ (Launchpad PPA)

```bash
sudo add-apt-repository ppa:yurinogueira/rdiskinfo
sudo apt update
sudo apt install rdiskinfo
```

---

## Verificação e Uso

```bash
rdiskinfo --help
rdiskinfo --cli
rdiskinfo --json --no-elevate
rdiskinfo --theme sakura --lang pt-br
```

---

## English Summary

AUR binary package for **[RDiskInfo](https://github.com/yurinogueira/RDiskInfo)**, a cross-protocol Linux S.M.A.R.T. and disk diagnostics viewer built in Rust.

- Installs `/usr/bin/rdiskinfo`, desktop entry (`/usr/share/applications/rdiskinfo.desktop`), 512x512 PNG application icon (`hicolor` and `pixmaps`), Polkit policy (`/usr/share/polkit-1/actions/io.github.yurinogueira.rdiskinfo.policy`), documentation, and the `GPL-3.0-or-later` license.
- Provides and conflicts with `rdiskinfo`.
- Depends on `smartmontools`, `util-linux`, `polkit`, `fontconfig`, `libglvnd`, `libxkbcommon`, `hicolor-icon-theme`, `gcc-libs`, and `glibc`.
