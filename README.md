# Exquis Dev Mode Polytouch Patch
Patch for Exquis firmware 3.0 which enables pressure/pitchbend/polytouch data even when in Developer Mode.

Developer Mode on the [Exquis](https://dualo.com/en/exquis-an-optimized-keyboard/) enables fine control of key LED colors by an application. But this mode removes any polytouch data, resulting in every pad sending **only** `velocity=0` (`NoteOff`) or `velocity=127` (`NoteOn`) messages. Pressure/polytouch thus is unavailable to the application.

This limitation is detrimental to applications that wish to set the colors of the Exquis keyboard while the user is playing it - tutorial applications, theory applications, performance apps with scale highlighting, color indication of scrolling octaves, and so on.

This repository contains:

- a Python script that patches the [3.0 Exquis firmware](https://dualo.com/en/welcome/) .bin file to eliminate the gate which blocks pressure information. You may need to find the file - on macOS, for example, it is located in Exquis_Fw_Updater.app/Contents/Resources/H723ZETx.bin
- the patched .bin, for convenience

This comes with no warranty, although flashing the Exquis device in this way is extremely safe. I also do not guarantee that it will work for any version of the firmware other than 3.0.

I have asked the team to modify this behavior, so hopefully a future release will remove the need for this patch.
