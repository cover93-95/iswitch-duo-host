# Shell builder for nxnative

Builds [nxnative](https://github.com/seedds/nxnative)'s iOS host, unsigned, with no module inside, for a test on the maintainer's own phone.

**This repository holds and uses no game file, key, certificate, signature or secret.** Please do not add any.

- `shell.patch`: makes nxnative's loader read its modules from a framework instead of the executable.
- `shell_build.py`: the build, without a game.
- `.github/workflows/build-shell.yml`: starts by hand only. By default it only reports the toolchain.

The result does not run a game, and this project provides none. See `NOTICE.md` for origins and licenses.
