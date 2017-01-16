# Advanced MAME Launcher metadata and artwork data model #

AML metadata/assets model is as much compatible with [Advanced Emulator Launcher] as much as possible.

[Advanced Emulator Launcher]: http://github.com/Wintermute0110/plugin.program.advanced.emulator.launcher/


## MAME machine metadata labels ##

 Metadata name | AML name  | setInfo label | Type                 |
---------------|-----------|---------------|----------------------|
 Title         |           | title         | string               |
 Year          |           | year          | string               |
 Genre         |           | genre         | string               |
 Manufacturer  |           | studio        | string               |
 Rating        |           | rating        | string range 0 to 10 |
               |           | overlay       | int range 0 to 8     |

## MAME machine asset labels ##

 Asset name | setArt label | setInfo label |
------------|--------------|---------------|
 Title      | title/icon   |               |
 Snap       | snap/fanart  |               |
 Marquee    | banner       |               |
 Clearlogo  | clearlogo    |               |
 Cabinet    | boxfront     |               |
 CPanel     | boxback      |               |
 PCB        | cartridge    |               |
 Flyer      | poster       |               |
 Trailer    |              | trailer       |


### MAME metadata availability ###

 Metadata name | Metadata source      |
---------------|----------------------|
 Title         | MAME XML description |
 Year          | MAME XML             |
 Genre         | Catver.ini           |
 Studio        | MAME XML             |
 Plot          |                      |
 Driver        | MAME XML             |
 Status        | MAME XML             |
 Controls      |                      |
 Players       |                      |
 Coins         |                      |
 Orientation   |                      |


### Software Lists Metadata availability ###

Same as Console ROMs Metadata.

 Metada source | Title | Year | Genre | Studio | Plot | Platform |
---------------|-------|------|-------|--------|------|----------|
Software Lists |  YES  |  YES | YES   |  YES   | YES  |   YES    |

 * Platform is the MAME machine that runs the Software List ROMs.


## MAME machine asset availability ##

 Artwork site     | Title | Snap  | Preview | Boss | End | GameOver | HowTo | Logo | Scores | Select |
------------------|-------|-------|---------|------|-----|----------|-------|------|--------|--------|
[Pleasuredome]    |  YES  | YES   | YES     | YES  | YES |    YES   |  YES  | YES  |  YES   |  YES   |
[ProgrrettoSNAPS] |  YES  | YES   | YES     | YES  | YES |    YES   |  YES  | YES  |  YES   |  YES   |


 Artwork site     | Versus | Cabinet | CPanel | Flyer  | Icon | Marquee | PCB | Manual | Trailer |
------------------|--------|---------|--------|--------|------|---------|-----|--------|---------|
[Pleasuredome]    |  YES   |  YES    |  YES   |  YES   | YES  |   YES   | YES |  YES   |  YES    |
[ProgrrettoSNAPS] |  YES   |  YES    |  YES   |  YES   | YES  |   YES   | YES |  YES   |  YES    |


## Software Lists asset availability ##

 Artwork site     |  Title | Snap | Fanart | Banner | Boxfront | Boxback  | Manual | Trailer | 
------------------|--------|------|--------|--------|----------|----------|--------|---------|
[Pleasuredome]    |  YES   | YES  | NO     | NO     |   YES    |   NO     |  YES   | YES     |
[ProgrrettoSNAPS] |  YES   | YES  | NO     | NO     |   YES    |   NO     |  YES   | YES     |

 * Many consoles/computers have the same artwork as arcade. For MAME, both arcade and consoles/computers are
   just "machines". For example, CPanel of MegaDrive is the SEGA 3 button joystick.

[Pleasuredome]: http://www.pleasuredome.org.uk/
[ProgrrettoSNAPS]: http://www.progettosnaps.net
