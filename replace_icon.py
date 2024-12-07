import platform
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
from datetime import datetime

KEYSTORE = Path("./bin/freekey.keystore")
ALIAS = "freekey"
PASSWORD = "123456"

GREEN = "\033[92m"
RED = "\033[91m"
ENDC = "\033[0m"


def infoprint(msg):
    print(f"{GREEN}[INFO] {msg}{ENDC}")


def errorprint(msg):
    print(f"{RED}[ERROR] {msg}{ENDC}")


def unpack_apk(APK, OUTPUT):
    UNPACKED = OUTPUT / "unpacked"
    infoprint(f'Unpacking "{APK}" to "{UNPACKED}"...')
    UNPACKED.mkdir(parents=True, exist_ok=True)
    with ZipFile(APK, "r") as zipf:
        zipf.extractall(UNPACKED)
    return UNPACKED


def repack_apk(UNPACKED, OUTPUT, APK):
    APK_PACKED = OUTPUT / f"{APK.stem}_repacked.apk"
    infoprint(f'Packing "{UNPACKED}" to "{APK_PACKED}"...')

    no_compress_exts = {".so", ".png", ".jpg", ".ogg", ".mp3"}
    no_compress_files = {"resources.arsc"}
    no_compress_dirs = {"assets/"}

    with ZipFile(APK_PACKED, "w") as zipf:
        for src_file in UNPACKED.rglob("*"):
            if src_file.is_file():
                if (
                    src_file.suffix in no_compress_exts
                    or src_file.name in no_compress_files
                ):
                    compress_type = ZIP_STORED
                    compress_level = None
                elif any(
                    src_file.parts[i] == nc.rstrip("/").split("/")[-1]
                    for i in range(len(src_file.parts))
                    for nc in no_compress_dirs
                ):
                    compress_type = ZIP_STORED
                    compress_level = None
                else:
                    compress_type = ZIP_DEFLATED
                    compress_level = 9

                zipf.write(
                    src_file,
                    src_file.relative_to(UNPACKED),
                    compress_type=compress_type,
                    compresslevel=compress_level,
                )
    return APK_PACKED


def replace_files(SOURCE, TARGET):
    infoprint(f'Replacing files from "{SOURCE}" to "{TARGET}"...')
    for src_file in SOURCE.rglob("*"):
        if src_file.is_file():
            dst_file = TARGET / src_file.relative_to(SOURCE)
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src_file, dst_file)


def align_and_sign(APK_PACKED, keystore, alias, password):
    plat = platform.system()
    if plat == "Windows":
        zip_align_name = "zipalign.exe"
        apk_signer_name = "apksigner.bat"
    elif plat == "Darwin":
        zip_align_name = "zipalign-macosx"
        apk_signer_name = "apksigner-macosx"
    else:
        #zip_align_name = "zipalign"
        apk_signer_name = "apksigner"
    BIN = Path("./bin")
    ZIPALIGN = "/usr/bin/zipalign"
    APKSIGNER = BIN / apk_signer_name
    APK_ALIGNED = APK_PACKED.with_name(f"{APK_PACKED.stem}_aligned.apk")
    APK_SIGNED = APK_ALIGNED.with_name(f"{APK_ALIGNED.stem}_signed.apk")

    infoprint(f'Aligning and signing "{APK_PACKED}" to "{APK_SIGNED}"...')
    subprocess.run([ZIPALIGN, "-p", "-f", "4", APK_PACKED, APK_ALIGNED], check=True)
    infoprint(f'Signing "{APK_ALIGNED}" to "{APK_SIGNED}"...')
    subprocess.run(
        [
            APKSIGNER,
            "sign",
            "--ks",
            keystore,
            "--ks-key-alias",
            alias,
            "--ks-pass",
            f"pass:{password}",
            "--out",
            APK_SIGNED,
            APK_ALIGNED,
        ],
        check=True,
    )
    return APK_SIGNED


def main(apk_path, output_dir):
    infoprint(f'Replacing icon in "{apk_path}"...')
    if not apk_path.suffix == ".apk":
        errorprint(f'The provided file "{apk_path}" is not an APK file.')
        sys.exit(1)

    apk_dir = apk_path.parent
    output_dir = output_dir or Path(f"{apk_dir}/out/{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    DIF = Path("./dif")
    UNPACKED = unpack_apk(apk_path, output_dir)
    replace_files(DIF, UNPACKED)
    APK_PACKED = repack_apk(UNPACKED, output_dir, apk_path)
    APK_SIGNED = align_and_sign(APK_PACKED, KEYSTORE, ALIAS, PASSWORD)

    output_file = apk_dir / f"{apk_path.stem}_replaced.apk"
    shutil.copy(APK_SIGNED, output_file)
    infoprint(f'Replaced APK saved as "{APK_SIGNED}"')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        infoprint("Usage: python replace_icon.py <apk_file>")
        sys.exit(1)
    apk_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    main(apk_path, output_path)
