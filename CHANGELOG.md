# Changelog

## [2.36.1](https://github.com/alltuner/vibetuner/compare/v2.36.0...v2.36.1) (2025-12-01)


### Documentation Updates

* update documentation for SQLModel support and flexible databases ([#628](https://github.com/alltuner/vibetuner/issues/628)) ([9cd7db5](https://github.com/alltuner/vibetuner/commit/9cd7db53564758d2ec26bce4c9527af0ea3b58d7))

## [2.36.0](https://github.com/alltuner/vibetuner/compare/v2.35.1...v2.36.0) (2025-12-01)


### Features

* add optional SQLModel/SQLAlchemy support ([#623](https://github.com/alltuner/vibetuner/issues/623)) ([4fa2249](https://github.com/alltuner/vibetuner/commit/4fa2249959ab5230f31c4b2ea4e2b210ae932a78))


### Code Refactoring

* move SQLModel schema creation to CLI and improve local dev workflow ([#627](https://github.com/alltuner/vibetuner/issues/627)) ([7d89e1d](https://github.com/alltuner/vibetuner/commit/7d89e1d6498233ea54298f811a3a9e558f085765))

## [2.35.1](https://github.com/alltuner/vibetuner/compare/v2.35.0...v2.35.1) (2025-12-01)


### Documentation Updates

* fix outdated MongoDB and template documentation ([#621](https://github.com/alltuner/vibetuner/issues/621)) ([2b3d2bf](https://github.com/alltuner/vibetuner/commit/2b3d2bf033fc6fc88d1308735105b4d72b5f9928))

## [2.35.0](https://github.com/alltuner/vibetuner/compare/v2.34.4...v2.35.0) (2025-11-30)


### Features

* make MongoDB and Redis configuration optional ([#618](https://github.com/alltuner/vibetuner/issues/618)) ([570a84e](https://github.com/alltuner/vibetuner/commit/570a84ef67c65631adac84fd5d3fa6a3553eab63))


### Miscellaneous Chores

* update dependencies and pre-commit hooks ([#616](https://github.com/alltuner/vibetuner/issues/616)) ([df09832](https://github.com/alltuner/vibetuner/commit/df09832e86b8eee58f09cd27c98a5bbc47bc96c1))

## [2.34.4](https://github.com/alltuner/vibetuner/compare/v2.34.3...v2.34.4) (2025-11-27)


### Bug Fixes

* **docker:** use python directly in healthcheck ([#614](https://github.com/alltuner/vibetuner/issues/614)) ([09fa99e](https://github.com/alltuner/vibetuner/commit/09fa99e38cec047a83b8837c59649b08c21fc2c2))

## [2.34.3](https://github.com/alltuner/vibetuner/compare/v2.34.2...v2.34.3) (2025-11-27)


### Bug Fixes

* **docker:** add --link to all COPY instructions in runtime stage ([#609](https://github.com/alltuner/vibetuner/issues/609)) ([61a15cc](https://github.com/alltuner/vibetuner/commit/61a15cc02fa9e8d2b13c997e989ae3e1725bd411))

## [2.34.2](https://github.com/alltuner/vibetuner/compare/v2.34.1...v2.34.2) (2025-11-27)


### Bug Fixes

* do not include all extras ([#606](https://github.com/alltuner/vibetuner/issues/606)) ([c50f0ba](https://github.com/alltuner/vibetuner/commit/c50f0ba4b7c5f09d3454d5fc3dd93e4ccbe92d59))

## [2.34.1](https://github.com/alltuner/vibetuner/compare/v2.34.0...v2.34.1) (2025-11-27)


### Miscellaneous Chores

* extend allowed WebFetch hosts for dependency documentation ([#604](https://github.com/alltuner/vibetuner/issues/604)) ([2bd66c1](https://github.com/alltuner/vibetuner/commit/2bd66c163c75a0045686e3bd7d92c244c71df675))

## [2.34.0](https://github.com/alltuner/vibetuner/compare/v2.33.0...v2.34.0) (2025-11-27)


### Features

* **docker:** optimize Dockerfile with non-editable install and multi-stage build ([#601](https://github.com/alltuner/vibetuner/issues/601)) ([cac6f51](https://github.com/alltuner/vibetuner/commit/cac6f51e9beb46cd636a27957d2ad828f3074aaa))

## [2.33.0](https://github.com/alltuner/vibetuner/compare/v2.32.0...v2.33.0) (2025-11-27)


### Features

* make production worker verbose logging configurable via settings.debug ([#596](https://github.com/alltuner/vibetuner/issues/596)) ([a2171b1](https://github.com/alltuner/vibetuner/commit/a2171b14321ed628aac8a52710f41e4fd56b6b7a))

## [2.32.0](https://github.com/alltuner/vibetuner/compare/v2.31.1...v2.32.0) (2025-11-26)


### Features

* add configurable Streaq worker concurrency ([#593](https://github.com/alltuner/vibetuner/issues/593)) ([aa2d94e](https://github.com/alltuner/vibetuner/commit/aa2d94e7e7aa3cba1023c9cdd1a7aac5993e2624))


### Bug Fixes

* **template:** use app config in lifespan modules ([#591](https://github.com/alltuner/vibetuner/issues/591)) ([9382f7d](https://github.com/alltuner/vibetuner/commit/9382f7d48be2eb269b95e591413adadd130a9c19))

## [2.31.1](https://github.com/alltuner/vibetuner/compare/v2.31.0...v2.31.1) (2025-11-26)


### Miscellaneous Chores

* update dependencies ([#587](https://github.com/alltuner/vibetuner/issues/587)) ([4cfd281](https://github.com/alltuner/vibetuner/commit/4cfd281dbc8b728efd007f34399b8fcd037f6320))

## [2.31.0](https://github.com/alltuner/vibetuner/compare/v2.30.3...v2.31.0) (2025-11-26)


### Features

* optimize Docker build caching and parallelization ([#585](https://github.com/alltuner/vibetuner/issues/585)) ([4d4e5d2](https://github.com/alltuner/vibetuner/commit/4d4e5d2f6e5223264374fc6f581d29f696cb44a7))

## [2.30.3](https://github.com/alltuner/vibetuner/compare/v2.30.2...v2.30.3) (2025-11-26)


### Bug Fixes

* use consistent ENVIRONMENT values (prod/dev) ([#579](https://github.com/alltuner/vibetuner/issues/579)) ([04bbbe0](https://github.com/alltuner/vibetuner/commit/04bbbe0fc653c4023ed1ce2b844afb2121df6991))

## [2.30.2](https://github.com/alltuner/vibetuner/compare/v2.30.1...v2.30.2) (2025-11-26)


### Miscellaneous Chores

* update dependencies ([#576](https://github.com/alltuner/vibetuner/issues/576)) ([f9b46e0](https://github.com/alltuner/vibetuner/commit/f9b46e081f51a3cdb5ac637742cffa1d787bde4b))

## [2.30.1](https://github.com/alltuner/vibetuner/compare/v2.30.0...v2.30.1) (2025-11-25)


### Code Refactoring

* remove custom NamespacedRedis wrapper ([#574](https://github.com/alltuner/vibetuner/issues/574)) ([8e50a96](https://github.com/alltuner/vibetuner/commit/8e50a961e6d95b092edc3fa37521a1c4d0abbfd0))

## [2.30.0](https://github.com/alltuner/vibetuner/compare/v2.29.0...v2.30.0) (2025-11-25)


### Features

* add sdiff and sdiffstore to NamespacedRedis ([#571](https://github.com/alltuner/vibetuner/issues/571)) ([1cfc143](https://github.com/alltuner/vibetuner/commit/1cfc14335b2958bdfd3b8036d5fc2be3a5de2380))


### Bug Fixes

* resolve set type hint shadowing in NamespacedRedis ([#573](https://github.com/alltuner/vibetuner/issues/573)) ([383513b](https://github.com/alltuner/vibetuner/commit/383513bbcd3519a348346db0827caf99954ab500))

## [2.29.0](https://github.com/alltuner/vibetuner/compare/v2.28.6...v2.29.0) (2025-11-25)


### Features

* add Redis key namespacing by project and environment ([#567](https://github.com/alltuner/vibetuner/issues/567)) ([4ebacd9](https://github.com/alltuner/vibetuner/commit/4ebacd95e09225e124eee92f8ecce1ccaf58b167))

## [2.28.6](https://github.com/alltuner/vibetuner/compare/v2.28.5...v2.28.6) (2025-11-25)


### Code Refactoring

* move core-template-symlink to scaffold link subcommand ([#565](https://github.com/alltuner/vibetuner/issues/565)) ([f7768d2](https://github.com/alltuner/vibetuner/commit/f7768d2eb511e514fdb41942f28ded8e69c05dfd))

## [2.28.5](https://github.com/alltuner/vibetuner/compare/v2.28.4...v2.28.5) (2025-11-24)


### Bug Fixes

* handle existing symlink in core-template-symlink command ([#562](https://github.com/alltuner/vibetuner/issues/562)) ([8e709ea](https://github.com/alltuner/vibetuner/commit/8e709ea6ae86a732105db49396dd40c77ead8188))

## [2.28.4](https://github.com/alltuner/vibetuner/compare/v2.28.3...v2.28.4) (2025-11-24)


### Bug Fixes

* implement check_bucket flag in BlobService.object_exists ([#560](https://github.com/alltuner/vibetuner/issues/560)) ([890bd1e](https://github.com/alltuner/vibetuner/commit/890bd1ef9351f13464a6a2c07a11cc97a22c3891))
* remove project-specific models from link inference ([#559](https://github.com/alltuner/vibetuner/issues/559)) ([8128ab8](https://github.com/alltuner/vibetuner/commit/8128ab86cdc7f2bd31d0764b42d29a180d69b5d4))
* secure debug routes in production with token-based auth ([#556](https://github.com/alltuner/vibetuner/issues/556)) ([0236f35](https://github.com/alltuner/vibetuner/commit/0236f351cf838700b818892e6d9bee0559cc29b0))


### Miscellaneous Chores

* update dependencies ([#561](https://github.com/alltuner/vibetuner/issues/561)) ([73354dc](https://github.com/alltuner/vibetuner/commit/73354dcd4a4594cbe9ee383e25732fc2ee849fdb))

## [2.28.3](https://github.com/alltuner/vibetuner/compare/v2.28.2...v2.28.3) (2025-11-24)


### Bug Fixes

* **deps:** update dependency copier to &gt;=9.11.0,&lt;9.11.1 ([#554](https://github.com/alltuner/vibetuner/issues/554)) ([efa7ba8](https://github.com/alltuner/vibetuner/commit/efa7ba80fa774cedb74a117bb114bfa00930bee2))
* **email:** replace blocking boto3 with async aioboto3 in SESEmailService ([#552](https://github.com/alltuner/vibetuner/issues/552)) ([9f3243b](https://github.com/alltuner/vibetuner/commit/9f3243be6311317a3b558326eb60b9f8c08c75ef)), closes [#451](https://github.com/alltuner/vibetuner/issues/451)


### Miscellaneous Chores

* **deps:** update actions/checkout action to v6 ([#553](https://github.com/alltuner/vibetuner/issues/553)) ([0201254](https://github.com/alltuner/vibetuner/commit/02012545f6980795e4d66c53eb25a3a301ed5a0d))
* remove unused ffmpeg dependency from Dockerfile ([#549](https://github.com/alltuner/vibetuner/issues/549)) ([d2cf0be](https://github.com/alltuner/vibetuner/commit/d2cf0be716496dc474e7037dd95f92fb28c0a657)), closes [#505](https://github.com/alltuner/vibetuner/issues/505)
* update dependencies ([#555](https://github.com/alltuner/vibetuner/issues/555)) ([5a6d351](https://github.com/alltuner/vibetuner/commit/5a6d351e74b467cea8beb8d6b43b77a185310a3f))

## [2.28.2](https://github.com/alltuner/vibetuner/compare/v2.28.1...v2.28.2) (2025-11-19)


### Code Refactoring

* **services:** extract S3 operations into reusable storage service ([#546](https://github.com/alltuner/vibetuner/issues/546)) ([3814174](https://github.com/alltuner/vibetuner/commit/3814174af4ffc5006886be028b1c7139e220aaee))

## [2.28.1](https://github.com/alltuner/vibetuner/compare/v2.28.0...v2.28.1) (2025-11-19)


### Miscellaneous Chores

* **deps:** update python docker tag ([#479](https://github.com/alltuner/vibetuner/issues/479)) ([20836ba](https://github.com/alltuner/vibetuner/commit/20836ba14de4377f55051fc0d3b98e767f5cc4bc))
* update dependencies ([#545](https://github.com/alltuner/vibetuner/issues/545)) ([fe6b255](https://github.com/alltuner/vibetuner/commit/fe6b255d79388e5de5a6718e5f48bb6a6129f98a))

## [2.28.0](https://github.com/alltuner/vibetuner/compare/v2.27.1...v2.28.0) (2025-11-19)


### Features

* replace pre-commit with prek ([#541](https://github.com/alltuner/vibetuner/issues/541)) ([fb3ddc2](https://github.com/alltuner/vibetuner/commit/fb3ddc2dc7cba9aae19caa16bbe16abc22cabcee))

## [2.27.1](https://github.com/alltuner/vibetuner/compare/v2.27.0...v2.27.1) (2025-11-19)


### Bug Fixes

* make context management for tasks a bit nicer to extend ([#539](https://github.com/alltuner/vibetuner/issues/539)) ([0c420fd](https://github.com/alltuner/vibetuner/commit/0c420fdefac682512eca643aa0707338f759bd9d))


### Miscellaneous Chores

* bump rumdl from 0.0.177 to 0.0.178 in /vibetuner-py ([#537](https://github.com/alltuner/vibetuner/issues/537)) ([e944739](https://github.com/alltuner/vibetuner/commit/e94473911c38d42dd8ca7fbcaf723c80e0d6e457))
* **deps:** update redis docker tag to v8.4 ([#538](https://github.com/alltuner/vibetuner/issues/538)) ([a07c799](https://github.com/alltuner/vibetuner/commit/a07c799825556b1b689420042ef22cf3f88afb2c))

## [2.27.0](https://github.com/alltuner/vibetuner/compare/v2.26.9...v2.27.0) (2025-11-17)


### Features

* add custom Jinja2 filter registration system ([#535](https://github.com/alltuner/vibetuner/issues/535)) ([64cc6d8](https://github.com/alltuner/vibetuner/commit/64cc6d8df843354ade7c3e1a0e29c88b56a7c6c2))

## [2.26.9](https://github.com/alltuner/vibetuner/compare/v2.26.8...v2.26.9) (2025-11-17)


### Bug Fixes

* docker build for core templates ([#532](https://github.com/alltuner/vibetuner/issues/532)) ([15338d5](https://github.com/alltuner/vibetuner/commit/15338d529819af24d625d1e6e8d3224da4f3bc6f))
* fix compose config ([#534](https://github.com/alltuner/vibetuner/issues/534)) ([c63e35a](https://github.com/alltuner/vibetuner/commit/c63e35ade39e30c041604d6908212ce8379400bb))

## [2.26.8](https://github.com/alltuner/vibetuner/compare/v2.26.7...v2.26.8) (2025-11-17)


### Bug Fixes

* allow frontend to have a custom context ([#530](https://github.com/alltuner/vibetuner/issues/530)) ([9014f9f](https://github.com/alltuner/vibetuner/commit/9014f9faf2c8f78bc89c4a26929e44a45d64fa75))

## [2.26.7](https://github.com/alltuner/vibetuner/compare/v2.26.6...v2.26.7) (2025-11-17)


### Bug Fixes

* allow custom middlewares ([#528](https://github.com/alltuner/vibetuner/issues/528)) ([658f36a](https://github.com/alltuner/vibetuner/commit/658f36ae3ad3d75fa34d62e7781c00e509370726))

## [2.26.6](https://github.com/alltuner/vibetuner/compare/v2.26.5...v2.26.6) (2025-11-17)


### Bug Fixes

* improve annotation for async generators ([#526](https://github.com/alltuner/vibetuner/issues/526)) ([1309233](https://github.com/alltuner/vibetuner/commit/13092335569e1dba764e1a0ae3fbaa0042262d1d))

## [2.26.5](https://github.com/alltuner/vibetuner/compare/v2.26.4...v2.26.5) (2025-11-17)


### Code Refactoring

* **tasks:** migrate from context-based to lifespan-based pattern ([#524](https://github.com/alltuner/vibetuner/issues/524)) ([a84852c](https://github.com/alltuner/vibetuner/commit/a84852cb410c7196b0b4bba9ca78ea96dfd4b8b0))

## [2.26.4](https://github.com/alltuner/vibetuner/compare/v2.26.3...v2.26.4) (2025-11-17)


### Miscellaneous Chores

* update pre-commit ([#522](https://github.com/alltuner/vibetuner/issues/522)) ([2248a73](https://github.com/alltuner/vibetuner/commit/2248a73a6434abdd4f813ad6ea5a96d69126adda))

## [2.26.3](https://github.com/alltuner/vibetuner/compare/v2.26.2...v2.26.3) (2025-11-15)


### Miscellaneous Chores

* remove backwards compatibility for legacy template and module locations ([#520](https://github.com/alltuner/vibetuner/issues/520)) ([35ca29c](https://github.com/alltuner/vibetuner/commit/35ca29cd6bef7f1c248a181a3bf063ebe1a4d3ee))

## [2.26.2](https://github.com/alltuner/vibetuner/compare/v2.26.1...v2.26.2) (2025-11-15)


### Bug Fixes

* bootstrap Release Please for template ([#518](https://github.com/alltuner/vibetuner/issues/518)) ([ce07e3c](https://github.com/alltuner/vibetuner/commit/ce07e3ca014d8772b11d6910931f693d07d610b0))

## [2.26.1](https://github.com/alltuner/vibetuner/compare/v2.26.0...v2.26.1) (2025-11-15)


### Bug Fixes

* release-please fails without that file ([#516](https://github.com/alltuner/vibetuner/issues/516)) ([46285ea](https://github.com/alltuner/vibetuner/commit/46285eae28d2f2b1848a3ea555708be23806a43d))

## [2.26.0](https://github.com/alltuner/vibetuner/compare/v2.25.0...v2.26.0) (2025-11-15)


### Features

* add Release Please integration to vibetuner-template ([#514](https://github.com/alltuner/vibetuner/issues/514)) ([cb30061](https://github.com/alltuner/vibetuner/commit/cb300616e662109b217cff71fe2eb3b7a998b826))

## [2.25.0](https://github.com/alltuner/vibetuner/compare/v2.24.1...v2.25.0) (2025-11-15)


### Features

* add symlink support for core frontend templates ([#512](https://github.com/alltuner/vibetuner/issues/512)) ([ec27d40](https://github.com/alltuner/vibetuner/commit/ec27d40801dc5dd8ad0b031f540bafb80eb361ce))

## [2.24.1](https://github.com/alltuner/vibetuner/compare/v2.24.0...v2.24.1) (2025-11-15)


### Miscellaneous Chores

* move custom commands to template directory ([#510](https://github.com/alltuner/vibetuner/issues/510)) ([dad108a](https://github.com/alltuner/vibetuner/commit/dad108ac5971c5e44fca0e311eea5f805c066969))

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
