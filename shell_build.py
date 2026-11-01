#!/usr/bin/env python3
"""Build nxnative's real iOS host with no game module inside: the shell the Windows side fills in.

Usage: GAME=<profile id> shell_build.py <nxnative checkout, with shell.patch applied> --output <new directory>

Runs on a machine with Xcode and XcodeGen. It needs no game files, keys, shaders, signing or device: it follows
nxnative's dm/ios/tools/build_smoke.py (MIT, see NOTICE.md), except that the executable embeds no module (-DDM_SHELL,
an empty embed.S) and the unsigned app comes out as <output>/shell/DmIOS.app, its stand-in resources removed, with the
licenses of what is compiled into it in <output>/shell/licenses.
"""
import argparse, json, os, plistlib, re, shutil, subprocess, sys
from pathlib import Path


# What the executable compiles in (dm/third_party/README.md): the rest of dm/third_party is only used by offline tools.
LICENSES = {'nxnative.LICENSE': 'LICENSE', 'libvpx.LICENSE': 'dm/third_party/libvpx/LICENSE', 'libvpx.PATENTS': 'dm/third_party/libvpx/PATENTS',
            'stb_vorbis.LICENSE': 'dm/third_party/stb_vorbis/LICENSE', 'vulkan-headers.LICENSE.md': 'dm/third_party/vulkan-headers/LICENSE.md',
            'macnativegames.LICENSE': 'dm/third_party/macnativegames/LICENSE'}


def copy_licenses(repo, folder):
    folder.mkdir()
    for name, source in LICENSES.items():
        shutil.copyfile(repo / source, folder / name)
    shutil.copyfile(Path(__file__).resolve().parent / 'NOTICE.md', folder / 'NOTICE.md')
    header = (repo / 'dm/gfx/nvn/include/nvn.h').read_text(errors='replace')   # MIT, in the file's own header
    (folder / 'nvn.h.LICENSE').write_text(header[:header.index('*/') + 2] + '\n')
    (folder / 'deko3d.NOTICE').write_text('dm/gfx/nvn/nvn_tex.c ports a layout algorithm from deko3d, source/dk_image.cpp (zlib license, Copyright (C) 2018-2020 fincs).\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', type=Path)
    parser.add_argument('--output', required=True, type=Path, help='new scratch directory')
    args = parser.parse_args()
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo / 'dm/games'))
    import game
    profile = game.load(os.environ.get('GAME'))
    root = args.output.resolve()
    root.mkdir(parents=True)
    ios = repo / 'dm/ios'
    project = root / 'project'
    gen = project / 'Gen'
    (gen / 'dm').mkdir(parents=True)
    (gen / 'dm/shell-placeholder.txt').write_text('Replaced on Windows by the loader tables.')   # nxnative only ever builds this folder non-empty.
    for name in ('Sources', 'tools'):
        (project / name).symlink_to(ios / name, target_is_directory=True)
    shutil.copyfile(ios / 'project.yml', project / 'project.yml')
    assets = gen / 'Assets.xcassets'
    assets.mkdir()
    (assets / 'Contents.json').write_text(json.dumps({'info': {'author': 'xcode', 'version': 1}}))

    env = dict(os.environ, GAME=profile.id, DM_GAME=profile.id, DM_BUNDLE_ID='local.iswitchduo.host', DM_DISPLAY_NAME='iSwitch Host',
               DM_APP_VERSION='0.1', DM_APP_CATEGORY=profile.get('app_category'), DM_TEAM_ID='', DM_SCHEME_NAME='DmIOS', DM_APPICON='',
               DM_SHOW_FPS='NO', DM_LANG='en-US')

    def run(*command, capture=False):
        return subprocess.run([str(c) for c in command], cwd=project, env=env, check=True, text=True, stdout=subprocess.PIPE if capture else None)

    config = run(sys.executable, ios / 'tools/gen_build.py', repo / 'dm/host', gen, capture=True).stdout
    if 'OTHER_CFLAGS = $(inherited) ' not in config:
        raise RuntimeError('gen_build.py no longer writes the OTHER_CFLAGS line this script extends')
    config = config.replace('OTHER_CFLAGS = $(inherited) ', 'OTHER_CFLAGS = $(inherited) -DDM_SHELL ')
    (gen / 'embed.S').write_text('// The shell: the modules are in Frameworks/Guest.framework, written on Windows.\n')
    (gen / 'dm.xcconfig').write_text(config + 'OTHER_LDFLAGS = $(inherited) $(DM_FRAMEWORKS)\n')
    run('xcodegen', 'generate')

    # The resource phase needs something to copy. Nothing from a game: these are removed again below.
    romfs, shaders, derived = root / 'romfs', root / 'shaders', root / 'derived'
    romfs.mkdir()
    shaders.mkdir()
    marker = 'shell-fixture.txt'
    (romfs / marker).write_text('Synthetic resource; no game data.\n')
    (shaders / marker).write_text('Synthetic resource; no shader library.\n')
    chain_h = repo / 'dm/gfx/nvn/dmsh_chain.h'
    chain = re.search(r'#define DMSH_CHAIN "(.*)"', chain_h.read_text()).group(1)
    run(sys.executable, ios / 'tools/gen_resources.py', project, romfs, marker, shaders, f'b-{chain}', '', derived, chain_h)
    run('xcodebuild', '-project', project / 'DmIOS.xcodeproj', '-scheme', 'DmIOS', '-configuration', 'Release', '-destination', 'generic/platform=iOS',
        '-derivedDataPath', derived, '-jobs', '3', 'CODE_SIGNING_ALLOWED=NO', 'CODE_SIGNING_REQUIRED=NO', 'CODE_SIGN_IDENTITY=',
        f'DM_XCODE_OUTPUT_ROOT={derived}', f'SYMROOT={derived}/Build/Products', f'OBJROOT={derived}/Build/Intermediates.noindex', 'build')

    built = derived / 'Build/Products/Release-iphoneos/DmIOS.app'
    out = root / 'shell'
    out.mkdir()
    app = out / 'DmIOS.app'
    shutil.copytree(built, app, symlinks=True)
    for name in ('romfs', 'msl', '_CodeSignature', 'embedded.mobileprovision'):
        target = app / name
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    info = plistlib.loads((app / 'Info.plist').read_bytes())
    executable = (app / info['CFBundleExecutable']).read_bytes()
    if b'Guest.framework did not load' not in executable or b'shaders compiled from source on the device' not in executable:   # Messages, not paths: the compiler may inline a short strcpy.
        raise RuntimeError('The executable lacks the shell patch: was shell.patch applied?')
    commit = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
    info['DMCommit'] = commit[:12] + '+shell'   # The host's log names it (dm/host/main.c).
    (app / 'Info.plist').write_bytes(plistlib.dumps(info))
    (out / 'shell_info.json').write_text(json.dumps({'nxnative': commit, 'game': profile.id, 'chain': chain, 'executable': info['CFBundleExecutable'], 'bytes': len(executable)}, indent=2))
    copy_licenses(repo, out / 'licenses')
    print(f'Shell built: {app}, {len(executable)} bytes, profile {profile.id}, chain {chain}', flush=True)


if __name__ == '__main__':
    main()
