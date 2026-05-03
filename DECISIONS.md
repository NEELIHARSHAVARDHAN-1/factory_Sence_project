1. Data Model and Schema

I kept the data model very simple because the problem is focused on recent readings and alert state.

I used two tables:

Telemetry
stores every reading (device_id, timestamp, temperature_c, vibration_g)
DeviceState
stores current state of each device (alert_type, alert_active, last_seen)

Reasoning:

I didnot try to compute alerts directly from raw data every time because that becomes inefficient and mixing all at once.
Instead, I separated:
history (Telemetry)
current state (DeviceState)

This made it easier to:

check last few readings
avoid duplicate alerts
handle silent detection

SQLite is used because it’s required in the spec and enough for this scale.

2. Alert State Machine (and Deduplication)

Main idea:
Send alert only when state changes

I track:

NONE then TEMP / VIB / SILENT then NONE

Logic:

Check last N readings (3 for temp, 5 for vibration)
Determine new alert (TEMP, VIB, or NONE)
Compare with current state
if new_alert == state.alert_type:
    return

So:

If device is already in alert then do nothing
If it changes then send message

This avoids spamming on every reading.

For resolved:

When alert goes back to normal then send one "RESOLVED"

This directly follows the requirement:

send exactly one alert and one resolved message

3. Silent Failure Detection

This was handled separately using a background worker.

Approach:

Every time telemetry comes then update last_seen
Background thread runs every ~30 seconds
For each device:
if current_time - last_seen > 120 sec → silent alert

Important decision:

Silent alert should not override TEMP/VIB alerts

So I only trigger silent when:

if device.alert_type == "NONE":

This avoids conflicting alerts.

When data comes again:

detect that device is no longer silent
send "SILENT RESOLVED"
4. Sensor Simulator Design

I created a Python script to simulate 3 devices.

device_1 and device_2 then normal data only
device_3 then cycles through:
TEMP alert
normal (resolve)
VIB alert
normal (resolve)
silent period (>2 minutes)

I used a simple cycle counter instead of randomness so that:

all alert conditions are guaranteed to trigger
easier to demonstrate in video
5. Scaling to 1000 Devices

Current design works for small scale but needs changes for larger systems.

What I would change:

Replace SQLite with PostgreSQL / TimescaleDB
Add indexing on device_id and timestamp
Move background worker to a proper job system
Batch processing instead of checking each device individually
Possibly use streaming (Kafka) for ingestion

Also:

API rate limiting
better logging and monitoring
6. Tradeoffs (48-hour constraint)

Because of time:

Used SQLite instead of production DB
Simple background thread instead of distributed worker
No authentication or multi-user system
Minimal error handling (focused on core logic)

Main focus was:

correctness of alert logic
clean separation of responsibilities
ensuring no duplicate alerts
7. Final Thoughts

I focused on getting the alert logic correct and reliable, since that is the core of the problem.

The most tricky part was:

avoiding duplicate alerts
handling silent detection without conflicting with other alerts

Once that was stable, everything else became straightforward.
