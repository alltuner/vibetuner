# Changelog

## [2.24.0](https://github.com/alltuner/vibetuner/compare/v2.23.0...v2.24.0) (2025-11-14)


### Features

* add OpenCode integration with enhanced tooling support ([#508](https://github.com/alltuner/vibetuner/issues/508)) ([6bff852](https://github.com/alltuner/vibetuner/commit/6bff8520dd126fb897e49edbbf23e3d5d104d6d7))
* improve dynamic import logging across vibetuner ([#507](https://github.com/alltuner/vibetuner/issues/507)) ([29a606b](https://github.com/alltuner/vibetuner/commit/29a606b8c0a305a2936164f3fdf48b702a1645ae))


### Miscellaneous Chores

* update dependencies to latest versions ([#506](https://github.com/alltuner/vibetuner/issues/506)) ([903b985](https://github.com/alltuner/vibetuner/commit/903b98555a3ffbda2d4a4b09f097ecffc7cef5b6))

## [2.23.0](https://github.com/alltuner/vibetuner/compare/v2.22.0...v2.23.0) (2025-11-13)


### Features

* add /issue command for GitHub issue workflow ([#499](https://github.com/alltuner/vibetuner/issues/499)) ([25d7fb7](https://github.com/alltuner/vibetuner/commit/25d7fb7d27980768c0cedd99a8c487f7572ccecc))
* add pr-create slash command ([#495](https://github.com/alltuner/vibetuner/issues/495)) ([ec961da](https://github.com/alltuner/vibetuner/commit/ec961dac507befae06df8d00da9733a8f9899da6))
* **allowlist:** add gh issue view and gh issue edit commands ([#504](https://github.com/alltuner/vibetuner/issues/504)) ([7a4fd25](https://github.com/alltuner/vibetuner/commit/7a4fd2572b5699126faeae14821ea3c7793853e2)), closes [#502](https://github.com/alltuner/vibetuner/issues/502)


### Bug Fixes

* **hooks:** replace missing format-files.sh with just format ([#503](https://github.com/alltuner/vibetuner/issues/503)) ([8553571](https://github.com/alltuner/vibetuner/commit/855357179896321c7c6288a6c7a0640e5467c960)), closes [#500](https://github.com/alltuner/vibetuner/issues/500)


### Miscellaneous Chores

* add git stash commands to Claude Code allowlist ([#501](https://github.com/alltuner/vibetuner/issues/501)) ([6dc7526](https://github.com/alltuner/vibetuner/commit/6dc7526b582283168eb9bf66460bf76da48cf449)), closes [#498](https://github.com/alltuner/vibetuner/issues/498)
* add git switch to Claude Code allow list ([#497](https://github.com/alltuner/vibetuner/issues/497)) ([bf7c75f](https://github.com/alltuner/vibetuner/commit/bf7c75f85210cf9f5c6dbb76d0e58118d93fd9fe))

## [2.22.0](https://github.com/alltuner/vibetuner/compare/v2.21.2...v2.22.0) (2025-11-13)


### Features

* add markdown formatting support with rumdl ([#493](https://github.com/alltuner/vibetuner/issues/493)) ([2e707c3](https://github.com/alltuner/vibetuner/commit/2e707c37c69942a2e39f4349d1fb36f6f855e105))

## [2.21.2](https://github.com/alltuner/vibetuner/compare/v2.21.1...v2.21.2) (2025-11-13)


### Miscellaneous Chores

* cleanup release workflow ([#491](https://github.com/alltuner/vibetuner/issues/491)) ([58f256e](https://github.com/alltuner/vibetuner/commit/58f256e04ce9682f2548a4d4db7aeff7e8c35ae1))

## [2.21.1](https://github.com/alltuner/vibetuner/compare/v2.21.0...v2.21.1) (2025-11-13)


### Bug Fixes

* remove cache-dependency-glob from publish-python job ([#490](https://github.com/alltuner/vibetuner/issues/490)) ([faa6ff8](https://github.com/alltuner/vibetuner/commit/faa6ff8166158837279136ab22a6c2c371381d3a))


### Miscellaneous Chores

* remove test file for minor release verification ([#488](https://github.com/alltuner/vibetuner/issues/488)) ([39b2be1](https://github.com/alltuner/vibetuner/commit/39b2be158c8ade7372ac0cfe094fbc03cfff4007))

## [2.21.0](https://github.com/alltuner/vibetuner/compare/v2.20.0...v2.21.0) (2025-11-13)


### Features

* add test file for minor release trigger verification ([#487](https://github.com/alltuner/vibetuner/issues/487)) ([6735294](https://github.com/alltuner/vibetuner/commit/67352949ff017d00530c7643ac3ca84299eefcf5))


### Bug Fixes

* enable publishing for release-please releases on push events ([#484](https://github.com/alltuner/vibetuner/issues/484)) ([b97f2b8](https://github.com/alltuner/vibetuner/commit/b97f2b8626ea3aa593545805be71133b0a874d28))
* prevent patch releases when no meaningful changes ([#485](https://github.com/alltuner/vibetuner/issues/485)) ([72795d1](https://github.com/alltuner/vibetuner/commit/72795d155569a00f32b6860873dd4a9dddc34767))

## [2.20.0](https://github.com/alltuner/vibetuner/compare/v2.19.6...v2.20.0) (2025-11-13)


### Features

* add actionlint job to justfile ([#483](https://github.com/alltuner/vibetuner/issues/483)) ([0f2b0e0](https://github.com/alltuner/vibetuner/commit/0f2b0e0c63ea2721ef7c797a45c520547d51a1c5))
* add CLI version command with project-aware display ([#480](https://github.com/alltuner/vibetuner/issues/480)) ([5652e5f](https://github.com/alltuner/vibetuner/commit/5652e5f9501d8d567dbe8d698b203d86321e2269))


### Bug Fixes

* configure UV cache dependency glob for monorepo structure ([#482](https://github.com/alltuner/vibetuner/issues/482)) ([54a19b9](https://github.com/alltuner/vibetuner/commit/54a19b97a8e6730c94eec43ac9c1e1dbb81535ed))

## [2.19.6](https://github.com/alltuner/vibetuner/compare/v2.19.5...v2.19.6) (2025-11-13)


### Bug Fixes

* add GH_TOKEN to plan-release step for gh CLI ([#477](https://github.com/alltuner/vibetuner/issues/477)) ([5ebaadb](https://github.com/alltuner/vibetuner/commit/5ebaadbc95c049b998ec4e90e79a54bb7a7b1375))

## [2.19.5](https://github.com/alltuner/vibetuner/compare/v2.19.4...v2.19.5) (2025-11-13)


### Bug Fixes

* handle missing version in workflow_dispatch ([#475](https://github.com/alltuner/vibetuner/issues/475)) ([dbe1f25](https://github.com/alltuner/vibetuner/commit/dbe1f252d05ef583754336a96f54a7e224a02e64))

## [2.19.4](https://github.com/alltuner/vibetuner/compare/v2.19.3...v2.19.4) (2025-11-13)


### Bug Fixes

* correct documentation deployment logic ([#473](https://github.com/alltuner/vibetuner/issues/473)) ([49ee4ab](https://github.com/alltuner/vibetuner/commit/49ee4abe8fafb94752237b52027aabf2925c0915))

## [2.19.3](https://github.com/alltuner/vibetuner/compare/v2.19.2...v2.19.3) (2025-11-13)


### Bug Fixes

* restore npm trusted publishing for JS package ([#472](https://github.com/alltuner/vibetuner/issues/472)) ([bd77cfb](https://github.com/alltuner/vibetuner/commit/bd77cfb46af692e9d5861d92d96f8c25a73fab79))


### Code Refactoring

* simplify version parsing in release workflow ([#470](https://github.com/alltuner/vibetuner/issues/470)) ([8c79d5f](https://github.com/alltuner/vibetuner/commit/8c79d5f9c0929ea67acd04f756e476bb5c41f8c7))

## [2.19.2](https://github.com/alltuner/vibetuner/compare/v2.19.1...v2.19.2) (2025-11-13)


### Bug Fixes

* use uvx with mkdocs-material for docs build ([#468](https://github.com/alltuner/vibetuner/issues/468)) ([3de7b1e](https://github.com/alltuner/vibetuner/commit/3de7b1ed44d29f5c9e2d8e6711f11b212302c131))

## [2.19.1](https://github.com/alltuner/vibetuner/compare/v2.19.0...v2.19.1) (2025-11-13)


### Bug Fixes

* improve release workflow with Bun setup and proper version commands ([#465](https://github.com/alltuner/vibetuner/issues/465)) ([1f84ed2](https://github.com/alltuner/vibetuner/commit/1f84ed2bc6ce65933f80a4ba672bf5f301430d14))


### Miscellaneous Chores

* **deps:** update actions/upload-pages-artifact action to v4 ([#467](https://github.com/alltuner/vibetuner/issues/467)) ([5a7e978](https://github.com/alltuner/vibetuner/commit/5a7e978d81eea93929e7c57f00bf87007a8fc511))

## [2.19.0](https://github.com/alltuner/vibetuner/compare/v2.18.4...v2.19.0) (2025-11-13)


### Features

* simplify release workflow structure ([#460](https://github.com/alltuner/vibetuner/issues/460)) ([67efee9](https://github.com/alltuner/vibetuner/commit/67efee9372843ac4e4ecf8512469eb3332db2af8))


### Bug Fixes

* resolve GitHub Actions syntax errors ([#463](https://github.com/alltuner/vibetuner/issues/463)) ([7bec8e8](https://github.com/alltuner/vibetuner/commit/7bec8e8352ee0dfb1a31c7548c80764b6606db65))


### Miscellaneous Chores

* **deps:** update actions/setup-python action to v6 ([#462](https://github.com/alltuner/vibetuner/issues/462)) ([85e5e99](https://github.com/alltuner/vibetuner/commit/85e5e996d5ca2d0cf514e5b9a66877683c15c692))

## [2.18.4](https://github.com/alltuner/vibetuner/compare/v2.18.3...v2.18.4) (2025-11-13)


### Bug Fixes

* properly handle force flags in release workflow ([#458](https://github.com/alltuner/vibetuner/issues/458)) ([589a205](https://github.com/alltuner/vibetuner/commit/589a20558007c98902c9b5315f67df5877e4b192))

## [2.18.3](https://github.com/alltuner/vibetuner/compare/v2.18.2...v2.18.3) (2025-11-13)


### Bug Fixes

* fixes bug [#449](https://github.com/alltuner/vibetuner/issues/449) ([#456](https://github.com/alltuner/vibetuner/issues/456)) ([8d7d879](https://github.com/alltuner/vibetuner/commit/8d7d8790fbfd49ddb987e74ab12b3fa1b3021afb))

## [2.18.2](https://github.com/alltuner/vibetuner/compare/v2.18.1...v2.18.2) (2025-11-12)


### Miscellaneous Chores

* add gh issue create to allowed tools without approval ([#453](https://github.com/alltuner/vibetuner/issues/453)) ([da8363e](https://github.com/alltuner/vibetuner/commit/da8363e631491ee71230befadc62ccab9090fe28))


### Documentation Updates

* clarify lifespan execution stages with inline comments ([#455](https://github.com/alltuner/vibetuner/issues/455)) ([f80abee](https://github.com/alltuner/vibetuner/commit/f80abee468356c57d25ee1894d4fd63e6afb1328))

## [2.18.1](https://github.com/alltuner/vibetuner/compare/v2.18.0...v2.18.1) (2025-11-12)


### CI/CD Changes

* consolidate release workflows into single file ([#445](https://github.com/alltuner/vibetuner/issues/445)) ([7548aaa](https://github.com/alltuner/vibetuner/commit/7548aaa752fce316692acedbd4dad376a54ddcc0))

## [2.18.0](https://github.com/alltuner/vibetuner/compare/v2.17.12...v2.18.0) (2025-11-12)


### Features

* allow users to extend FastAPI lifespan ([#442](https://github.com/alltuner/vibetuner/issues/442)) ([14c3c18](https://github.com/alltuner/vibetuner/commit/14c3c187d955a89b2f3256a2ecf0b1c807c96e25))


### Documentation Updates

* reorganize agent documentation and add comprehensive justfile references ([#444](https://github.com/alltuner/vibetuner/issues/444)) ([2c1b1e5](https://github.com/alltuner/vibetuner/commit/2c1b1e5f0bb504349cf264357d883ef1b8c4b05c))

## [2.17.12](https://github.com/alltuner/vibetuner/compare/v2.17.11...v2.17.12) (2025-11-12)


### Bug Fixes

* adds yaml linter and simplifies the ignore logic for type checking ([#441](https://github.com/alltuner/vibetuner/issues/441)) ([30628bf](https://github.com/alltuner/vibetuner/commit/30628bf204e62de33a31035e6e73611d156feb36))
* ensure jinja code is properly linted in scaffolded projects ([#439](https://github.com/alltuner/vibetuner/issues/439)) ([07cc301](https://github.com/alltuner/vibetuner/commit/07cc3016088f00a9199852473c9143da2ef55122))

## [2.17.11](https://github.com/alltuner/vibetuner/compare/v2.17.10...v2.17.11) (2025-11-11)


### Bug Fixes

* detect merge conflicts when updating scaffolding ([#434](https://github.com/alltuner/vibetuner/issues/434)) ([3ddde7c](https://github.com/alltuner/vibetuner/commit/3ddde7c931b5ba222fcbea45fd3eda13404d91bf))


### Miscellaneous Chores

* configure renovate ([#436](https://github.com/alltuner/vibetuner/issues/436)) ([358601f](https://github.com/alltuner/vibetuner/commit/358601fe584238ff166a7b32da30fb3bbd04e36a))


### CI/CD Changes

* enable dependabot ([#437](https://github.com/alltuner/vibetuner/issues/437)) ([da83795](https://github.com/alltuner/vibetuner/commit/da837954b3bb6a7f0210af80579d6f8698d4a490))
* fix trusted publishing ([#433](https://github.com/alltuner/vibetuner/issues/433)) ([0cd54ff](https://github.com/alltuner/vibetuner/commit/0cd54ff17882dde3426d8dd645e951dee96d8619))
* get changelog properly populated with all commit types ([#438](https://github.com/alltuner/vibetuner/issues/438)) ([b0bfa11](https://github.com/alltuner/vibetuner/commit/b0bfa1133cdeb59ba9aa67a874631f8d9c30c053))

## [2.17.10](https://github.com/alltuner/vibetuner/compare/v2.17.9...v2.17.10) (2025-11-11)


### Miscellaneous Chores

* better to ignore pyproject from the toml linter ([#430](https://github.com/alltuner/vibetuner/issues/430)) ([0dacfd2](https://github.com/alltuner/vibetuner/commit/0dacfd2cb464e616ce81dee1687b4e322cc0d1a6))

## [2.17.9](https://github.com/alltuner/vibetuner/compare/v2.17.8...v2.17.9) (2025-11-11)


### Bug Fixes

* fix wrong path for tasks worker redis url ([#428](https://github.com/alltuner/vibetuner/issues/428)) ([0bd5fc1](https://github.com/alltuner/vibetuner/commit/0bd5fc1bf4cabb25ac95418397fcf547d96349e9))

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
