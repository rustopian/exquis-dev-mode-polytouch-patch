# Exquis Dev Mode Polytouch Patch
Patch for Exquis firmware 3.0 which enables pressure/pitchbend/polytouch data even when in Developer Mode.

Developer Mode on the [Exquis]([url](https://dualo.com/en/exquis-an-optimized-keyboard/) enables fine control of key LED colors by an application, but this mode removes any polytouch data, resulting in every pad sending on `velocity=0` (`NoteOff`) or `velocity=127` (`NoteOn`) messages. This is detrimental to applications that wish to set the colors of the Exquis keyboard while the user is playing it - tutorial applications, theory applications, performance apps with scale highlighting, color indication of scrolling octaves, and so on.

This python script patches the [3.0 Exquis firmware]([url](https://dualo.com/en/welcome/) .bin file to eliminate the gate which blocks pressure information. You may need to find the file - on macOS, for example, it is located in Exquis_Fw_Updater.app/Contents/Resources/H723ZETx.bin.

This comes with no warranty, although flashing the Exquis device in this way is extremely safe. I have asked the team to modify this behavior, so hopefully the next release will remove the need for this patch.
