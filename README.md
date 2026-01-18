# Exquis Dev Mode Polytouch Patch
Patch for Exquis firmware 3.0 which enables pressure/pitchbend/polytouch data even when in Developer Mode.

Developer Mode on the [Exquis](https://dualo.com/en/exquis-an-optimized-keyboard/) enables fine control of key LED colors by an application. But this mode removes any polytouch data, resulting in every pad sending **only** `velocity=0` (`NoteOff`) or `velocity=127` (`NoteOn`) messages. Pressure/polytouch thus is unavailable to the application.

This limitation is detrimental to applications that wish to set the colors of the Exquis keyboard while the user is playing it - tutorial applications, theory applications, performance apps with scale highlighting, color indication of scrolling octaves, and so on.

## Repo Contents

This repository contains:

- a Python script that patches the [3.0 Exquis firmware](https://dualo.com/en/welcome/) .bin file to eliminate the gate which blocks pressure information. You may need to find the file - on macOS, for example, it is located in Exquis_Fw_Updater.app/Contents/Resources/H723ZETx.bin
- the patched .bin, for convenience

Note that you will still receive the default `velocity=127` `NoteOn` as well.

## Explanation

In Exquis firmware, **Developer / Slave Mode is not “Normal Mode + SysEx”**. It switches the engine into an alternate control regime that deliberately masks expressive computation and emission. A single engine-wide flag (internally a mode bit) is set when DevMode is active; that bit is checked in multiple places across the engine. When it’s set, the engine still scans buttons and sends basic NoteOn/NoteOff, but it **short-circuits every path that would make a pad “expressive”**: pads are prevented from becoming (or staying) active, pressure and pitchbend computations early-out, and CC74 / aftertouch emitters are suppressed. The result is exactly what users see: velocity-127 notes only, no X/Y/Z data, even though sensors are physically working.

The **core patch** does one thing, very precisely: it neutralizes those DevMode expression gates, without touching hardware drivers, SysEx handling, or the normal performance engine. With the gates removed, DevMode still behaves like DevMode (host mapping, LEDs, SysEx control), but the normal engine pad pipeline is allowed to run. Pads can activate, sensor-derived values are computed, and the existing MPE emitters produce Pitch Bend, Channel/Poly Aftertouch, and CC74 exactly as they do in normal mode.

#### Simplified flow (before vs after)

**Before (DevMode):**

```
Sensors → (OK)
Engine tick →
  pad_try_activate → BLOCKED (DevMode flag)
  pressure / PB compute → BLOCKED
  MPE emit (PB / AT / CC74) → BLOCKED
↓
Only NoteOn/NoteOff via Dev scan
```

**After (patched DevMode):**

```
Sensors → (OK)
Engine tick →
  pad_try_activate → ALLOWED
  pressure / PB compute → RUNS
  MPE emit (PB / AT / CC74) → RUNS
↓
Dev SysEx + LEDs + full expressive MIDI
```

## No Warranty or Guarantee

This comes with no warranty, although flashing the Exquis device in this way is extremely safe. I also do not guarantee that it will work for any version of the firmware other than 3.0.

I have asked the team to modify this behavior, so hopefully a future release will remove the need for this patch.
