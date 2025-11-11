# Changelog

## [2.17.8](https://github.com/alltuner/vibetuner/compare/v2.17.7...v2.17.8) (2025-11-11)


### Bug Fixes

* restore configuration loader ([#426](https://github.com/alltuner/vibetuner/issues/426)) ([2d948e2](https://github.com/alltuner/vibetuner/commit/2d948e2ac4f0b4d64d9eacbf5572b45fee3a9830))

## [2.17.7](https://github.com/alltuner/vibetuner/compare/v2.17.6...v2.17.7) (2025-11-11)


### Bug Fixes

* resolve template synchronization for Tailwind CSS rebuilds ([#424](https://github.com/alltuner/vibetuner/issues/424)) ([f2ded92](https://github.com/alltuner/vibetuner/commit/f2ded924a70277eca356951aa2f4e2bfffa3f03b))

## [2.17.6](https://github.com/alltuner/vibetuner/compare/v2.17.5...v2.17.6) (2025-11-11)


### Bug Fixes

* enable Docker local development with environment-based configuration ([#422](https://github.com/alltuner/vibetuner/issues/422)) ([c8222a7](https://github.com/alltuner/vibetuner/commit/c8222a759bed7769b2d2767206db7f6406ad1021))

## [2.17.5](https://github.com/alltuner/vibetuner/compare/v2.17.4...v2.17.5) (2025-11-10)


### Miscellaneous Chores

* cleanup repository structure and dependencies ([#420](https://github.com/alltuner/vibetuner/issues/420)) ([8b021ad](https://github.com/alltuner/vibetuner/commit/8b021ad2ddc1a82c95db04fc243a76dcc282b584))

## [2.17.4](https://github.com/alltuner/vibetuner/compare/v2.17.3...v2.17.4) (2025-11-10)


### Code Refactoring

* modularize justfile structure and remove base.justfile import ([#418](https://github.com/alltuner/vibetuner/issues/418)) ([9719fd1](https://github.com/alltuner/vibetuner/commit/9719fd1269c7407e4619566c288dc739ec45ec87))

## [2.17.3](https://github.com/alltuner/vibetuner/compare/v2.17.2...v2.17.3) (2025-11-10)


### Code Refactoring

* simplify dependency management commands ([#416](https://github.com/alltuner/vibetuner/issues/416)) ([26a23d8](https://github.com/alltuner/vibetuner/commit/26a23d8f446766680b5cac38fcb0a887bc7ec309))

## [2.17.2](https://github.com/alltuner/vibetuner/compare/v2.17.1...v2.17.2) (2025-11-10)


### Bug Fixes

* configure Release Please to update Python package versions ([#414](https://github.com/alltuner/vibetuner/issues/414)) ([67dfc5c](https://github.com/alltuner/vibetuner/commit/67dfc5ca79360c0dec0376b038a689649a5df4cc))

## [2.17.1](https://github.com/alltuner/vibetuner/compare/v2.17.0...v2.17.1) (2025-11-10)


### Bug Fixes

* add uv setup to prepare-release job ([#412](https://github.com/alltuner/vibetuner/issues/412)) ([43f3834](https://github.com/alltuner/vibetuner/commit/43f3834812c7a40eedfa3dc752bc214d97100249))

## [2.17.0](https://github.com/alltuner/vibetuner/compare/v2.16.2...v2.17.0) (2025-11-10)


### Features

* revamp CI workflows with sequential builds and version synchronization ([#408](https://github.com/alltuner/vibetuner/issues/408)) ([9cd8540](https://github.com/alltuner/vibetuner/commit/9cd8540694f9634bb6f5365115aa50af246db419))


### Bug Fixes

* add workflow_call trigger to make release.yml reusable ([#409](https://github.com/alltuner/vibetuner/issues/409)) ([5ac41f5](https://github.com/alltuner/vibetuner/commit/5ac41f5a729c99b205ba38ccb07f80a12a414ae0))
* ensure builds always run and any build failure blocks all publishing ([#410](https://github.com/alltuner/vibetuner/issues/410)) ([b24e153](https://github.com/alltuner/vibetuner/commit/b24e1538fc682d3deb5665ed801f41e7aba286c1))


### Code Refactoring

* move change detection to publish phase for logical workflow ([#411](https://github.com/alltuner/vibetuner/issues/411)) ([8a62150](https://github.com/alltuner/vibetuner/commit/8a6215069cfd56995f889a30aa7a7d7396b9f52d))


### Miscellaneous Chores

* **deps:** update redis docker tag to v8.2 ([#406](https://github.com/alltuner/vibetuner/issues/406)) ([fe2cc99](https://github.com/alltuner/vibetuner/commit/fe2cc999c1aa22a0d523d30aeb601c31ff7d101d))

## [2.16.2](https://github.com/alltuner/vibetuner/compare/v2.16.1...v2.16.2) (2025-11-08)


### Code Refactoring

* simplify publish workflow logic ([#404](https://github.com/alltuner/vibetuner/issues/404)) ([b30cd32](https://github.com/alltuner/vibetuner/commit/b30cd3227957fa198963d2f4deec79a2fcc111ec))

## [2.16.1](https://github.com/alltuner/vibetuner/compare/v2.16.0...v2.16.1) (2025-11-08)


### Bug Fixes

* resolve version extraction and simplify workflow dependencies ([#402](https://github.com/alltuner/vibetuner/issues/402)) ([bfab621](https://github.com/alltuner/vibetuner/commit/bfab6210aa777d8f04c63b04095770c38b3339b8))

## [2.16.0](https://github.com/alltuner/vibetuner/compare/v2.15.2...v2.16.0) (2025-11-08)


### Features

* add .env.j2 template for scaffolded projects ([#395](https://github.com/alltuner/vibetuner/issues/395)) ([da335b5](https://github.com/alltuner/vibetuner/commit/da335b5604e1c48fe1ab7c4ab129b1bc8f9a4e65))
* add mongo and redis services to compose.dev.yml ([#397](https://github.com/alltuner/vibetuner/issues/397)) ([9c299f9](https://github.com/alltuner/vibetuner/commit/9c299f9c80d159fc59f1fefd3161ff29be3c00d9))
* integrate docs publishing into unified publish workflow ([#401](https://github.com/alltuner/vibetuner/issues/401)) ([e615b43](https://github.com/alltuner/vibetuner/commit/e615b437bd14f38b9932d1e3464e8c0e0af28228))


### Code Refactoring

* simplify template structure and improve organization ([#398](https://github.com/alltuner/vibetuner/issues/398)) ([16f1b27](https://github.com/alltuner/vibetuner/commit/16f1b27f6c62cd2291f0f8f5485e3161078ea539))


### Miscellaneous Chores

* **deps:** update mongo docker tag to v8.2 ([#400](https://github.com/alltuner/vibetuner/issues/400)) ([f3c9f46](https://github.com/alltuner/vibetuner/commit/f3c9f466674b8574b830acef90d6907c9de9337a))

## [2.15.2](https://github.com/alltuner/vibetuner/compare/v2.15.1...v2.15.2) (2025-11-06)


### Bug Fixes

* improve release workflow build logic ([#393](https://github.com/alltuner/vibetuner/issues/393)) ([b78ff09](https://github.com/alltuner/vibetuner/commit/b78ff0915730e4c68421505c07682362f95698cc))

## [2.15.1](https://github.com/alltuner/vibetuner/compare/v2.15.0...v2.15.1) (2025-11-06)


### Miscellaneous Chores

* remove temporary test workflow ([#391](https://github.com/alltuner/vibetuner/issues/391)) ([4b06f23](https://github.com/alltuner/vibetuner/commit/4b06f2364fe19453a4092c27100d5a222590b300))

## [2.15.0](https://github.com/alltuner/vibetuner/compare/v2.14.1...v2.15.0) (2025-11-06)


### Features

* add llms.txt and llms-full.txt for LLM integration ([#389](https://github.com/alltuner/vibetuner/issues/389)) ([34bf3bb](https://github.com/alltuner/vibetuner/commit/34bf3bb20621bad79e34164b58d217a1134a60e1))

## [2.14.1](https://github.com/alltuner/vibetuner/compare/v2.14.0...v2.14.1) (2025-11-06)


### Bug Fixes

* make version updates idempotent in build steps ([#386](https://github.com/alltuner/vibetuner/issues/386)) ([a70550b](https://github.com/alltuner/vibetuner/commit/a70550bead2e0d806be5d90e8cc974d8e62f1e1b))

## [2.14.0](https://github.com/alltuner/vibetuner/compare/v2.13.6...v2.14.0) (2025-11-06)


### Features

* add manual workflow dispatch for force publishing ([#384](https://github.com/alltuner/vibetuner/issues/384)) ([49efdb8](https://github.com/alltuner/vibetuner/commit/49efdb8190df105a984a930652b5e03f5e498b54))

## [2.13.6](https://github.com/alltuner/vibetuner/compare/v2.13.5...v2.13.6) (2025-11-06)


### Bug Fixes

* sandboxing was a real productivity killer ([#382](https://github.com/alltuner/vibetuner/issues/382)) ([adb9429](https://github.com/alltuner/vibetuner/commit/adb94295be92c812260e4a4260e4bbe41323baff))

## [2.13.5](https://github.com/alltuner/vibetuner/compare/v2.13.4...v2.13.5) (2025-11-06)


### Bug Fixes

* convert relative links to absolute URLs in changelog docs ([#373](https://github.com/alltuner/vibetuner/issues/373)) ([a3ab5cb](https://github.com/alltuner/vibetuner/commit/a3ab5cbb99d165f44602ff5956f3f821cf863139))
* include chore commits in changelog ([#379](https://github.com/alltuner/vibetuner/issues/379)) ([44ffea3](https://github.com/alltuner/vibetuner/commit/44ffea38f9e1e77713cbe7d62cb069ae0e32a0bb))
* include refactor and perf commits in changelog ([#378](https://github.com/alltuner/vibetuner/issues/378)) ([f98e9df](https://github.com/alltuner/vibetuner/commit/f98e9df0b15621615ad2fe613b48057c9802465c))


### Code Refactoring

* remove template backwards compatibility symlink ([#377](https://github.com/alltuner/vibetuner/issues/377)) ([3ba7e11](https://github.com/alltuner/vibetuner/commit/3ba7e1111f7241cf45016b49e0c27ed3d69d10e4))


### Miscellaneous Chores

* add gh pr list and gh run list permissions ([#380](https://github.com/alltuner/vibetuner/issues/380)) ([6fb0642](https://github.com/alltuner/vibetuner/commit/6fb06423e1e201bc7f9e798185353343126eb912))
* add permissions for uvx uv-bump and gh pr create ([#375](https://github.com/alltuner/vibetuner/issues/375)) ([27e392a](https://github.com/alltuner/vibetuner/commit/27e392a869b83816adc4c3100131776eecaa610f))
* **deps:** update JavaScript and Python dependencies ([#374](https://github.com/alltuner/vibetuner/issues/374)) ([0370036](https://github.com/alltuner/vibetuner/commit/0370036ad1d242ac2bccd0eb03ba6c237b5e03b2))

## [2.13.4](https://github.com/alltuner/vibetuner/compare/v2.13.3...v2.13.4) (2025-11-06)


### Bug Fixes

* resolve workflow trigger and PR title validation issues ([#372](https://github.com/alltuner/vibetuner/issues/372)) ([42816c4](https://github.com/alltuner/vibetuner/commit/42816c45ac2c67dee655635b760b199a60c9d720))
* trigger publish and docs workflows after release creation ([#370](https://github.com/alltuner/vibetuner/issues/370)) ([20ac331](https://github.com/alltuner/vibetuner/commit/20ac33178059ad31998af232befe29b676d08892))

## [2.13.3](https://github.com/alltuner/vibetuner/compare/v2.13.2...v2.13.3) (2025-11-06)


### Bug Fixes

* add pull_request_target trigger and ignore Release Please PRs in title validation ([3e681d2](https://github.com/alltuner/vibetuner/commit/3e681d2df6946a8d607aab3be6093dee9b4c4595))
* add pull_request_target trigger and ignore Release Please PRs in title validation ([344a683](https://github.com/alltuner/vibetuner/commit/344a683ce086ad3df7e09ca95a334fcfeefd94e5))
* configure release-please for unified monorepo releases ([#365](https://github.com/alltuner/vibetuner/issues/365)) ([9827da3](https://github.com/alltuner/vibetuner/commit/9827da3eccbf3a32afce54f13fc6a10626f8435f))
* release workflow ([eaadbbe](https://github.com/alltuner/vibetuner/commit/eaadbbee47d7b87196a1ba6ebd8c2ab644ef8f00))

## [2.13.2](https://github.com/alltuner/vibetuner/compare/v2.13.1...v2.13.2) (2025-11-05)


### Bug Fixes

* add push tag trigger to publish workflow ([3c9f01f](https://github.com/alltuner/vibetuner/commit/3c9f01f754282ce34417850955b0587bb403a2ff))
* add push tag trigger to publish workflow ([635840f](https://github.com/alltuner/vibetuner/commit/635840fd5c273a146476ac285d8108340ec85ae8))
* add workflow_dispatch trigger to publish workflow ([453afb0](https://github.com/alltuner/vibetuner/commit/453afb033c685884a50f28af24bf9709d6059b92))
* add workflow_dispatch trigger to publish workflow ([587609e](https://github.com/alltuner/vibetuner/commit/587609ec61b8b0eecda2ad0309d8c62bfbc4c727))

## [2.13.1](https://github.com/alltuner/vibetuner/compare/v2.13.0...v2.13.1) (2025-11-05)


### Miscellaneous Chores

* release v2.13.1 ([#348](https://github.com/alltuner/vibetuner/issues/348)) ([a9c95c3](https://github.com/alltuner/vibetuner/commit/a9c95c36794471a6cf08e64ec749d73d94303ee1))

## [2.13.0](https://github.com/alltuner/vibetuner/compare/v2.12.2...v2.13.0) (2025-11-05)

### Features

* simplify Renovate configuration to default settings ([#342](https://github.com/alltuner/vibetuner/issues/342)) ([76ffb0b](https://github.com/alltuner/vibetuner/commit/76ffb0b5261c8d9b8b6adab62166a2b81167ef6d))

## [2.12.2](https://github.com/alltuner/vibetuner/compare/v2.12.1...v2.12.2) (2025-11-05)

### Bug Fixes

* remove component prefixes from release tags ([1095b32](https://github.com/alltuner/vibetuner/commit/1095b3298dea497c5b89469fd1ae96054e95d6d7))
* remove component prefixes from release tags ([0ef87b3](https://github.com/alltuner/vibetuner/commit/0ef87b367f692d7bba2480f5500ab4927128276c))

## [2.12.1](https://github.com/alltuner/vibetuner/compare/v2.12.0...v2.12.1) (2025-11-05)

### Bug Fixes

* update PR title validation to support breaking changes and upgrade action ([#334](https://github.com/alltuner/vibetuner/issues/334)) ([2464200](https://github.com/alltuner/vibetuner/commit/24642009e8d15f891a85e574c50f5cb303379a4d))

## [2.12.0](https://github.com/alltuner/vibetuner/compare/v2.11.0...v2.12.0) (2025-11-05)

### Features

* enable automatic GitHub releases on PR merge ([#338](https://github.com/alltuner/vibetuner/issues/338)) ([e759ec1](https://github.com/alltuner/vibetuner/commit/e759ec1398acc678257eb9698ef4c4a21da4c7ac))
* implement automated changelog management with Release Please ([#333](https://github.com/alltuner/vibetuner/issues/333)) ([c498374](https://github.com/alltuner/vibetuner/commit/c4983741d87fbabcbd89e496860712d6d793eba2))

### Bug Fixes

* resolve Release Please workflow issues and improve commit validation ([#335](https://github.com/alltuner/vibetuner/issues/335)) ([57cebfe](https://github.com/alltuner/vibetuner/commit/57cebfed0fc03a1b32b534f2e738d4ced7efaa42))
