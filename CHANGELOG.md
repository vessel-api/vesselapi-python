# Changelog

All notable changes to this package are documented here.
This project follows [Semantic Versioning](https://semver.org/).

## [2.1.0] - 2026-10-26

### Added

- `VesselPositionResponse` has three new fields, which the API returns on every
  position response since 25 October 2026: `vessel` (a `Vessel`, as from
  `vessels.get()`), `vessel_eta` (a `VesselETA`, as from `vessels.eta()`) and
  `position_check` (the new `PositionCheck` model). `vessel` and `vessel_eta`
  are `None` when the API holds no record for them. Earlier versions drop these
  keys when parsing.
- `PositionCheck` compares the position with the vessel's previous report from
  the last 80 hours (`previous_position`, the new `PreviousPosition` model). It
  gives the time and great-circle distance since then, and the speed and course
  that would cover that distance. It also says whether that speed is more than
  1.2 times the vessel's usual top speed, and whether the MMSI and IMO match.
- `vessels.position()` takes `filter_sat_lookback_minutes` and
  `filter_sat_max_age_minutes`, which set the satellite fallback's time windows.
  Both the sync and async clients have them.

### Changed

- The bundled OpenAPI spec is synced with the API.

## [2.0.1] - 2026-10-08

Documentation only. No method, parameter or model changed.

### Fixed

- The bundled OpenAPI spec named the satellite fallback parameter `sat`; the
  API's parameter is `filter.sat`. Descriptions corrected.

### Changed

- README: the satellite fallback note says when it fires (no recent terrestrial
  position stored); the radius example describes the time window it searches
  (default 2 hours, at most 4).

## [2.0.0] - 2026-08-16

Vessel ownership, classification and inspection data, and NAVTEX messages, were
retired from the VesselAPI service on **10 August 2026**. This release removes
the corresponding client surface and brings the SDK back in line with the API.

Every change below applies to both the sync and async clients.

### Removed (breaking)

These endpoints no longer exist. Calling them returned HTTP 410 from 10 August
2026 onward; the methods are now gone so the failure surfaces at import or call
time rather than as a runtime error.

| Removed | Replacement |
|---|---|
| `vessels.classification()` | none |
| `vessels.inspections()` | none |
| `vessels.inspection_detail()` | none |
| `vessels.ownership()` | none |
| `client.navtex` (whole service: `list()`, `list_all()`) | none |

Also removed:

- **Search filters** `filter_class_society` and `filter_owner` on
  `search.vessels()`. The API began rejecting both with HTTP 400, so any call
  passing them was already failing.
- **Vessel fields** `builder`, `class_society`, `owner_name`, `manager_name`.
- **Models** for the removed endpoints (26 classes), plus the four
  backwards-compatibility aliases `Classification`, `Inspection`,
  `InspectionDetail` and `Ownership`: 30 public names in total.

**Migrating from 1.x:** remove calls to the methods above. There is no
alternative source for that data through this API. Drop `filter_class_society`
and `filter_owner` from any search call. If you read `owner_name`,
`manager_name`, `builder` or `class_society` from a vessel, those attributes are
gone.

### Added

- **Search**: `q` (free-text across name, IMO, MMSI, ENI and callsign) and
  `filter_eni` on `search.vessels()`.
- **Repeatable filters.** `filter_flag` and `filter_vessel_type` on
  `search.vessels()`, and `filter_country`, `filter_port_type`, `filter_size`,
  `filter_harbor_size` and `filter_harbor_use` on `search.ports()`, now accept
  `str | list[str]` (exported as `MultiFilter`). A list matches any of the
  values. Passing a plain string behaves exactly as before.
- **`filter_sat`** on `vessels.position()`. ⚠️ Satellite lookups draw on a
  prepaid balance and are charged per call. Omit it to serve stored positions.
- **`time_from` / `time_to`** on `port_events.by_port()`, `by_ports()`,
  `by_vessels()` and their iterators.
- **Vessel fields**: `eni`, `teu`, `vessel_subtype`, `name_ais`,
  `summer_draught`, `draught_calculated_avg`, `draught_observed_max`,
  `speed_calculated_avg`, `speed_observed_max`. All are declared by the API and
  were previously discarded by the models. Each is optional, and how often one
  is populated varies by field and by vessel.
- **Search metadata**: `FindVesselsResponse.meta` (`matched_on`, `query`) via
  the new `VesselSearchMeta` model, and `ResolutionMeta.suggested_id_type`, a
  hint to retry with the other identifier type when a lookup misses.
- **Error handling**: `VesselPaymentRequiredError` (402, satellite credits
  exhausted) and `VesselForbiddenError` (403, key suspended or feature not on
  your plan), plus `is_payment_required` / `is_forbidden` properties. All errors
  now expose the API's machine-readable `code` and `error_type`. Branch on
  those rather than on `message`, which may be reworded.

### Changed (breaking)

- **Parameters the API requires are now required in Python too.** They are
  keyword-only with no default, so omitting one raises `TypeError` at the call
  instead of returning HTTP 400 from the server. Previously they defaulted to
  `None`, which type-checked cleanly and then failed at runtime.
  - `location.*_bounding_box()`: `lat_min`, `lat_max`, `lon_min`, `lon_max`.
  - `location.*_radius()`: `latitude`, `longitude`, `radius`.
  - `search.dgps()`, `search.light_aids()`, `search.modus()`,
    `search.radio_beacons()`: `filter_name`.
  - `port_events.by_ports()`: `filter_port_name`.
    `port_events.by_vessels()`: `filter_vessel_name`.
  - `vessels.positions()`: `filter_ids`.
  - The matching `all_*` iterators enforce the same set. 38 methods in total,
    on both the sync and async clients.
- **`vessels.positions()` parameter order changed.** `filter_ids` now precedes
  `filter_id_type`. Both are keyword-only, so callers are unaffected.
- `search.vessels()` and `search.ports()` are unaffected: the API marks their
  `filter_name` optional, and it stays optional here.
- `filter_id_type` is unchanged. The API requires it, but the SDK sends it on
  every call and it keeps its `"imo"` default.
- **Iterator signatures are now explicit.** 50 of the `all_*` / `*_all`
  iterators accepted `**kwargs` and forwarded blindly. They now declare exactly
  the parameters they support, so mistyped keywords raise `TypeError` instead of
  being silently ignored, and type checkers and editors can see them. This one
  is breaking only in a narrow case:
  - Anyone passing valid keyword arguments is unaffected.
  - Passing `pagination_next_token` to an iterator is now rejected at the call.
    It was already broken: the iterator supplies that token itself, so it
    raised `got multiple values for keyword argument` at first iteration.

**Migrating from 1.x:** any call that relied on the server rejecting a missing
bound or name now fails at the call site instead. Supply the values listed above.

### Fixed

- **`vessels.all_positions()` could not be time-bounded.** It did not accept
  `time_from` / `time_to` at all, although `positions()` supported them, so
  auto-paginating a historical window was impossible without hand-rolling the
  token loop.
- **`ports.inbound()` and `ports.inbound_all()` required an ETA window** they
  should not have. `eta_from` and `eta_to` were mandatory since 1.2.0, although
  the service treats both as optional and defaults them to now and 72 hours
  ahead. Both are now optional.
- The User-Agent reported `1.1.0` regardless of the installed version.
- Source distributions previously included files beyond the package itself. The
  sdist is now scoped to the library, README, licence and metadata.

### Attribution

Emissions and casualty data: © European Union. Source: European Maritime Safety
Agency (EMSA), THETIS-MRV (EU MRV, Regulation (EU) 2015/757) and the European
Marine Casualty Information Platform (EMCIP). See the README.
