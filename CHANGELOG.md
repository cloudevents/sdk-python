# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added `.get` accessor for even properties ([#165])
- Added type information for all event member functions ([#173])

### Fixed
-  Fixed event `__eq__` operator raising `AttributeError` on non-CloudEvent values ([#172])

### Changed
- Code quality and styling tooling is unified and configs compatibility is ensured ([#167])
- CI configurations updated and added macOS and Windows tests ([#169])
- Copyright is unified with the other SDKs and updated/added where needed. ([#170])

### Removed
- `docs` folder and related unused tooling ([#168])


## [1.3.0] — 2022-09-07
### Added
- Python 3.9 support ([#144])
- Python 3.10 support ([#150])
- Automatic CLO checks ([#158], [#159], [#160])

### Fixed
- `ce-datacontenttype` is not longer generated for binary representation ([#138])
- Fixed typings issues ([#149])
- The package redistributive ability by inlining required `pypi-packaging.py` functions ([#151])

## [1.2.0] — 2020-08-20
### Added
- Added GenericException, DataMarshallingError and DataUnmarshallingError ([#120])

## [1.1.0] — 2020-08-18
### Changed
- Changed from_http to now expect headers argument before data ([#110])
- Renamed exception names ([#111])

### Fixed
- Fixed from_http bugs with data of type None, or not dict-like ([#119])

### Deprecated
- Renamed to_binary_http and to_structured_http. ([#108])

## [1.0.1] — 2020-08-14
### Added
- CloudEvent exceptions and event type checking in http module ([#96])
- CloudEvent equality override ([#98])

## [1.0.0] — 2020-08-11
### Added
- Update types and handle data_base64 structured ([#34])
- Added a user friendly CloudEvent class with data validation ([#36])
- CloudEvent structured cloudevent support ([#47])
- Separated http methods into cloudevents.http module ([#60])
- Implemented to_json and from_json in http module ([#72])

### Fixed
- Fixed top level extensions bug ([#71])

### Removed
- Removed support for Cloudevents V0.2 and V0.1 ([#43])

## [0.3.0] — 2020-07-11
### Added
- Added Cloudevents V0.3 and V1 implementations ([#22])
- Add helpful text to README ([#23])
- Add link to email in README ([#27])

### Fixed
- Fix small bug with extensions ([#25])

## [0.2.4] - 2019-06-07
### Fixed
- Fix typo in extensions ([#21])

## [0.2.3] - 2019-04-20
### Changed
- Update sample scripts ([#15])

### Fixed
- Move Sphinx dependency out of package depedency ([#17])

## [0.2.2] - 2019-01-16
### Added
- Adding web app tests ([#13])

### Fixed
- Add content-type for long-description. ([#11])

## [0.2.1] - 2019-01-16
### Changed
- Consolidating return types ([#7])
- Updates for binary encoding ([#9])
- 0.2 force improvements ([#10])

## [0.2.0] - 2018-12-08
### Changed
- Make SDK compliant wtih CloudEvents SDK spec ([#2])

## [0.0.1] - 2018-11-19
### Added
- Initial release

[1.3.0]: https://github.com/cloudevents/sdk-python/compare/1.2.0...1.3.0
[1.2.0]: https://github.com/cloudevents/sdk-python/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/cloudevents/sdk-python/compare/1.0.1...1.1.0
[1.0.1]: https://github.com/cloudevents/sdk-python/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/cloudevents/sdk-python/compare/0.3.0...1.0.0
[0.3.0]: https://github.com/cloudevents/sdk-python/compare/0.2.4...0.3.0
[0.2.4]: https://github.com/cloudevents/sdk-python/compare/0.2.3...0.2.4
[0.2.3]: https://github.com/cloudevents/sdk-python/compare/0.2.2...0.2.3
[0.2.2]: https://github.com/cloudevents/sdk-python/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/cloudevents/sdk-python/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/cloudevents/sdk-python/compare/0.0.1...0.2.0
[0.0.1]: https://github.com/cloudevents/sdk-python/releases/tag/0.0.1

[#2]: https://github.com/cloudevents/sdk-python/pull/2
[#7]: https://github.com/cloudevents/sdk-python/pull/7
[#9]: https://github.com/cloudevents/sdk-python/pull/9
[#10]: https://github.com/cloudevents/sdk-python/pull/10
[#11]: https://github.com/cloudevents/sdk-python/pull/11
[#13]: https://github.com/cloudevents/sdk-python/pull/13
[#15]: https://github.com/cloudevents/sdk-python/pull/15
[#17]: https://github.com/cloudevents/sdk-python/pull/17
[#21]: https://github.com/cloudevents/sdk-python/pull/21
[#22]: https://github.com/cloudevents/sdk-python/pull/22
[#23]: https://github.com/cloudevents/sdk-python/pull/23
[#25]: https://github.com/cloudevents/sdk-python/pull/25
[#27]: https://github.com/cloudevents/sdk-python/pull/27
[#34]: https://github.com/cloudevents/sdk-python/pull/34
[#36]: https://github.com/cloudevents/sdk-python/pull/36
[#43]: https://github.com/cloudevents/sdk-python/pull/43
[#47]: https://github.com/cloudevents/sdk-python/pull/47
[#60]: https://github.com/cloudevents/sdk-python/pull/60
[#71]: https://github.com/cloudevents/sdk-python/pull/71
[#72]: https://github.com/cloudevents/sdk-python/pull/72
[#96]: https://github.com/cloudevents/sdk-python/pull/96
[#98]: https://github.com/cloudevents/sdk-python/pull/98
[#108]: https://github.com/cloudevents/sdk-python/pull/108
[#110]: https://github.com/cloudevents/sdk-python/pull/110
[#111]: https://github.com/cloudevents/sdk-python/pull/111
[#119]: https://github.com/cloudevents/sdk-python/pull/119
[#120]: https://github.com/cloudevents/sdk-python/pull/120
[#144]: https://github.com/cloudevents/sdk-python/pull/144
[#149]: https://github.com/cloudevents/sdk-python/pull/149
[#150]: https://github.com/cloudevents/sdk-python/pull/150
[#151]: https://github.com/cloudevents/sdk-python/pull/151
[#158]: https://github.com/cloudevents/sdk-python/pull/158
[#159]: https://github.com/cloudevents/sdk-python/pull/159
[#160]: https://github.com/cloudevents/sdk-python/pull/160
[#165]: https://github.com/cloudevents/sdk-python/pull/165
[#167]: https://github.com/cloudevents/sdk-python/pull/167
[#168]: https://github.com/cloudevents/sdk-python/pull/168
[#169]: https://github.com/cloudevents/sdk-python/pull/169
[#170]: https://github.com/cloudevents/sdk-python/pull/170
[#172]: https://github.com/cloudevents/sdk-python/pull/172
[#173]: https://github.com/cloudevents/sdk-python/pull/173
