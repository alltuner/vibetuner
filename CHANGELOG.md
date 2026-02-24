# Changelog

## [8.2.6](https://github.com/alltuner/vibetuner/compare/v8.2.5...v8.2.6) (2026-02-24)


### Bug Fixes

* use frozen lockfiles, enable bytecode compilation, remove git from Dockerfile ([#1248](https://github.com/alltuner/vibetuner/issues/1248)) ([2634084](https://github.com/alltuner/vibetuner/commit/26340841aaf97a59106e12a43181d8b59b7d521b))

## [8.2.5](https://github.com/alltuner/vibetuner/compare/v8.2.4...v8.2.5) (2026-02-24)


### Bug Fixes

* load .env and .env.local instead of ../.env ([#1243](https://github.com/alltuner/vibetuner/issues/1243)) ([79ab1e2](https://github.com/alltuner/vibetuner/commit/79ab1e27abcb5d65938d59d34cb29b08d7e651c9))

## [8.2.4](https://github.com/alltuner/vibetuner/compare/v8.2.3...v8.2.4) (2026-02-23)


### Bug Fixes

* prevent cp -r .core-templates failure from being masked by || true ([#1242](https://github.com/alltuner/vibetuner/issues/1242)) ([f2b74fb](https://github.com/alltuner/vibetuner/commit/f2b74fb0a74cce52389bf3a380714ff008a18c73))


### Miscellaneous Chores

* update dependencies and pre-commit hooks ([#1239](https://github.com/alltuner/vibetuner/issues/1239)) ([54c28eb](https://github.com/alltuner/vibetuner/commit/54c28ebe91adf31dddd9a7a74ae4c48350dfb2d2))

## [8.2.3](https://github.com/alltuner/vibetuner/compare/v8.2.2...v8.2.3) (2026-02-18)


### Bug Fixes

* skip OAuth relay URL in production environment ([#1237](https://github.com/alltuner/vibetuner/issues/1237)) ([d171564](https://github.com/alltuner/vibetuner/commit/d171564e3847c7c4dc6762fcab98ba9937465a1e))


### Miscellaneous Chores

* **deps:** bump authlib from 1.6.7 to 1.6.8 in /vibetuner-py ([#1233](https://github.com/alltuner/vibetuner/issues/1233)) ([ddcf27c](https://github.com/alltuner/vibetuner/commit/ddcf27c1df4de531655b21d3ccba1f696e5427e5))
* **deps:** bump htmx.org from 4.0.0-alpha6 to 4.0.0-alpha7 in /vibetuner-js ([#1236](https://github.com/alltuner/vibetuner/issues/1236)) ([3546c1b](https://github.com/alltuner/vibetuner/commit/3546c1b8aac3cca7f14b9be8f33c6e232771b0b2))
* **deps:** bump pydantic-settings from 2.12.0 to 2.13.0 in /vibetuner-py ([#1234](https://github.com/alltuner/vibetuner/issues/1234)) ([3449f2e](https://github.com/alltuner/vibetuner/commit/3449f2e1ebd79914df0610ba80c628c79b198d89))
* **deps:** bump rumdl from 0.1.18 to 0.1.22 in /vibetuner-py ([#1235](https://github.com/alltuner/vibetuner/issues/1235)) ([10d53de](https://github.com/alltuner/vibetuner/commit/10d53de45125595e7e893e7f8affa582b4160eb7))
* **deps:** bump sqlmodel from 0.0.33 to 0.0.34 in /vibetuner-py ([#1232](https://github.com/alltuner/vibetuner/issues/1232)) ([f2efd71](https://github.com/alltuner/vibetuner/commit/f2efd718b2efa0becce19f4f3385c3c4c1f8c3d8))
* **deps:** bump types-authlib from 1.6.7.20260208 to 1.6.8.20260215 in /vibetuner-py ([#1231](https://github.com/alltuner/vibetuner/issues/1231)) ([cc98884](https://github.com/alltuner/vibetuner/commit/cc98884a58c9a7f9069d2110b0226dc39fc9cad7))

## [8.2.2](https://github.com/alltuner/vibetuner/compare/v8.2.1...v8.2.2) (2026-02-12)


### Miscellaneous Chores

* add missing README.md ([#1228](https://github.com/alltuner/vibetuner/issues/1228)) ([da45e0d](https://github.com/alltuner/vibetuner/commit/da45e0daf5396eb58052f55605d5a6f6f3efcc32))

## [8.2.1](https://github.com/alltuner/vibetuner/compare/v8.2.0...v8.2.1) (2026-02-12)


### Miscellaneous Chores

* remove README template and preserve project locale files ([#1226](https://github.com/alltuner/vibetuner/issues/1226)) ([126d200](https://github.com/alltuner/vibetuner/commit/126d200db202e0c71752aca90933824d4920c8a3))

## [8.2.0](https://github.com/alltuner/vibetuner/compare/v8.1.2...v8.2.0) (2026-02-12)


### Features

* add OAuth relay for multi-app local development ([#1225](https://github.com/alltuner/vibetuner/issues/1225)) ([ccfa5f5](https://github.com/alltuner/vibetuner/commit/ccfa5f58d81109aa3b3574072856fbea89248d4c))


### Bug Fixes

* quote command substitution in setup-tw-sources script ([#1223](https://github.com/alltuner/vibetuner/issues/1223)) ([0aa9fd6](https://github.com/alltuner/vibetuner/commit/0aa9fd6f9ec170f0b0a596056cf2625a295d2a2f))

## [8.1.2](https://github.com/alltuner/vibetuner/compare/v8.1.1...v8.1.2) (2026-02-12)


### Bug Fixes

* add invoke_without_command=True to doctor_app ([#1220](https://github.com/alltuner/vibetuner/issues/1220)) ([99521db](https://github.com/alltuner/vibetuner/commit/99521db8534800f99630aa63110f61f5bf57e21f))

## [8.1.1](https://github.com/alltuner/vibetuner/compare/v8.1.0...v8.1.1) (2026-02-12)


### Bug Fixes

* prevent infinite recursion when user CLI re-exports vibetuner.cli.app ([#1217](https://github.com/alltuner/vibetuner/issues/1217)) ([894f01f](https://github.com/alltuner/vibetuner/commit/894f01f5e17c6d08139fe378063fc9726fd192e1))

## [8.1.0](https://github.com/alltuner/vibetuner/compare/v8.0.1...v8.1.0) (2026-02-12)


### Features

* print HTTPS localdev URL on startup when LOCALDEV_URL is configured ([#1214](https://github.com/alltuner/vibetuner/issues/1214)) ([fc6aeb7](https://github.com/alltuner/vibetuner/commit/fc6aeb717c1549d1ecf5e803f8fce663e534c5d0))

## [8.0.1](https://github.com/alltuner/vibetuner/compare/v8.0.0...v8.0.1) (2026-02-12)


### Bug Fixes

* add get_optional_blob_service and improve error handling ([#1207](https://github.com/alltuner/vibetuner/issues/1207)) ([d00fbab](https://github.com/alltuner/vibetuner/commit/d00fbab5db6d7ffc8b94973c4fe4d263a4d8a0b3))
* auto-create SQL tables on startup in dev mode ([#1206](https://github.com/alltuner/vibetuner/issues/1206)) ([2ddacf2](https://github.com/alltuner/vibetuner/commit/2ddacf2e87294154714c046d9a3c310e0a4918b5))


### Miscellaneous Chores

* **deps:** update dependency @alltuner/vibetuner to v8 ([#1199](https://github.com/alltuner/vibetuner/issues/1199)) ([961948a](https://github.com/alltuner/vibetuner/commit/961948afd899080d45dd685a92f959ce624b4793))


### Documentation Updates

* document CRUD factory hook signatures ([#1212](https://github.com/alltuner/vibetuner/issues/1212)) ([6d62b35](https://github.com/alltuner/vibetuner/commit/6d62b3562e43c9ca295444674056d62c61903776))
* document that template filters returning HTML must use Markup ([#1208](https://github.com/alltuner/vibetuner/issues/1208)) ([cae82f9](https://github.com/alltuner/vibetuner/commit/cae82f9c39ad34228c5841574f6a77523ca906df))
* document worker vs frontend lifespan signature difference ([#1211](https://github.com/alltuner/vibetuner/issues/1211)) ([c9bd59f](https://github.com/alltuner/vibetuner/commit/c9bd59f5d0239e9bcae50e656c8a11472c28acff))
* mention vibetuner db create-schema in Quick Start ([#1209](https://github.com/alltuner/vibetuner/issues/1209)) ([2e63ac6](https://github.com/alltuner/vibetuner/commit/2e63ac69e03a06dad3385ea9efa27b54553da7be))

## [8.0.0](https://github.com/alltuner/vibetuner/compare/v7.0.1...v8.0.0) (2026-02-12)


### ⚠ BREAKING CHANGES

* upgrade htmx from v2.0.8 to v4.0 (alpha) ([#1043](https://github.com/alltuner/vibetuner/issues/1043))

### Features

* add --auto-port support for worker monitoring UI ([#1040](https://github.com/alltuner/vibetuner/issues/1040)) ([e0d61b1](https://github.com/alltuner/vibetuner/commit/e0d61b1bec50d4c3481b554611ecc709a29b561b))
* add --template and --branch options to scaffold commands ([#1178](https://github.com/alltuner/vibetuner/issues/1178)) ([84d0bc0](https://github.com/alltuner/vibetuner/commit/84d0bc00c90f9de47684f303ee4f9929d160ea65))
* add decorator-based API for runtime config values ([#988](https://github.com/alltuner/vibetuner/issues/988)) ([de87d31](https://github.com/alltuner/vibetuner/commit/de87d31f76d517aa322e01629edc8fd871de3ca1))
* add detailed health check reporting status of all connected services ([#984](https://github.com/alltuner/vibetuner/issues/984)) ([83ab37e](https://github.com/alltuner/vibetuner/commit/83ab37e259d0fd4d809af8c3069efc0a1163d5ca))
* add FastAPI Depends() wrappers for built-in services ([#983](https://github.com/alltuner/vibetuner/issues/983)) ([8e6bf19](https://github.com/alltuner/vibetuner/commit/8e6bf19c9122a7c2874e815c29690f57665eea23))
* add generic CRUD route factory for Beanie documents ([#996](https://github.com/alltuner/vibetuner/issues/996)) ([b85596e](https://github.com/alltuner/vibetuner/commit/b85596efdeece93c2e58e2ca3ba759b9a0126a06))
* add register_globals() and register_context_provider() for app-level template context ([#987](https://github.com/alltuner/vibetuner/issues/987)) ([0ad50a0](https://github.com/alltuner/vibetuner/commit/0ad50a086a7e4f602e5b92ba9801dcb6c83f20c9))
* add robust_task decorator with retries and dead letters ([#992](https://github.com/alltuner/vibetuner/issues/992)) ([f110dad](https://github.com/alltuner/vibetuner/commit/f110dadeffc32b62aa40d087b149d653766c7569))
* add sql_models field to VibetunerApp for explicit model registration ([#1144](https://github.com/alltuner/vibetuner/issues/1144)) ([88bcacb](https://github.com/alltuner/vibetuner/commit/88bcacb693a4779e7f4023dfbf711d8c2c8110f6))
* add SSE and real-time streaming helpers for HTMX ([#994](https://github.com/alltuner/vibetuner/issues/994)) ([02745f8](https://github.com/alltuner/vibetuner/commit/02745f854ce1081bf8ab0c51abe6d1b928ad2493))
* add template blocks reference page to debug panel ([#1041](https://github.com/alltuner/vibetuner/issues/1041)) ([c545f73](https://github.com/alltuner/vibetuner/commit/c545f736d1e7b814afca97b0eeddce0e79082f75))
* add testing utilities and pytest fixtures for vibetuner apps ([#1022](https://github.com/alltuner/vibetuner/issues/1022)) ([d4ced1d](https://github.com/alltuner/vibetuner/commit/d4ced1dbf6eefa7039d04a77ed55f17cd0e31b96))
* add vibetuner doctor CLI command ([#991](https://github.com/alltuner/vibetuner/issues/991)) ([64494e6](https://github.com/alltuner/vibetuner/commit/64494e636c4d6f61f223b3a611641b723a699b2a))
* allow context providers to access the current request ([#1174](https://github.com/alltuner/vibetuner/issues/1174)) ([abfec06](https://github.com/alltuner/vibetuner/commit/abfec06c7424551b5efc761a54d86c0e78f97846))
* allow custom OAuth providers via tune.py config ([#989](https://github.com/alltuner/vibetuner/issues/989)) ([6518281](https://github.com/alltuner/vibetuner/commit/6518281c2d225abcc9745ed67538d90b03b2919d))
* allow SQL-only projects without requiring MongoDB ([#1143](https://github.com/alltuner/vibetuner/issues/1143)) ([5e909c4](https://github.com/alltuner/vibetuner/commit/5e909c4b66734ef7e4f6a0268d38c686e3c4c73f))
* enable OpenAPI docs (/docs, /redoc) in DEBUG mode ([#1028](https://github.com/alltuner/vibetuner/issues/1028)) ([32890f5](https://github.com/alltuner/vibetuner/commit/32890f58c8171fcabcdcfafc7af72fa7be417243))
* generate project README from template variables ([#1175](https://github.com/alltuner/vibetuner/issues/1175)) ([c10a0d3](https://github.com/alltuner/vibetuner/commit/c10a0d3ee5ccac09321489dce9ec223216847c1b))
* make default_language configurable via copier.yml ([#985](https://github.com/alltuner/vibetuner/issues/985)) ([9a70897](https://github.com/alltuner/vibetuner/commit/9a70897a513bf293914352c3dbf7bd9ffa2c4457))
* mount Streaq task queue UI at /debug/tasks ([#993](https://github.com/alltuner/vibetuner/issues/993)) ([88bb81b](https://github.com/alltuner/vibetuner/commit/88bb81b967f1a00e2162fa83c6af66dd0023983a))
* **sse:** add input validation for SSE channel names ([#1097](https://github.com/alltuner/vibetuner/issues/1097)) ([bf21653](https://github.com/alltuner/vibetuner/commit/bf21653c3c22f9d8320b4f659270aad1e93cd5e1))
* upgrade htmx from v2.0.8 to v4.0 (alpha) ([#1043](https://github.com/alltuner/vibetuner/issues/1043)) ([88e81c7](https://github.com/alltuner/vibetuner/commit/88e81c79791c91c497929b4e3c906ad6a06017a0))


### Bug Fixes

* add content block alias inside body block in skeleton template ([#1016](https://github.com/alltuner/vibetuner/issues/1016)) ([edd728d](https://github.com/alltuner/vibetuner/commit/edd728d96d708a364ae9a26251184c4f135826fc))
* add defensive check for missing task_context in robust middleware ([#1193](https://github.com/alltuner/vibetuner/issues/1193)) ([c588cd5](https://github.com/alltuner/vibetuner/commit/c588cd5c36a76213c09808eb982611679d7ee1a3))
* add greenlet dependency required by SQLAlchemy async ([#1133](https://github.com/alltuner/vibetuner/issues/1133)) ([61cbaf0](https://github.com/alltuner/vibetuner/commit/61cbaf058fd27fcc3b6b089fbc3c473457abd660))
* allow extra fields on worker Context model ([#1176](https://github.com/alltuner/vibetuner/issues/1176)) ([a26efcc](https://github.com/alltuner/vibetuner/commit/a26efcc60601fe97d98c356a52f0bc23de624946))
* auto-generate partial update schema for PATCH endpoints ([#1034](https://github.com/alltuner/vibetuner/issues/1034)) ([f704175](https://github.com/alltuner/vibetuner/commit/f704175b5f5d8c75fef741c42bbc09d2b613ae2d))
* call _ensure_engine() lazily in get_session() ([#1134](https://github.com/alltuner/vibetuner/issues/1134)) ([30edd84](https://github.com/alltuner/vibetuner/commit/30edd849e8e8c5bbc404ac9990bf56aee7209e76))
* clarify create_crud_routes is Beanie-only in docs and comments ([#1190](https://github.com/alltuner/vibetuner/issues/1190)) ([cf1f1bb](https://github.com/alltuner/vibetuner/commit/cf1f1bbd1d46e44c6a54be9824e4f75f917a2fed))
* **cli:** register user CLI extensions as named subcommand groups ([#1127](https://github.com/alltuner/vibetuner/issues/1127)) ([fb7c10b](https://github.com/alltuner/vibetuner/commit/fb7c10bf640135cd0790cee7988b217b2825b936))
* convert ObjectId to string in field selection responses ([#1035](https://github.com/alltuner/vibetuner/issues/1035)) ([6939836](https://github.com/alltuner/vibetuner/commit/69398363f6082e5a99e102993b8ecf86d6ce3036))
* **crud:** add error handling for lifecycle hooks ([#1083](https://github.com/alltuner/vibetuner/issues/1083)) ([03a59f1](https://github.com/alltuner/vibetuner/commit/03a59f1e585758e32d7ec5696685806c566f80b3))
* **crud:** escape user input in MongoDB regex search query ([#1081](https://github.com/alltuner/vibetuner/issues/1081)) ([bd1eb7c](https://github.com/alltuner/vibetuner/commit/bd1eb7c5ddbe420ff3c770a0fbf2763ed8d88a81))
* **crud:** use search query parameter for CRUD list filtering ([#1130](https://github.com/alltuner/vibetuner/issues/1130)) ([bf9fee5](https://github.com/alltuner/vibetuner/commit/bf9fee5c93a84e9795444ff247bbe0184e24ecbd))
* fall back to pyproject.toml name for CLI help title ([#1136](https://github.com/alltuner/vibetuner/issues/1136)) ([abb2e8e](https://github.com/alltuner/vibetuner/commit/abb2e8e6d77a316bb029e2edccf3880204ec9d59))
* **health:** add asyncio.timeout() to health check operations ([#1084](https://github.com/alltuner/vibetuner/issues/1084)) ([7975209](https://github.com/alltuner/vibetuner/commit/79752094ca4822f46ee995aa90e380bba8d74cc0))
* **health:** reuse existing Redis connections instead of creating new ones per check ([#1093](https://github.com/alltuner/vibetuner/issues/1093)) ([d9e1b46](https://github.com/alltuner/vibetuner/commit/d9e1b46df2486c4ee10bca66f5c5e703c272488c))
* **health:** sanitize error messages in health check responses ([#1100](https://github.com/alltuner/vibetuner/issues/1100)) ([3701139](https://github.com/alltuner/vibetuner/commit/3701139a9d78ad24c93e1d2d493f3a181cf105ca))
* ignore ruff B008 for FastAPI Depends() convention ([#1170](https://github.com/alltuner/vibetuner/issues/1170)) ([469fa7d](https://github.com/alltuner/vibetuner/commit/469fa7d875f5e721dc71e8f5c2aac11c9f15abc6))
* improve doctor command help, template checks, and port labels ([#1191](https://github.com/alltuner/vibetuner/issues/1191)) ([d771f06](https://github.com/alltuner/vibetuner/commit/d771f06b200e1bc996e21609122386b559949c25))
* improve error messages when required services are not configured ([#986](https://github.com/alltuner/vibetuner/issues/986)) ([a8417ba](https://github.com/alltuner/vibetuner/commit/a8417ba56e8806ecb035a6b45a35e46c15c42d2c))
* include dev deps, gitflow recipes, and YAML in scaffold justfiles ([#1192](https://github.com/alltuner/vibetuner/issues/1192)) ([786e849](https://github.com/alltuner/vibetuner/commit/786e849f7e54791438feb34f025c19797ce31256))
* make service error rich panels opt-in to reduce log noise ([#1187](https://github.com/alltuner/vibetuner/issues/1187)) ([2f28d7d](https://github.com/alltuner/vibetuner/commit/2f28d7d9fc3f06ba215cbdc43a9bc4f493355403))
* match streaq Middleware type in robust_retry_middleware ([#1173](https://github.com/alltuner/vibetuner/issues/1173)) ([1f4a629](https://github.com/alltuner/vibetuner/commit/1f4a6292e95a10250c70262e3184097afb402a1d))
* move sse.py out of vibetuner.frontend to avoid circular imports ([#1020](https://github.com/alltuner/vibetuner/issues/1020)) ([f2f0470](https://github.com/alltuner/vibetuner/commit/f2f04704cb15d7273034d051e133b489fcf606f1))
* normalize hyphens to underscores in project name for module imports ([#1021](https://github.com/alltuner/vibetuner/issues/1021)) ([1280f55](https://github.com/alltuner/vibetuner/commit/1280f55ee6c0616450c0dbdacb065abeb139f34b))
* **oauth:** add runtime validation for custom OAuth providers ([#1099](https://github.com/alltuner/vibetuner/issues/1099)) ([9f0a741](https://github.com/alltuner/vibetuner/commit/9f0a7415e93eaf46d72c0c3ecc012dc4ad5d8826))
* remove **kwargs from CRUD list route handler ([#1013](https://github.com/alltuner/vibetuner/issues/1013)) ([3844039](https://github.com/alltuner/vibetuner/commit/38440398e2d99e0027ad8438c9e7e9516382c949))
* remove `from __future__ import annotations` from CRUD factory ([#1012](https://github.com/alltuner/vibetuner/issues/1012)) ([84031a2](https://github.com/alltuner/vibetuner/commit/84031a26cdff29994988db5f043cc3149f13a22d))
* remove all from __future__ import annotations and ban via ruff ([#1024](https://github.com/alltuner/vibetuner/issues/1024)) ([7e4d8d9](https://github.com/alltuner/vibetuner/commit/7e4d8d94e9a6e9bae325e888ab3b75a6a43d1601))
* remove AllTuner-specific localdev URL from run dev output ([#1189](https://github.com/alltuner/vibetuner/issues/1189)) ([b1c18ab](https://github.com/alltuner/vibetuner/commit/b1c18ab9b38f85b2dd4d4dc1525bde1e6d6b7258))
* remove broken debug_claude link from debug nav ([#1017](https://github.com/alltuner/vibetuner/issues/1017)) ([fff01d8](https://github.com/alltuner/vibetuner/commit/fff01d811eda590c34affa254506757080e11327))
* **rendering:** add thread safety for global template context registration ([#1087](https://github.com/alltuner/vibetuner/issues/1087)) ([1b7f85b](https://github.com/alltuner/vibetuner/commit/1b7f85bc98290fd818c3e8751ab58d530f1abc2b))
* **rendering:** improve type safety for context providers ([#1092](https://github.com/alltuner/vibetuner/issues/1092)) ([52a9c1d](https://github.com/alltuner/vibetuner/commit/52a9c1d6920476bf14801441195da5f916a3cfd4))
* replace deprecated typer-slim[standard] with typer ([#1185](https://github.com/alltuner/vibetuner/issues/1185)) ([d434185](https://github.com/alltuner/vibetuner/commit/d434185d2dab0f59a4aabfd6442dd7f9a5dfecf0))
* resolve OAuth user through account link instead of email ([#990](https://github.com/alltuner/vibetuner/issues/990)) ([b071903](https://github.com/alltuner/vibetuner/commit/b0719030220f3eee0da842eb65340d11874b3854))
* **runtime_config:** validate config_value decorated functions take no parameters ([#1090](https://github.com/alltuner/vibetuner/issues/1090)) ([e1e72c5](https://github.com/alltuner/vibetuner/commit/e1e72c532b6a3392e24ee423ee8dc1e637ff3e4c))
* serialize ObjectId as string in CRUD response schemas ([#1171](https://github.com/alltuner/vibetuner/issues/1171)) ([c14150d](https://github.com/alltuner/vibetuner/commit/c14150da169a4fa6b3cda7a41500ead40c6da7ca))
* **services:** add error handling for service config failures in Depends() wrappers ([#1080](https://github.com/alltuner/vibetuner/issues/1080)) ([25f7773](https://github.com/alltuner/vibetuner/commit/25f7773db44dbf7e3a15be2a82adf227dacfac98))
* **services:** fix cache refresh concurrency issue in get_runtime_config() ([#1082](https://github.com/alltuner/vibetuner/issues/1082)) ([8687a50](https://github.com/alltuner/vibetuner/commit/8687a503ced159a9dbdde6f999deede829a91a30))
* **services:** move cache refresh lock into RuntimeConfig class ([#1115](https://github.com/alltuner/vibetuner/issues/1115)) ([4c412cc](https://github.com/alltuner/vibetuner/commit/4c412cc5ffb54f712d8ab2eb55592e101ce4219b))
* skip logging during CLI help commands ([#1172](https://github.com/alltuner/vibetuner/issues/1172)) ([0395077](https://github.com/alltuner/vibetuner/commit/03950775b8932ff3f21f1d44bbb6ee8fce0551c3))
* **sse:** validate Redis pub/sub messages before dispatching ([#1098](https://github.com/alltuner/vibetuner/issues/1098)) ([e826277](https://github.com/alltuner/vibetuner/commit/e8262775d7f0bfcf289d6668143428abf2115160))
* **sse:** warn when endpoint path duplicates router prefix ([#1128](https://github.com/alltuner/vibetuner/issues/1128)) ([7687fc4](https://github.com/alltuner/vibetuner/commit/7687fc4c6fa786fd60993fc131394cff34936a87))
* surface original import errors in load_app_config ([#1186](https://github.com/alltuner/vibetuner/issues/1186)) ([eac0081](https://github.com/alltuner/vibetuner/commit/eac0081fd996ed752761e08ebf1f55b0e0a47dcf))
* **tasks:** add missing exports to tasks/__init__.py ([#1095](https://github.com/alltuner/vibetuner/issues/1095)) ([7e32532](https://github.com/alltuner/vibetuner/commit/7e325320ff587f4a85ad9b7662ef817182642321))
* **tasks:** add threading lock to robust_task middleware registration ([#1088](https://github.com/alltuner/vibetuner/issues/1088)) ([59b87ae](https://github.com/alltuner/vibetuner/commit/59b87aedb60165f68676c42f4a07d67249c12b7d))
* **tasks:** handle empty string in robust_task name resolution ([#1091](https://github.com/alltuner/vibetuner/issues/1091)) ([81a3b6c](https://github.com/alltuner/vibetuner/commit/81a3b6cff08c7847a1bb34e806e8b270cbdd3928))
* use colon notation for streaq worker import path ([#1030](https://github.com/alltuner/vibetuner/issues/1030)) ([2a395f8](https://github.com/alltuner/vibetuner/commit/2a395f83adc73b7fe1eeef2aac016e8e43db2c69))
* use default import for htmx to expose window.htmx ([#1042](https://github.com/alltuner/vibetuner/issues/1042)) ([a98fb27](https://github.com/alltuner/vibetuner/commit/a98fb27ae0933cff6f70f994df682bb9476b2da5))
* wrap JS bundle script tag in overridable block ([#1019](https://github.com/alltuner/vibetuner/issues/1019)) ([446cfd8](https://github.com/alltuner/vibetuner/commit/446cfd808799ac3abd0672fb99c4abb2fe9f640a))


### Code Refactoring

* deduplicate data parsing in scaffold new command ([#1195](https://github.com/alltuner/vibetuner/issues/1195)) ([7d7f70b](https://github.com/alltuner/vibetuner/commit/7d7f70b45c53ded34f5a65daf5a59330bdfec68f))


### Performance Improvements

* cache provider signature checks at registration time ([#1194](https://github.com/alltuner/vibetuner/issues/1194)) ([179c4cc](https://github.com/alltuner/vibetuner/commit/179c4cc5db0efe03db3a3917c815547222bd2ab1))
* **sse:** reuse cached Redis client for broadcast publishing ([#1096](https://github.com/alltuner/vibetuner/issues/1096)) ([c42a73c](https://github.com/alltuner/vibetuner/commit/c42a73ce757919e50afb3c8026579b85cc43cf48))


### Miscellaneous Chores

* update all dependencies to latest versions ([#1198](https://github.com/alltuner/vibetuner/issues/1198)) ([b5a2e87](https://github.com/alltuner/vibetuner/commit/b5a2e87bc1510d5cf6337884ea17731e26d5a761))


### Documentation Updates

* add comprehensive background tasks documentation ([#1044](https://github.com/alltuner/vibetuner/issues/1044)) ([2bc10a1](https://github.com/alltuner/vibetuner/commit/2bc10a18a7b55c000775b37cd409ab2efd29d06b))
* align SECRET_KEY, auth, and CLI reference with implementation ([#1197](https://github.com/alltuner/vibetuner/issues/1197)) ([fff2b43](https://github.com/alltuner/vibetuner/commit/fff2b43bf0215ba8bed33c0e0e6d358219d83fb6))
* comprehensive documentation update for v7.1 features ([#1031](https://github.com/alltuner/vibetuner/issues/1031)) ([0ed8dfe](https://github.com/alltuner/vibetuner/commit/0ed8dfe756cd0b891a6b3292c4273f077cf8c8b4))
* create htmx v2-to-v4 migration guide for downstream projects ([#1094](https://github.com/alltuner/vibetuner/issues/1094)) ([9514aa3](https://github.com/alltuner/vibetuner/commit/9514aa33a960bfaefdb56c536a098049a93f6696))
* document render_template path convention ([#1014](https://github.com/alltuner/vibetuner/issues/1014)) ([b21f532](https://github.com/alltuner/vibetuner/commit/b21f532be7fa2342dc814ae292b5beefba74ee4b))
* document tune.py import ordering requirements ([#1015](https://github.com/alltuner/vibetuner/issues/1015)) ([c2829ef](https://github.com/alltuner/vibetuner/commit/c2829efd2cd999132f10cac074d784382ff0c67e))
* update documentation for recent SQLModel, CRUD, and SSE changes ([#1145](https://github.com/alltuner/vibetuner/issues/1145)) ([bf3f8d2](https://github.com/alltuner/vibetuner/commit/bf3f8d2d10978af8171e4c687479357a46c634df))
* update SSE documentation examples for htmx v4 patterns ([#1089](https://github.com/alltuner/vibetuner/issues/1089)) ([7de9b31](https://github.com/alltuner/vibetuner/commit/7de9b3107df09d150f914eb3bf451d49cf2f09d9))


### Styling Changes

* enforce ruff formatting on vibetuner-py source files ([#1125](https://github.com/alltuner/vibetuner/issues/1125)) ([e267b76](https://github.com/alltuner/vibetuner/commit/e267b7687a1b2d135eab47cd72749229f663ba1c))

## [7.0.1](https://github.com/alltuner/vibetuner/compare/v7.0.0...v7.0.1) (2026-02-11)


### Miscellaneous Chores

* **deps:** bump @alltuner/vibetuner from 6.4.0 to 7.0.0 in /vibetuner-template ([#966](https://github.com/alltuner/vibetuner/issues/966)) ([8efbbb3](https://github.com/alltuner/vibetuner/commit/8efbbb3bcb5d14de233991d98674a336fddcd776))
* **deps:** bump cryptography from 46.0.4 to 46.0.5 ([#971](https://github.com/alltuner/vibetuner/issues/971)) ([88fab70](https://github.com/alltuner/vibetuner/commit/88fab7046ff17a4927b7c826c1ac82baff4ab6e4))
* **deps:** bump cryptography from 46.0.4 to 46.0.5 in /vibetuner-py ([#970](https://github.com/alltuner/vibetuner/issues/970)) ([b485553](https://github.com/alltuner/vibetuner/commit/b4855537b4dba20208d02b1e570373bad577d3ca))
* **deps:** update dependency @alltuner/vibetuner to v7 ([#968](https://github.com/alltuner/vibetuner/issues/968)) ([9998321](https://github.com/alltuner/vibetuner/commit/9998321e608a563df4e68fccd89d15e7bff70040))
* **deps:** update redis docker tag to v8.6 ([#969](https://github.com/alltuner/vibetuner/issues/969)) ([5514103](https://github.com/alltuner/vibetuner/commit/5514103f949715a284812786abb4ec8e9a27436c))

## [7.0.0](https://github.com/alltuner/vibetuner/compare/v6.4.1...v7.0.0) (2026-02-10)


### ⚠ BREAKING CHANGES

* upgrade streaq dependency from v5 to v6 ([#956](https://github.com/alltuner/vibetuner/issues/956))

### Features

* upgrade streaq dependency from v5 to v6 ([#956](https://github.com/alltuner/vibetuner/issues/956)) ([41ec3dd](https://github.com/alltuner/vibetuner/commit/41ec3dd88b9f22dc40e4d12d14d448aa10747771))

## [6.4.1](https://github.com/alltuner/vibetuner/compare/v6.4.0...v6.4.1) (2026-02-10)


### Code Refactoring

* use pydantic-settings for OAuth credentials ([#962](https://github.com/alltuner/vibetuner/issues/962)) ([dabee2a](https://github.com/alltuner/vibetuner/commit/dabee2acd5a05802fbe462c5a2eb55b3a7324c24))

## [6.4.0](https://github.com/alltuner/vibetuner/compare/v6.3.9...v6.4.0) (2026-02-10)


### Features

* auto-register OAuth providers from oauth_providers config ([#959](https://github.com/alltuner/vibetuner/issues/959)) ([81ee179](https://github.com/alltuner/vibetuner/commit/81ee1799c16d428e9092b4d330e29980d79110bb))

## [6.3.9](https://github.com/alltuner/vibetuner/compare/v6.3.8...v6.3.9) (2026-02-10)


### Bug Fixes

* add pyproject.toml to Dockerfile runtime stage and warn on missing config ([#954](https://github.com/alltuner/vibetuner/issues/954)) ([98acee1](https://github.com/alltuner/vibetuner/commit/98acee1fde953126c76f3ab01a686cc3519c24b8))

## [6.3.8](https://github.com/alltuner/vibetuner/compare/v6.3.7...v6.3.8) (2026-02-10)


### Bug Fixes

* lazy-import git in scaffold.py to prevent CLI crash in production ([#952](https://github.com/alltuner/vibetuner/issues/952)) ([ebe4112](https://github.com/alltuner/vibetuner/commit/ebe4112e849ce9268170b1281dc3035d9d854fbb))
* remove --no-sources from Dockerfile deps stage ([#950](https://github.com/alltuner/vibetuner/issues/950)) ([e4f13ea](https://github.com/alltuner/vibetuner/commit/e4f13eaa04fcfdd37eeb4c3c1c75b863a6a81684))
* use --frozen instead of --locked in Dockerfile uv sync ([#947](https://github.com/alltuner/vibetuner/issues/947)) ([f412eb5](https://github.com/alltuner/vibetuner/commit/f412eb57d5b26587567818f2b2c115e18df4cf17))

## [6.3.7](https://github.com/alltuner/vibetuner/compare/v6.3.6...v6.3.7) (2026-02-09)


### Miscellaneous Chores

* bump uv_build ([#943](https://github.com/alltuner/vibetuner/issues/943)) ([2c35591](https://github.com/alltuner/vibetuner/commit/2c3559199468679ac96d63c64b8ecff4689c247e))

## [6.3.6](https://github.com/alltuner/vibetuner/compare/v6.3.5...v6.3.6) (2026-02-09)


### Bug Fixes

* add --frozen to all uv run commands in justfiles ([#941](https://github.com/alltuner/vibetuner/issues/941)) ([fc06a7a](https://github.com/alltuner/vibetuner/commit/fc06a7a17bcb71089973c36eea7149c2833ec3be))

## [6.3.5](https://github.com/alltuner/vibetuner/compare/v6.3.4...v6.3.5) (2026-02-09)


### Bug Fixes

* defer GitPython import to prevent crash when git is unavailable ([#940](https://github.com/alltuner/vibetuner/issues/940)) ([3e8b7e9](https://github.com/alltuner/vibetuner/commit/3e8b7e9b00e461cd223765bc3af1ad310b93a2d6))
* run copier with uvx to prevent pollution of scaffolding ([#938](https://github.com/alltuner/vibetuner/issues/938)) ([c876f76](https://github.com/alltuner/vibetuner/commit/c876f76796c4ea2c2427fa6d69df489e411c0c75))

## [6.3.4](https://github.com/alltuner/vibetuner/compare/v6.3.3...v6.3.4) (2026-02-09)


### Bug Fixes

* releasing should not install deps to avoid polluting the dir ([#936](https://github.com/alltuner/vibetuner/issues/936)) ([fafeead](https://github.com/alltuner/vibetuner/commit/fafeead2aad19ec00511d952cfba668bb2e0ae94))

## [6.3.3](https://github.com/alltuner/vibetuner/compare/v6.3.2...v6.3.3) (2026-02-09)


### Bug Fixes

* move render_template out of frontend package to prevent circular imports ([#935](https://github.com/alltuner/vibetuner/issues/935)) ([7c88d7b](https://github.com/alltuner/vibetuner/commit/7c88d7b483ebbab9734a8b240e9608e45d4bc6fe))
* use dynamic project name for model import in db CLI ([#934](https://github.com/alltuner/vibetuner/issues/934)) ([a506467](https://github.com/alltuner/vibetuner/commit/a50646730142f74b91484f58b6805895ef66a059))


### Documentation Updates

* clarify that app in paths/imports is a placeholder for project slug ([#932](https://github.com/alltuner/vibetuner/issues/932)) ([844ec4c](https://github.com/alltuner/vibetuner/commit/844ec4caa34feb8518fee32207f8220fce2ca190))

## [6.3.2](https://github.com/alltuner/vibetuner/compare/v6.3.1...v6.3.2) (2026-02-09)


### Bug Fixes

* resolve bun dev race condition producing empty bundle.css ([#927](https://github.com/alltuner/vibetuner/issues/927)) ([e5a3933](https://github.com/alltuner/vibetuner/commit/e5a3933ed77b6b773d19150d5756a1730a2c3a62))

## [6.3.1](https://github.com/alltuner/vibetuner/compare/v6.3.0...v6.3.1) (2026-02-09)


### Bug Fixes

* add missing __init__.py to template for uv_build ([#923](https://github.com/alltuner/vibetuner/issues/923)) ([9269bd6](https://github.com/alltuner/vibetuner/commit/9269bd636205d708e67fa08131735ab523ff970d))
* use uv run vibetuner in local dev recipes ([#925](https://github.com/alltuner/vibetuner/issues/925)) ([c8f54e6](https://github.com/alltuner/vibetuner/commit/c8f54e62ccb59a37058679cc10277566a52d4976))

## [6.3.0](https://github.com/alltuner/vibetuner/compare/v6.2.3...v6.3.0) (2026-02-09)


### Features

* auto-install deps and replace concurrently with bun run --parallel ([#920](https://github.com/alltuner/vibetuner/issues/920)) ([cbb7a99](https://github.com/alltuner/vibetuner/commit/cbb7a99d0571e301044ba6fcca6a689a268b899c))

## [6.2.3](https://github.com/alltuner/vibetuner/compare/v6.2.2...v6.2.3) (2026-02-08)


### Bug Fixes

* remove install-deps from local dev commands ([#917](https://github.com/alltuner/vibetuner/issues/917)) ([c01bc73](https://github.com/alltuner/vibetuner/commit/c01bc737223a06e4ddb4055135aef6283de32038))


### Miscellaneous Chores

* ignore local settings ([#919](https://github.com/alltuner/vibetuner/issues/919)) ([38a7267](https://github.com/alltuner/vibetuner/commit/38a7267fe1c994f7eb7de6ef8830213ed27b8747))

## [6.2.2](https://github.com/alltuner/vibetuner/compare/v6.2.1...v6.2.2) (2026-02-08)


### Miscellaneous Chores

* remove .claude, .opencode, .mcp.json, opencode.json, and tmp from template ([#915](https://github.com/alltuner/vibetuner/issues/915)) ([05bc9db](https://github.com/alltuner/vibetuner/commit/05bc9dbdd911ed32be2bfea46d7d24486a022ca7))

## [6.2.1](https://github.com/alltuner/vibetuner/compare/v6.2.0...v6.2.1) (2026-02-08)


### Bug Fixes

* remove --delete-branch from deps-pr gh merge ([fcbd818](https://github.com/alltuner/vibetuner/commit/fcbd81844e5304530c8ce3d431b040bb513da9bb))


### Miscellaneous Chores

* update deps 2026-02-08 ([ca43c81](https://github.com/alltuner/vibetuner/commit/ca43c81325029818ff091a4945186915f3264d40))

## [6.2.0](https://github.com/alltuner/vibetuner/compare/v6.1.5...v6.2.0) (2026-02-06)


### Features

* load parent .env before local .env in configuration ([#910](https://github.com/alltuner/vibetuner/issues/910)) ([2993ae1](https://github.com/alltuner/vibetuner/commit/2993ae1a759a51cbbd6ee40210469d5e33333600))

## [6.1.5](https://github.com/alltuner/vibetuner/compare/v6.1.4...v6.1.5) (2026-02-06)


### Documentation Updates

* clarify uv as sole Python tool in agent instructions ([#908](https://github.com/alltuner/vibetuner/issues/908)) ([fdcdd20](https://github.com/alltuner/vibetuner/commit/fdcdd20f3d931efc29a8da802c1b7aee571fe5db))

## [6.1.4](https://github.com/alltuner/vibetuner/compare/v6.1.3...v6.1.4) (2026-02-06)


### Code Refactoring

* remove mise from project toolchain ([#906](https://github.com/alltuner/vibetuner/issues/906)) ([e0438dd](https://github.com/alltuner/vibetuner/commit/e0438dd4668e702f582ce168978e475f15073267))

## [6.1.3](https://github.com/alltuner/vibetuner/compare/v6.1.2...v6.1.3) (2026-02-06)


### Code Refactoring

* remove custom worktree conventions ([#904](https://github.com/alltuner/vibetuner/issues/904)) ([fd6bfe8](https://github.com/alltuner/vibetuner/commit/fd6bfe822dc6b5346efdd87dc376b849e286dd13))

## [6.1.2](https://github.com/alltuner/vibetuner/compare/v6.1.1...v6.1.2) (2026-02-06)


### Miscellaneous Chores

* **deps:** update dependency uv_build to &gt;=0.10,&lt;0.11 ([#900](https://github.com/alltuner/vibetuner/issues/900)) ([da5845c](https://github.com/alltuner/vibetuner/commit/da5845c6dd35c37ca22957c12248db8feacb7f13))
* **deps:** update ghcr.io/astral-sh/uv docker tag to v0.10 ([#901](https://github.com/alltuner/vibetuner/issues/901)) ([0867450](https://github.com/alltuner/vibetuner/commit/0867450471f216252810b867e1751969b343fd78))
* update deps 2026-02-06 ([41d0715](https://github.com/alltuner/vibetuner/commit/41d07155498715d69998b39805a175627ba8cded))

## [6.1.1](https://github.com/alltuner/vibetuner/compare/v6.1.0...v6.1.1) (2026-02-04)


### Miscellaneous Chores

* **deps:** bump vibetuner from 6.0.2 to 6.1.0 ([#897](https://github.com/alltuner/vibetuner/issues/897)) ([68d789c](https://github.com/alltuner/vibetuner/commit/68d789cd113991583709d367908f6fb75460ba86))


### Documentation Updates

* update documentation and remove claude notification system ([#899](https://github.com/alltuner/vibetuner/issues/899)) ([7ca6ca6](https://github.com/alltuner/vibetuner/commit/7ca6ca6402b8b1d90a7ed4deb063dbeb20ad6bd4))

## [6.1.0](https://github.com/alltuner/vibetuner/compare/v6.0.3...v6.1.0) (2026-02-03)


### Features

* add short format to timeago filter ([#895](https://github.com/alltuner/vibetuner/issues/895)) ([7013131](https://github.com/alltuner/vibetuner/commit/7013131687035e9e2f74d4c87b9dc095cedd1db9))


### Bug Fixes

* ensure Ctrl+C cleanly stops dev server with SSE connections ([#894](https://github.com/alltuner/vibetuner/issues/894)) ([cac0c0c](https://github.com/alltuner/vibetuner/commit/cac0c0cc6930392a76ed7e1081297ea3725d593c))

## [6.0.3](https://github.com/alltuner/vibetuner/compare/v6.0.2...v6.0.3) (2026-02-03)


### Bug Fixes

* resolve circular imports and missing module references ([#885](https://github.com/alltuner/vibetuner/issues/885)) ([d6f7091](https://github.com/alltuner/vibetuner/commit/d6f7091040ba65a09a58816cadad042cb542b579))
* use conventional commit format for deps-pr title ([#890](https://github.com/alltuner/vibetuner/issues/890)) ([0381f53](https://github.com/alltuner/vibetuner/commit/0381f53307d268d1e240853b767a83f31ee5c8ce))


### Miscellaneous Chores

* trigger release workflow ([#888](https://github.com/alltuner/vibetuner/issues/888)) ([d023b7b](https://github.com/alltuner/vibetuner/commit/d023b7b025545e124da0ecdd4e9a05fdd5c32fd2))
* update deps 2026-02-03 ([743e0e0](https://github.com/alltuner/vibetuner/commit/743e0e0cd542e4d1e9e210b2458bcc83e3ece539))

## [6.0.2](https://github.com/alltuner/vibetuner/compare/v6.0.1...v6.0.2) (2026-02-03)


### Bug Fixes

* lazy-load worker lifespan to avoid circular imports ([#881](https://github.com/alltuner/vibetuner/issues/881)) ([807226b](https://github.com/alltuner/vibetuner/commit/807226b73d6f5b89fcf35316168958f449c56a5e))

## [6.0.1](https://github.com/alltuner/vibetuner/compare/v6.0.0...v6.0.1) (2026-02-03)


### Bug Fixes

* lazy-load custom template filters to avoid circular imports ([#877](https://github.com/alltuner/vibetuner/issues/877)) ([013f686](https://github.com/alltuner/vibetuner/commit/013f686d6768eab935742819ae8e0f80c9238897))


### Miscellaneous Chores

* **deps:** update dependency @alltuner/vibetuner to v6 ([#879](https://github.com/alltuner/vibetuner/issues/879)) ([6dd7ec8](https://github.com/alltuner/vibetuner/commit/6dd7ec84cb17d150d3fce46142f17bd493e836e5))

## [6.0.0](https://github.com/alltuner/vibetuner/compare/v5.0.3...v6.0.0) (2026-02-03)


### ⚠ BREAKING CHANGES

* replace magic imports with explicit tune.py configuration ([#873](https://github.com/alltuner/vibetuner/issues/873))

### Features

* replace magic imports with explicit tune.py configuration ([#873](https://github.com/alltuner/vibetuner/issues/873)) ([9bea69c](https://github.com/alltuner/vibetuner/commit/9bea69c22535a1b789bb34518cbf31549c40392d))

## [5.0.3](https://github.com/alltuner/vibetuner/compare/v5.0.2...v5.0.3) (2026-02-01)


### Bug Fixes

* fix loader of routes ([#871](https://github.com/alltuner/vibetuner/issues/871)) ([4c84d63](https://github.com/alltuner/vibetuner/commit/4c84d635043a163889aa6c71385af4d827a6fc46))

## [5.0.2](https://github.com/alltuner/vibetuner/compare/v5.0.1...v5.0.2) (2026-02-01)


### Bug Fixes

* make frontend lifespan optional ([#867](https://github.com/alltuner/vibetuner/issues/867)) ([7ca776a](https://github.com/alltuner/vibetuner/commit/7ca776ab202b401625d56806a45ccfcaf3d04fd5))


### Miscellaneous Chores

* update deps ([#870](https://github.com/alltuner/vibetuner/issues/870)) ([d68d881](https://github.com/alltuner/vibetuner/commit/d68d881f32944b17367e411ff7f768204a758b49))
* update deps 2026-02-01 ([ad45423](https://github.com/alltuner/vibetuner/commit/ad45423936eaa53b2367d34b4b983e1c2972aae8))

## [5.0.1](https://github.com/alltuner/vibetuner/compare/v5.0.0...v5.0.1) (2026-02-01)


### Bug Fixes

* use latest uv build backend ([#865](https://github.com/alltuner/vibetuner/issues/865)) ([4943de8](https://github.com/alltuner/vibetuner/commit/4943de8ee0a1a0e5bc36deed1f6a00739614d432))


### Miscellaneous Chores

* **deps:** update dependency @alltuner/vibetuner to v5 ([#864](https://github.com/alltuner/vibetuner/issues/864)) ([935e311](https://github.com/alltuner/vibetuner/commit/935e311d49f52a0eda1b0f8bc8843b96e3ac0e1e))

## [5.0.0](https://github.com/alltuner/vibetuner/compare/v4.0.1...v5.0.0) (2026-02-01)


### ⚠ BREAKING CHANGES

* simplify versioning - read from pyproject.toml instead of git tags ([#858](https://github.com/alltuner/vibetuner/issues/858))

### Features

* add vibetuner scaffold adopt command ([#862](https://github.com/alltuner/vibetuner/issues/862)) ([1ab4103](https://github.com/alltuner/vibetuner/commit/1ab4103cc95ea041d65a905dad2d1f22c175f9a4))
* simplify versioning - read from pyproject.toml instead of git tags ([#858](https://github.com/alltuner/vibetuner/issues/858)) ([34e12b2](https://github.com/alltuner/vibetuner/commit/34e12b2ce3bcf96077936addc8af8d895965780c))


### Bug Fixes

* cache git branch lookup in versioning module ([#860](https://github.com/alltuner/vibetuner/issues/860)) ([9ac832b](https://github.com/alltuner/vibetuner/commit/9ac832bd06051826378dba63786b9addfab21b4b))
* remove worktree placeholder ([#863](https://github.com/alltuner/vibetuner/issues/863)) ([cff196c](https://github.com/alltuner/vibetuner/commit/cff196c7653d2d1b82c5591930c08bbfb06880d3))


### Code Refactoring

* move worktrees to sibling directory with readable names ([#861](https://github.com/alltuner/vibetuner/issues/861)) ([79c28c9](https://github.com/alltuner/vibetuner/commit/79c28c940071de17c4766c013772c88da003b332))

## [4.0.1](https://github.com/alltuner/vibetuner/compare/v4.0.0...v4.0.1) (2026-02-01)


### Bug Fixes

* require vibetuner&gt;=4.0.0 in scaffolded projects ([#855](https://github.com/alltuner/vibetuner/issues/855)) ([4186839](https://github.com/alltuner/vibetuner/commit/41868390b1f31a4d5bea878978e22ffb694133ae))


### Miscellaneous Chores

* **deps:** update dependency @alltuner/vibetuner to v4 ([#857](https://github.com/alltuner/vibetuner/issues/857)) ([325cb46](https://github.com/alltuner/vibetuner/commit/325cb4662a399356c762923d0502da7bb5d8ded5))

## [4.0.0](https://github.com/alltuner/vibetuner/compare/v3.5.0...v4.0.0) (2026-02-01)


### ⚠ BREAKING CHANGES

* self-sufficient vibetuner - no more scaffolding boilerplate ([#853](https://github.com/alltuner/vibetuner/issues/853))

### Features

* self-sufficient vibetuner - no more scaffolding boilerplate ([#853](https://github.com/alltuner/vibetuner/issues/853)) ([8747a5e](https://github.com/alltuner/vibetuner/commit/8747a5ea6c134bb9bdda3260c2edaeb1c67ed899))

## [3.5.0](https://github.com/alltuner/vibetuner/compare/v3.4.3...v3.5.0) (2026-01-29)


### Features

* add locale detection configuration via environment variables ([#850](https://github.com/alltuner/vibetuner/issues/850)) ([f6b15dc](https://github.com/alltuner/vibetuner/commit/f6b15dcbae6422d87eb88d3e68c8d679783771ff))


### Miscellaneous Chores

* update deps 2026-01-28 ([557ccee](https://github.com/alltuner/vibetuner/commit/557cceeb0ed452d25110929a2cae955f78609b36))
* update deps 2026-01-29 ([6616dd1](https://github.com/alltuner/vibetuner/commit/6616dd1835bf14d42d10ed876aebb50c1a4c9fe4))

## [3.4.3](https://github.com/alltuner/vibetuner/compare/v3.4.2...v3.4.3) (2026-01-28)


### Bug Fixes

* update default python to 3.14 ([#845](https://github.com/alltuner/vibetuner/issues/845)) ([e5209b8](https://github.com/alltuner/vibetuner/commit/e5209b80d6e6c2134c41fe0d17fc0a565b321266))


### Miscellaneous Chores

* **deps:** bump rumdl from 0.1.1 to 0.1.2 in /vibetuner-py ([#843](https://github.com/alltuner/vibetuner/issues/843)) ([e93f47c](https://github.com/alltuner/vibetuner/commit/e93f47ccd9f9369cae2157cee8d9e61a1c46e157))
* **deps:** bump vibetuner from 3.4.1 to 3.4.2 ([#844](https://github.com/alltuner/vibetuner/issues/844)) ([c651914](https://github.com/alltuner/vibetuner/commit/c651914b1fda1850a947a67b03a121faff6af4ce))

## [3.4.2](https://github.com/alltuner/vibetuner/compare/v3.4.1...v3.4.2) (2026-01-27)


### Bug Fixes

* bootstrap without requiring just or mise installed ([#840](https://github.com/alltuner/vibetuner/issues/840)) ([b9e0d94](https://github.com/alltuner/vibetuner/commit/b9e0d946b17e04eab97677e0b2792a99153fcf30))


### Miscellaneous Chores

* update deps 2026-01-27 ([b6d34c8](https://github.com/alltuner/vibetuner/commit/b6d34c81d1d5070d505e6fbb74b4a7d57dd81a4b))

## [3.4.1](https://github.com/alltuner/vibetuner/compare/v3.4.0...v3.4.1) (2026-01-27)


### Miscellaneous Chores

* update deps 2026-01-27 ([b74901d](https://github.com/alltuner/vibetuner/commit/b74901da84c02c46c389ef4dc8b406a6bbe52a0f))

## [3.4.0](https://github.com/alltuner/vibetuner/compare/v3.3.0...v3.4.0) (2026-01-26)


### Features

* add Claude Code notification system ([#835](https://github.com/alltuner/vibetuner/issues/835)) ([828686f](https://github.com/alltuner/vibetuner/commit/828686f5aa48ef267e671eeaad34720e62131d70))

## [3.3.0](https://github.com/alltuner/vibetuner/compare/v3.2.1...v3.3.0) (2026-01-26)


### Features

* expose compute_auto_port function with optional path parameter ([#826](https://github.com/alltuner/vibetuner/issues/826)) ([789480a](https://github.com/alltuner/vibetuner/commit/789480a9ce10715be13af12406afe6054f737ed9))
* skip Claude Code trust prompt in worktrees via sparse checkout ([#830](https://github.com/alltuner/vibetuner/issues/830)) ([810499e](https://github.com/alltuner/vibetuner/commit/810499ee1d041d81efea6bea2fc8d851f26e7b14))


### Miscellaneous Chores

* update deps 2026-01-26 ([5d184ab](https://github.com/alltuner/vibetuner/commit/5d184ab9a4b96e4e6574b66eed30ef286a598dbe))


### Documentation Updates

* fix README project structure and command names ([#828](https://github.com/alltuner/vibetuner/issues/828)) ([0892936](https://github.com/alltuner/vibetuner/commit/08929365853a900feaa787cafada2a44a98a94d6))

## [3.2.1](https://github.com/alltuner/vibetuner/compare/v3.2.0...v3.2.1) (2026-01-26)


### Bug Fixes

* remove DEBUG and ENVIRONMENT from template .env ([#823](https://github.com/alltuner/vibetuner/issues/823)) ([4c9341f](https://github.com/alltuner/vibetuner/commit/4c9341f49f8bee4427df2770a4b4a11e4c195c12))

## [3.2.0](https://github.com/alltuner/vibetuner/compare/v3.1.1...v3.2.0) (2026-01-24)


### Features

* add /static/fonts route for custom font support ([#821](https://github.com/alltuner/vibetuner/issues/821)) ([75708b2](https://github.com/alltuner/vibetuner/commit/75708b26ae94ecfc703aa9b76f1b5bd12c182792))

## [3.1.1](https://github.com/alltuner/vibetuner/compare/v3.1.0...v3.1.1) (2026-01-22)


### Bug Fixes

* use conventional commit title in deps-pr squash merge ([#819](https://github.com/alltuner/vibetuner/issues/819)) ([d92e723](https://github.com/alltuner/vibetuner/commit/d92e7230733df743e9495d42b3fb6f492273829c))


### Documentation Updates

* update docs to reflect vibetuner as installed package ([#816](https://github.com/alltuner/vibetuner/issues/816)) ([1aa22ec](https://github.com/alltuner/vibetuner/commit/1aa22ece31986d607520d2355d8e7e378da4ddec))

## [3.1.0](https://github.com/alltuner/vibetuner/compare/v3.0.2...v3.1.0) (2026-01-21)


### Features

* add default_language question to copier scaffold ([#812](https://github.com/alltuner/vibetuner/issues/812)) ([ec8ca99](https://github.com/alltuner/vibetuner/commit/ec8ca995d373e3fcd6f06a439b107bfea396de04))


### Miscellaneous Chores

* update dependencies ([#814](https://github.com/alltuner/vibetuner/issues/814)) ([1ae65b2](https://github.com/alltuner/vibetuner/commit/1ae65b219f8186f800954d7bfdfee8e7489962b3))

## [3.0.2](https://github.com/alltuner/vibetuner/compare/v3.0.1...v3.0.2) (2026-01-21)


### Miscellaneous Chores

* **deps:** update dependency @alltuner/vibetuner to v3 ([#810](https://github.com/alltuner/vibetuner/issues/810)) ([b26065a](https://github.com/alltuner/vibetuner/commit/b26065a636aefeaf7967934af3014218d53f70a4))

## [3.0.1](https://github.com/alltuner/vibetuner/compare/v3.0.0...v3.0.1) (2026-01-21)


### Bug Fixes

* missing parameter in the locale middleware ([#808](https://github.com/alltuner/vibetuner/issues/808)) ([ffd5911](https://github.com/alltuner/vibetuner/commit/ffd5911b432c730565d509aa29dc92e53f7a614b))

## [3.0.0](https://github.com/alltuner/vibetuner/compare/v2.53.3...v3.0.0) (2026-01-21)


### ⚠ BREAKING CHANGES

* improve multi-language support with clearer SEO semantics ([#804](https://github.com/alltuner/vibetuner/issues/804))

### Features

* improve multi-language support with clearer SEO semantics ([#804](https://github.com/alltuner/vibetuner/issues/804)) ([4402f3c](https://github.com/alltuner/vibetuner/commit/4402f3cb5231e1fe86a59874b7aff6351a4a520b))


### Miscellaneous Chores

* update dependencies ([#806](https://github.com/alltuner/vibetuner/issues/806)) ([8f542ca](https://github.com/alltuner/vibetuner/commit/8f542cab6afb54976139db6cf6f25a1aa424224a))

## [2.53.3](https://github.com/alltuner/vibetuner/compare/v2.53.2...v2.53.3) (2026-01-21)


### Miscellaneous Chores

* **deps:** bump vibetuner from 2.53.1 to 2.53.2 ([#801](https://github.com/alltuner/vibetuner/issues/801)) ([b700a5b](https://github.com/alltuner/vibetuner/commit/b700a5bf0eaddd2eabf6302afb1a0f5da76f0be3))

## [2.53.2](https://github.com/alltuner/vibetuner/compare/v2.53.1...v2.53.2) (2026-01-20)


### Bug Fixes

* use correct SessionMiddleware parameter for secure cookies ([#798](https://github.com/alltuner/vibetuner/issues/798)) ([70bcb78](https://github.com/alltuner/vibetuner/commit/70bcb78e37faea4359a55f9e1c4f52ee87ccce67))


### Miscellaneous Chores

* update dependencies ([#800](https://github.com/alltuner/vibetuner/issues/800)) ([311945c](https://github.com/alltuner/vibetuner/commit/311945cd6706b8cf515b173d47298cef2e57c74d))

## [2.53.1](https://github.com/alltuner/vibetuner/compare/v2.53.0...v2.53.1) (2026-01-20)


### Bug Fixes

* mark session cookie as Secure in production ([#795](https://github.com/alltuner/vibetuner/issues/795)) ([78e63ab](https://github.com/alltuner/vibetuner/commit/78e63ab2d6215a77fc4090341a68bdc588edc0da))

## [2.53.0](https://github.com/alltuner/vibetuner/compare/v2.52.1...v2.53.0) (2026-01-20)


### Features

* add language to automatic template context ([#793](https://github.com/alltuner/vibetuner/issues/793)) ([2696751](https://github.com/alltuner/vibetuner/commit/2696751d21c6cd80f193fcc5e2eb501fad86e901))

## [2.52.1](https://github.com/alltuner/vibetuner/compare/v2.52.0...v2.52.1) (2026-01-20)


### Bug Fixes

* allow claude to use playwright more easily ([#790](https://github.com/alltuner/vibetuner/issues/790)) ([72b3c66](https://github.com/alltuner/vibetuner/commit/72b3c66199ecebd2f1fcc83e9cd6fdd75c79b11f))

## [2.52.0](https://github.com/alltuner/vibetuner/compare/v2.51.0...v2.52.0) (2026-01-20)


### Features

* add named email address support to EmailService ([#788](https://github.com/alltuner/vibetuner/issues/788)) ([b7eb84b](https://github.com/alltuner/vibetuner/commit/b7eb84bdd5c86b3245b9daf338e1d780e464fb2d))


### Bug Fixes

* make claude plugins behave a bit more nicely ([#786](https://github.com/alltuner/vibetuner/issues/786)) ([93bce3a](https://github.com/alltuner/vibetuner/commit/93bce3a7e6137a7b84fce158c04645bbaa20c812))


### Miscellaneous Chores

* update dependencies ([#789](https://github.com/alltuner/vibetuner/issues/789)) ([396ce71](https://github.com/alltuner/vibetuner/commit/396ce711876be6681e15bd6db8b9e5040981ec2b))

## [2.51.0](https://github.com/alltuner/vibetuner/compare/v2.50.1...v2.51.0) (2026-01-20)


### Features

* add traceability params to EmailService for Mailjet ([#782](https://github.com/alltuner/vibetuner/issues/782)) ([09ffd84](https://github.com/alltuner/vibetuner/commit/09ffd84c5a4ca1a234028655017ab2f58d9a8c7c))


### Miscellaneous Chores

* update dependencies ([#784](https://github.com/alltuner/vibetuner/issues/784)) ([802eef4](https://github.com/alltuner/vibetuner/commit/802eef43a7868b7b02f2c46a79b0f09077982496))

## [2.50.1](https://github.com/alltuner/vibetuner/compare/v2.50.0...v2.50.1) (2026-01-19)


### Miscellaneous Chores

* update dependencies ([#780](https://github.com/alltuner/vibetuner/issues/780)) ([f470958](https://github.com/alltuner/vibetuner/commit/f4709580f673d3ce25eea3f0dc9583b07af55d5b))

## [2.50.0](https://github.com/alltuner/vibetuner/compare/v2.49.0...v2.50.0) (2026-01-19)


### Features

* replace SES email service with Mailjet ([#778](https://github.com/alltuner/vibetuner/issues/778)) ([af00e58](https://github.com/alltuner/vibetuner/commit/af00e58b0135a4cb39536160e52b193d17f9de57))

## [2.49.0](https://github.com/alltuner/vibetuner/compare/v2.48.0...v2.49.0) (2026-01-19)


### Features

* add lint-po linter for Gettext translation files ([#776](https://github.com/alltuner/vibetuner/issues/776)) ([df6df39](https://github.com/alltuner/vibetuner/commit/df6df39c3f895ad626819292872d416b0dc1a48a))
* expose locale_names to template context ([#774](https://github.com/alltuner/vibetuner/issues/774)) ([9a42c3b](https://github.com/alltuner/vibetuner/commit/9a42c3ba664901c45de6d1f6f720f9c1a0f8e2d4))


### Miscellaneous Chores

* update dependencies ([#777](https://github.com/alltuner/vibetuner/issues/777)) ([91af7a3](https://github.com/alltuner/vibetuner/commit/91af7a3a96ce84558ce8e1994b33e5621dee10dd))

## [2.48.0](https://github.com/alltuner/vibetuner/compare/v2.47.4...v2.48.0) (2026-01-19)


### Features

* add path-prefix language routing for SEO-friendly URLs ([#770](https://github.com/alltuner/vibetuner/issues/770)) ([30544a4](https://github.com/alltuner/vibetuner/commit/30544a4ec7c412ce1d648b44111e73dfc7ccfe8f))

## [2.47.4](https://github.com/alltuner/vibetuner/compare/v2.47.3...v2.47.4) (2026-01-18)


### Bug Fixes

* resolve Dependabot alert and add configuration ([#765](https://github.com/alltuner/vibetuner/issues/765)) ([9506210](https://github.com/alltuner/vibetuner/commit/9506210918019f4d05b96356a0d85bd7aedec4fe))


### Miscellaneous Chores

* linting and claude config ([#767](https://github.com/alltuner/vibetuner/issues/767)) ([49c87ec](https://github.com/alltuner/vibetuner/commit/49c87ec3d90b87a8a4121bb19f9f7bea8ddc2347))

## [2.47.3](https://github.com/alltuner/vibetuner/compare/v2.47.2...v2.47.3) (2026-01-16)


### Bug Fixes

* dependabot is really in a bad shape, replacing completely with r… ([#762](https://github.com/alltuner/vibetuner/issues/762)) ([c16ff61](https://github.com/alltuner/vibetuner/commit/c16ff616717d17111220611b206642823220db75))

## [2.47.2](https://github.com/alltuner/vibetuner/compare/v2.47.1...v2.47.2) (2026-01-16)


### Miscellaneous Chores

* update claude review templates to latest version ([#759](https://github.com/alltuner/vibetuner/issues/759)) ([e2d4d26](https://github.com/alltuner/vibetuner/commit/e2d4d26941d5bd0d0a52236e081a934541e1c68c))

## [2.47.1](https://github.com/alltuner/vibetuner/compare/v2.47.0...v2.47.1) (2026-01-14)


### Bug Fixes

* use builtin prek hooks instead of pre-commit hooks ([#755](https://github.com/alltuner/vibetuner/issues/755)) ([7c5aad2](https://github.com/alltuner/vibetuner/commit/7c5aad2ef1c6eb049dfb52932c08a50013b24cd4))


### Miscellaneous Chores

* update dependencies ([#758](https://github.com/alltuner/vibetuner/issues/758)) ([e5920d7](https://github.com/alltuner/vibetuner/commit/e5920d76884ebc99728222a21da84d0bb4be5e9a))
* update pre-commit hooks ([#757](https://github.com/alltuner/vibetuner/issues/757)) ([16b804f](https://github.com/alltuner/vibetuner/commit/16b804fc97bcab8ac96bfe24c0415007041d6263))

## [2.47.0](https://github.com/alltuner/vibetuner/compare/v2.46.5...v2.47.0) (2026-01-13)


### Features

* add plugins to claude repo context ([#750](https://github.com/alltuner/vibetuner/issues/750)) ([f275b93](https://github.com/alltuner/vibetuner/commit/f275b93da73a4a4258aba67e4d69b745d620d9e0))


### Miscellaneous Chores

* bump copier from 9.11.0 to 9.11.1 in /vibetuner-py ([#747](https://github.com/alltuner/vibetuner/issues/747)) ([4475dbd](https://github.com/alltuner/vibetuner/commit/4475dbd13ad62634bf9ddd8a5c3beba9adb09dba))
* update dependencies ([#754](https://github.com/alltuner/vibetuner/issues/754)) ([a2df1c4](https://github.com/alltuner/vibetuner/commit/a2df1c41809faa3d1b93eed4f69ed979d4896226))

## [2.46.5](https://github.com/alltuner/vibetuner/compare/v2.46.4...v2.46.5) (2026-01-09)


### Miscellaneous Chores

* allow code to close issues and show commits ([#744](https://github.com/alltuner/vibetuner/issues/744)) ([4800743](https://github.com/alltuner/vibetuner/commit/4800743db79c2face3a01f8a01e4a97dd8b1767f))

## [2.46.4](https://github.com/alltuner/vibetuner/compare/v2.46.3...v2.46.4) (2026-01-09)


### Miscellaneous Chores

* improve claude settings ([#740](https://github.com/alltuner/vibetuner/issues/740)) ([24bfa74](https://github.com/alltuner/vibetuner/commit/24bfa7496a185d81aa50278823ad456269edb57c))

## [2.46.3](https://github.com/alltuner/vibetuner/compare/v2.46.2...v2.46.3) (2026-01-09)


### Miscellaneous Chores

* update dependencies and enable playwright ([#738](https://github.com/alltuner/vibetuner/issues/738)) ([e86548b](https://github.com/alltuner/vibetuner/commit/e86548bf112362faf850d1bcefbbf3f0d5ad051a))

## [2.46.2](https://github.com/alltuner/vibetuner/compare/v2.46.1...v2.46.2) (2026-01-08)


### Miscellaneous Chores

* update tool ecosystem to favor mise ([#736](https://github.com/alltuner/vibetuner/issues/736)) ([ae3a069](https://github.com/alltuner/vibetuner/commit/ae3a0692c9b516dfe53899d78782e09c2ff5514e))

## [2.46.1](https://github.com/alltuner/vibetuner/compare/v2.46.0...v2.46.1) (2026-01-08)


### Documentation Updates

* add worktree management documentation ([#734](https://github.com/alltuner/vibetuner/issues/734)) ([0a0dfa2](https://github.com/alltuner/vibetuner/commit/0a0dfa218b0789c0acb11b3fdb2a785dc0362102))

## [2.46.0](https://github.com/alltuner/vibetuner/compare/v2.45.0...v2.46.0) (2026-01-08)


### Features

* add feature-rebase command to sync worktree with main ([#731](https://github.com/alltuner/vibetuner/issues/731)) ([75833ca](https://github.com/alltuner/vibetuner/commit/75833ca8dcf03a34055c09d170aba4c6a4c758ac))
* creates new action to update dependencies and scaffolding for scaffolded projects ([#729](https://github.com/alltuner/vibetuner/issues/729)) ([423c037](https://github.com/alltuner/vibetuner/commit/423c0375925f9685c067c8df708ca23b7b956ddf))
* improve feature-done and feature-drop with flexible input ([#732](https://github.com/alltuner/vibetuner/issues/732)) ([5a48354](https://github.com/alltuner/vibetuner/commit/5a48354d1ec3326183af5f8e2c71b12fb4aebe36))


### Bug Fixes

* cd to main worktree before deleting branch in feature-done/drop ([#733](https://github.com/alltuner/vibetuner/issues/733)) ([c2b98bf](https://github.com/alltuner/vibetuner/commit/c2b98bf21da8fcfac4b2ed367172c885882103f1))


### Miscellaneous Chores

* **main:** release 2.45.0 ([#728](https://github.com/alltuner/vibetuner/issues/728)) ([b95acf0](https://github.com/alltuner/vibetuner/commit/b95acf0202378c23a6e896f33a346b580db8bda5))

## [2.45.0](https://github.com/alltuner/vibetuner/compare/v2.44.2...v2.45.0) (2026-01-08)


### Features

* add worktrees directory placeholder to template ([#724](https://github.com/alltuner/vibetuner/issues/724)) ([495562b](https://github.com/alltuner/vibetuner/commit/495562b6b4540690279d05dcf1171c65bed11d57))
* allow parallel development using worktrees ([#727](https://github.com/alltuner/vibetuner/issues/727)) ([df32b1a](https://github.com/alltuner/vibetuner/commit/df32b1afbe6961450764e0d480dba2dfcd57a939))

## [2.44.2](https://github.com/alltuner/vibetuner/compare/v2.44.1...v2.44.2) (2026-01-07)


### Bug Fixes

* move to the latest prek version ([#722](https://github.com/alltuner/vibetuner/issues/722)) ([fc9f6a1](https://github.com/alltuner/vibetuner/commit/fc9f6a1b9d1de8e107f358f34fe2637c5412a6b2))

## [2.44.1](https://github.com/alltuner/vibetuner/compare/v2.44.0...v2.44.1) (2026-01-07)


### Bug Fixes

* add copy-core-templates stub for backwards compatibility ([#719](https://github.com/alltuner/vibetuner/issues/719)) ([70cc5e0](https://github.com/alltuner/vibetuner/commit/70cc5e029abc7d2f3d3f5ff04f64af8d863fba1b))


### Miscellaneous Chores

* update dependencies ([#721](https://github.com/alltuner/vibetuner/issues/721)) ([0fe2db4](https://github.com/alltuner/vibetuner/commit/0fe2db4ebe3f18ea0c3637b2767617327f59fd1f))

## [2.44.0](https://github.com/alltuner/vibetuner/compare/v2.43.0...v2.44.0) (2026-01-07)


### Features

* add deps-pr command for automated dependency updates ([#714](https://github.com/alltuner/vibetuner/issues/714)) ([4e45d08](https://github.com/alltuner/vibetuner/commit/4e45d0818a4989a8c8fb0dbeefb8bc248436ef92))


### Bug Fixes

* pin prek to 0.2.25 (0.2.26 missing arm64 wheel) ([#716](https://github.com/alltuner/vibetuner/issues/716)) ([51c762a](https://github.com/alltuner/vibetuner/commit/51c762a71d79d8a9a5a3666afa6dbf367606095c))


### Miscellaneous Chores

* update dependencies ([#717](https://github.com/alltuner/vibetuner/issues/717)) ([0e6e4bf](https://github.com/alltuner/vibetuner/commit/0e6e4bfe9cfc4e42ca1d9d1ebbda6a3066135617))

## [2.43.0](https://github.com/alltuner/vibetuner/compare/v2.42.1...v2.43.0) (2026-01-07)


### Features

* improve worktree management with hash-based directories ([#712](https://github.com/alltuner/vibetuner/issues/712)) ([11c7522](https://github.com/alltuner/vibetuner/commit/11c752202f67aab8ab350d4dab84b7dc5252c6af))

## [2.42.1](https://github.com/alltuner/vibetuner/compare/v2.42.0...v2.42.1) (2026-01-07)


### Bug Fixes

* run mise trust in new worktrees ([#710](https://github.com/alltuner/vibetuner/issues/710)) ([6ff0b1e](https://github.com/alltuner/vibetuner/commit/6ff0b1ebfa289f0d241d910337f498517d3a3555))

## [2.42.0](https://github.com/alltuner/vibetuner/compare/v2.41.0...v2.42.0) (2026-01-07)


### Features

* add auto-port selection for local development ([#705](https://github.com/alltuner/vibetuner/issues/705)) ([3aeea30](https://github.com/alltuner/vibetuner/commit/3aeea3080349aba4930336bdef3d8dac8d52b0b5))
* add git worktree support for feature development ([#707](https://github.com/alltuner/vibetuner/issues/707)) ([c68f77f](https://github.com/alltuner/vibetuner/commit/c68f77fd3b12bad93ae3b63cd8b402a588091248))
* add local-all command for simplified local development ([#709](https://github.com/alltuner/vibetuner/issues/709)) ([cc763d6](https://github.com/alltuner/vibetuner/commit/cc763d6b5b45e02d5e0d5c4c167361607c1f18a1))

## [2.41.0](https://github.com/alltuner/vibetuner/compare/v2.40.0...v2.41.0) (2026-01-07)


### Features

* include playwriter mcp ([#703](https://github.com/alltuner/vibetuner/issues/703)) ([0fe01f8](https://github.com/alltuner/vibetuner/commit/0fe01f8d361b0eca31286e5d57312418d1aafbe3))

## [2.40.0](https://github.com/alltuner/vibetuner/compare/v2.39.2...v2.40.0) (2026-01-07)


### Features

* dynamic vibetuner templates for Tailwind CSS scanning ([#700](https://github.com/alltuner/vibetuner/issues/700)) ([e902e4a](https://github.com/alltuner/vibetuner/commit/e902e4a25709a9d2e966b41af60b8669e8b10cc4))


### Bug Fixes

* remove daisyui properties workaround ([#702](https://github.com/alltuner/vibetuner/issues/702)) ([678e8d0](https://github.com/alltuner/vibetuner/commit/678e8d02b91d87046cc65fef8a6e04057e1741c3))

## [2.39.2](https://github.com/alltuner/vibetuner/compare/v2.39.1...v2.39.2) (2026-01-04)


### Miscellaneous Chores

* update dependencies ([#697](https://github.com/alltuner/vibetuner/issues/697)) ([025ae8c](https://github.com/alltuner/vibetuner/commit/025ae8c9b67c3f36d799808c477c237d70a993c4))

## [2.39.1](https://github.com/alltuner/vibetuner/compare/v2.39.0...v2.39.1) (2025-12-21)


### Miscellaneous Chores

* update deps and pre-commit ([#689](https://github.com/alltuner/vibetuner/issues/689)) ([b8ab284](https://github.com/alltuner/vibetuner/commit/b8ab284ee26a5357a65e8e2b614aa37926c5bd46))

## [2.39.0](https://github.com/alltuner/vibetuner/compare/v2.38.0...v2.39.0) (2025-12-17)


### Features

* add default dependabot.yml to template with bun ecosystem ([#685](https://github.com/alltuner/vibetuner/issues/685)) ([dc6d64a](https://github.com/alltuner/vibetuner/commit/dc6d64af47889367e871eb9d3d06ed7e70314ba8))
* enhance renovate config and add documentation domains to template ([#687](https://github.com/alltuner/vibetuner/issues/687)) ([13b8f02](https://github.com/alltuner/vibetuner/commit/13b8f02e15a2601c99f618cd5e300da788abd432))

## [2.38.0](https://github.com/alltuner/vibetuner/compare/v2.37.0...v2.38.0) (2025-12-17)


### Features

* **templates:** add render_template_string helper for SSE responses ([#683](https://github.com/alltuner/vibetuner/issues/683)) ([064609e](https://github.com/alltuner/vibetuner/commit/064609e95d4519e1d9116ca8e77b1cb3e3c77527))


### Documentation Updates

* **template:** add Tailwind CSS best practices to scaffold guide ([#680](https://github.com/alltuner/vibetuner/issues/680)) ([90906c4](https://github.com/alltuner/vibetuner/commit/90906c4c7fb01d004b65439c9225d3ee00495d04)), closes [#645](https://github.com/alltuner/vibetuner/issues/645)
* **template:** fix task registration instructions to prevent circular imports ([#682](https://github.com/alltuner/vibetuner/issues/682)) ([c87eab8](https://github.com/alltuner/vibetuner/commit/c87eab82e4bbd0718c38b4e89392b2b7cbf1121d)), closes [#611](https://github.com/alltuner/vibetuner/issues/611)

## [2.37.0](https://github.com/alltuner/vibetuner/compare/v2.36.8...v2.37.0) (2025-12-16)


### Features

* add support for X-Forwarded-For headers via Granian proxy wrapper ([#679](https://github.com/alltuner/vibetuner/issues/679)) ([2619336](https://github.com/alltuner/vibetuner/commit/26193369603db818deed9370e1d206c242809e7a))


### Miscellaneous Chores

* bump @tailwindcss/cli from 4.1.17 to 4.1.18 in /vibetuner-js ([#668](https://github.com/alltuner/vibetuner/issues/668)) ([878b15a](https://github.com/alltuner/vibetuner/commit/878b15a4de342e61e890557dc47b3ffd40769172))
* bump actions/download-artifact from 6 to 7 ([#665](https://github.com/alltuner/vibetuner/issues/665)) ([e4327a0](https://github.com/alltuner/vibetuner/commit/e4327a0ca1f0ba6e4a889bd12942a8a4aaa9cef6))
* bump actions/upload-artifact from 5 to 6 ([#666](https://github.com/alltuner/vibetuner/issues/666)) ([d6622d1](https://github.com/alltuner/vibetuner/commit/d6622d1519463156017408614f8815f823f37bfc))
* bump daisyui from 5.5.11 to 5.5.14 in /vibetuner-js ([#669](https://github.com/alltuner/vibetuner/issues/669)) ([28a5f96](https://github.com/alltuner/vibetuner/commit/28a5f960570f3e1078fea203a222a592129b711c))
* bump prek from 0.2.21 to 0.2.22 in /vibetuner-py ([#674](https://github.com/alltuner/vibetuner/issues/674)) ([0cf42c6](https://github.com/alltuner/vibetuner/commit/0cf42c6d0db3c42233433a3f372d2e01bdda143d))
* bump ruff from 0.14.8 to 0.14.9 in /vibetuner-py ([#670](https://github.com/alltuner/vibetuner/issues/670)) ([d8d2e15](https://github.com/alltuner/vibetuner/commit/d8d2e157f5b146136c0b1b88758175047d9417d9))
* bump tailwindcss from 4.1.17 to 4.1.18 in /vibetuner-js ([#671](https://github.com/alltuner/vibetuner/issues/671)) ([f5618bb](https://github.com/alltuner/vibetuner/commit/f5618bbb88ac1a2f81b791582836a74602409758))
* bump ty from 0.0.1a33 to 0.0.1a34 in /vibetuner-py ([#672](https://github.com/alltuner/vibetuner/issues/672)) ([4d0b258](https://github.com/alltuner/vibetuner/commit/4d0b2583615d232c9572b1718c18bea2a72d70f4))
* bump types-authlib from 1.6.5.20251005 to 1.6.6.20251214 in /vibetuner-py ([#667](https://github.com/alltuner/vibetuner/issues/667)) ([8c08bd5](https://github.com/alltuner/vibetuner/commit/8c08bd561911ad6df87f5a8ee3cc87fbd6a0d855))
* bump uv-bump from 0.3.2 to 0.4.0 in /vibetuner-py ([#673](https://github.com/alltuner/vibetuner/issues/673)) ([2b5f838](https://github.com/alltuner/vibetuner/commit/2b5f838e42be4206116e53537a1310de3439ebca))
* **deps:** update github artifact actions (major) ([#664](https://github.com/alltuner/vibetuner/issues/664)) ([1aa893f](https://github.com/alltuner/vibetuner/commit/1aa893fb92adbb84badc0eb8ea7077b1838b1b55))
* update pre-commit and deps ([#677](https://github.com/alltuner/vibetuner/issues/677)) ([da63233](https://github.com/alltuner/vibetuner/commit/da6323327e0074937e7d6133c6d19fc7a5b99475))


### Documentation Updates

* **template:** prevent circular imports in task registration ([#678](https://github.com/alltuner/vibetuner/issues/678)) ([f602b0e](https://github.com/alltuner/vibetuner/commit/f602b0e1f68c6fa3c0822831b9b812099781f530))

## [2.36.8](https://github.com/alltuner/vibetuner/compare/v2.36.7...v2.36.8) (2025-12-10)


### Bug Fixes

* make deployments reliable cacheable and robust ([#662](https://github.com/alltuner/vibetuner/issues/662)) ([bbf23a6](https://github.com/alltuner/vibetuner/commit/bbf23a6ecb98206076984e29da71f7309578a411))


### Miscellaneous Chores

* bump pytest from 9.0.1 to 9.0.2 in /vibetuner-py ([#661](https://github.com/alltuner/vibetuner/issues/661)) ([31ff5e0](https://github.com/alltuner/vibetuner/commit/31ff5e059d9ac089cf6652fbc43d6cad212c24fc))
* bump ruff from 0.14.7 to 0.14.8 in /vibetuner-py ([#659](https://github.com/alltuner/vibetuner/issues/659)) ([53f098b](https://github.com/alltuner/vibetuner/commit/53f098b7758b411a2a85ee09d7ec29929fa7c2bf))

## [2.36.7](https://github.com/alltuner/vibetuner/compare/v2.36.6...v2.36.7) (2025-12-02)


### Bug Fixes

* await mongo_client.close() in teardown_mongodb ([#648](https://github.com/alltuner/vibetuner/issues/648)) ([6b69692](https://github.com/alltuner/vibetuner/commit/6b696927c943380af9d454e7f71472f14c9bf596))


### Miscellaneous Chores

* **template:** add frontend-design skill to permissions whitelist ([#643](https://github.com/alltuner/vibetuner/issues/643)) ([41334fb](https://github.com/alltuner/vibetuner/commit/41334fbdcce7fc293c1579543ed84e61826577d9))


### Documentation Updates

* improve CLI and model documentation ([#651](https://github.com/alltuner/vibetuner/issues/651)) ([2f608a7](https://github.com/alltuner/vibetuner/commit/2f608a73d08842eea910222c479360cabc9961ff))

## [2.36.6](https://github.com/alltuner/vibetuner/compare/v2.36.5...v2.36.6) (2025-12-02)


### Miscellaneous Chores

* remove direct sniffio dependency ([#641](https://github.com/alltuner/vibetuner/issues/641)) ([b8a402c](https://github.com/alltuner/vibetuner/commit/b8a402c9953cc9225ff3caac3fc3500093716796))

## [2.36.5](https://github.com/alltuner/vibetuner/compare/v2.36.4...v2.36.5) (2025-12-02)


### Bug Fixes

* include core-templates in initial scaffold commit ([#639](https://github.com/alltuner/vibetuner/issues/639)) ([6480fac](https://github.com/alltuner/vibetuner/commit/6480facc2eefd6dfe300b6fc55a87af3906e4ee3))

## [2.36.4](https://github.com/alltuner/vibetuner/compare/v2.36.3...v2.36.4) (2025-12-02)


### Miscellaneous Chores

* comment out optional MONGODB_URL and REDIS_URL in template ([#637](https://github.com/alltuner/vibetuner/issues/637)) ([8341398](https://github.com/alltuner/vibetuner/commit/8341398037df8e2df0ed8a8c4f7b9055e25f80c9))

## [2.36.3](https://github.com/alltuner/vibetuner/compare/v2.36.2...v2.36.3) (2025-12-02)


### Code Refactoring

* symlink pre-commit config and remove --no-sources from dev commands ([#636](https://github.com/alltuner/vibetuner/issues/636)) ([e809191](https://github.com/alltuner/vibetuner/commit/e8091919b1e8d6b88787312b73de8479991c8426))


### Miscellaneous Chores

* remove unused enable_job_queue and update LLM docs ([#634](https://github.com/alltuner/vibetuner/issues/634)) ([ac2682b](https://github.com/alltuner/vibetuner/commit/ac2682bb395bb15760043cef2f0307a21174e218))

## [2.36.2](https://github.com/alltuner/vibetuner/compare/v2.36.1...v2.36.2) (2025-12-02)


### Bug Fixes

* allow CLI to run outside project directory ([#632](https://github.com/alltuner/vibetuner/issues/632)) ([863cf45](https://github.com/alltuner/vibetuner/commit/863cf45c024c8edcdffac063c28d1de8a715926d))

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
