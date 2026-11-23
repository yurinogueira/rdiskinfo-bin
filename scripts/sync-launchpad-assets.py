#!/usr/bin/env python3
"""
Downloads the upstream RDiskInfo release archive for a given version (or pkgver in PKGBUILD),
normalizes libm GLIBC_2.43 symbol versions (atan2f/acosf -> GLIBC_2.2.5) for Ubuntu 22.04+/24.04+
compatibility, strips and compresses the binary to rdiskinfo.zst, and updates desktop/icon/Polkit
assets in the repository root for Launchpad PPA native builds.
"""

import io
import re
import struct
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent


def get_pkgver() -> str:
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip().lstrip("v")
    pkgbuild = (REPO_DIR / "PKGBUILD").read_text(encoding="utf-8")
    m = re.search(r"^pkgver=([^\s#]+)", pkgbuild, re.MULTILINE)
    if not m:
        raise RuntimeError("Could not find pkgver in PKGBUILD")
    return m.group(1).strip().strip("'\"")


def patch_libm_glibc_2_43(bin_path: Path) -> int:
    data = bytearray(bin_path.read_bytes())
    e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", data, 0x3A)
    shstr_off, shstr_size = struct.unpack_from("<QQ", data, e_shoff + e_shstrndx * e_shentsize + 0x18)
    shstr = bytes(data[shstr_off : shstr_off + shstr_size])
    dynstr_off = dynstr_size = 0

    sections = {}
    for i in range(e_shnum):
        sh = e_shoff + i * e_shentsize
        name_idx = struct.unpack_from("<I", data, sh)[0]
        name = shstr[name_idx : shstr.index(0, name_idx)].decode()
        sh_offset, sh_size = struct.unpack_from("<QQ", data, sh + 0x18)
        sections[name] = (sh_offset, sh_size)
        if name == ".dynstr":
            dynstr_off, dynstr_size = sh_offset, sh_size

    if ".gnu.version" not in sections or ".gnu.version_r" not in sections:
        return 0

    dynstr = bytes(data[dynstr_off : dynstr_off + dynstr_size])

    def get_dynstr(offset: int) -> str:
        return dynstr[offset : dynstr.index(0, offset)].decode()

    gvr_off, gvr_size = sections[".gnu.version_r"]
    pos = gvr_off
    libm_225_ver = None
    libm_243_ver = None
    while pos < gvr_off + gvr_size:
        vn_version, vn_cnt, vn_file, vn_aux, vn_next = struct.unpack_from("<HHIII", data, pos)
        file_name = get_dynstr(vn_file)
        if file_name == "libm.so.6":
            aux_pos = pos + vn_aux
            prev_aux_pos = None
            for _ in range(vn_cnt):
                vna_hash, vna_flags, vna_other, vna_name, vna_next = struct.unpack_from(
                    "<IHHII", data, aux_pos
                )
                ver_name = get_dynstr(vna_name)
                if ver_name == "GLIBC_2.2.5":
                    libm_225_ver = vna_other & 0x7FFF
                elif ver_name == "GLIBC_2.43" and vna_next == 0 and prev_aux_pos is not None:
                    libm_243_ver = vna_other & 0x7FFF
                    struct.pack_into("<H", data, pos + 2, vn_cnt - 1)
                    struct.pack_into("<I", data, prev_aux_pos + 12, 0)
                prev_aux_pos = aux_pos
                if vna_next == 0:
                    break
                aux_pos += vna_next
        if vn_next == 0:
            break
        pos += vn_next

    replaced = 0
    if libm_225_ver is not None and libm_243_ver is not None:
        gv_off, gv_size = sections[".gnu.version"]
        for p in range(gv_off, gv_off + gv_size, 2):
            val = struct.unpack_from("<H", data, p)[0]
            if val == libm_243_ver:
                struct.pack_into("<H", data, p, libm_225_ver)
                replaced += 1
        bin_path.write_bytes(data)
    return replaced


def main() -> None:
    ver = get_pkgver()
    url = f"https://github.com/yurinogueira/RDiskInfo/releases/download/v{ver}/rdiskinfo-v{ver}-x86_64-linux.tar.gz"
    print(f"==> Downloading {url} ...")
    with urllib.request.urlopen(url, timeout=60) as resp:
        archive_bytes = resp.read()

    prefix = f"rdiskinfo-v{ver}-x86_64-linux"
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as tf:
        for name in (
            "rdiskinfo",
            "rdiskinfo.desktop",
            "rdiskinfo.png",
            "io.github.yurinogueira.rdiskinfo.policy",
            "LICENSE",
        ):
            content = tf.extractfile(f"{prefix}/{name}").read()
            (REPO_DIR / name).write_bytes(content)

    bin_path = REPO_DIR / "rdiskinfo"
    bin_path.chmod(0o755)
    patched = patch_libm_glibc_2_43(bin_path)
    print(f"==> Normalized {patched} libm GLIBC_2.43 symbol(s) to GLIBC_2.2.5")

    subprocess.run(["strip", "--strip-unneeded", str(bin_path)], check=True)
    subprocess.run(
        ["zstd", "-19", "-q", "-f", "--rm", str(bin_path), "-o", str(REPO_DIR / "rdiskinfo.zst")],
        check=True,
    )
    print(f"==> Generated {REPO_DIR / 'rdiskinfo.zst'} successfully.")


if __name__ == "__main__":
    main()
