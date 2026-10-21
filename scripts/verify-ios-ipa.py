"""Check a real device IPA and record its payload, binary and web asset hashes."""
import argparse
import hashlib
import json
import plistlib
import struct
from pathlib import Path
from zipfile import ZipFile


def verify(ipa_path):
    with ZipFile(ipa_path) as archive:
        assert archive.testzip() is None, "IPA contains a damaged ZIP entry"
        names = set(archive.namelist())
        app = "Payload/App.app/"
        info = plistlib.loads(archive.read(app + "Info.plist"))
        assert info["CFBundlePackageType"] == "APPL", "Payload is not an app"
        assert info["CFBundleSupportedPlatforms"] == ["iPhoneOS"], "Simulator build"
        assert info["CFBundleDisplayName"] == "Bet Or Go", "App display name mismatch"
        assert info["CFBundleIdentifier"] == "com.riverpoker.game", "Wrong application"
        executable_name = app + info["CFBundleExecutable"]
        binary = archive.read(executable_name)
        assert binary[:4] == b"\xcf\xfa\xed\xfe", "Expected a thin 64-bit Mach-O executable"
        _, cpu_type, _, file_type, commands, _, _, _ = struct.unpack_from("<8I", binary)
        assert cpu_type == 0x0100000C, "Executable is not arm64"
        assert file_type == 2, "Mach-O is not an executable"
        offset = 32
        ios_device = False
        for _ in range(commands):
            command, size = struct.unpack_from("<2I", binary, offset)
            assert size >= 8 and offset + size <= len(binary), "Invalid Mach-O command"
            if command == 0x32:  # LC_BUILD_VERSION: PLATFORM_IOS = 2
                ios_device = struct.unpack_from("<I", binary, offset + 8)[0] == 2
            if command == 0x21:  # LC_ENCRYPTION_INFO
                assert struct.unpack_from("<I", binary, offset + 16)[0] == 0, "Encrypted executable"
            if command == 0x2C:  # LC_ENCRYPTION_INFO_64
                assert struct.unpack_from("<I", binary, offset + 16)[0] == 0, "Encrypted executable"
            offset += size
        assert ios_device, "Executable was not built for a physical iOS device"
        assert archive.getinfo(executable_name).external_attr >> 16 & 0o111, "Executable permission missing"
        required = [app + "public/index.html", app + "capacitor.config.json"]
        assert all(name in names for name in required), "Bundled app resources missing"
        asset_names = sorted(name for name in names if name.startswith(app + "public/") and not name.endswith("/"))
        assert any(name.endswith(".js") for name in asset_names), "JavaScript assets missing"
        assert any(name.endswith(".css") for name in asset_names), "Stylesheet assets missing"
        config = json.loads(archive.read(app + "capacitor.config.json"))
        assert config["appId"] == info["CFBundleIdentifier"], "Capacitor bundle identifier mismatch"
        return {
            "file": ipa_path.name,
            "sha256": hashlib.sha256(ipa_path.read_bytes()).hexdigest(),
            "bundleIdentifier": info["CFBundleIdentifier"],
            "displayName": info["CFBundleDisplayName"],
            "version": info["CFBundleShortVersionString"],
            "build": info["CFBundleVersion"],
            "minimumIOSVersion": info["MinimumOSVersion"],
            "platform": "iPhoneOS",
            "architecture": "arm64",
            "encrypted": False,
            "requiresDeviceOwnerSigning": True,
            "deviceInstallationTested": False,
            "webAssets": {name[len(app):]: hashlib.sha256(archive.read(name)).hexdigest() for name in asset_names},
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ipa", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.ipa)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
