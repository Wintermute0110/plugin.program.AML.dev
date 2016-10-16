# Advanced MAME Launcher metadata and artwork data model #

## MAME machine metadata labels ##

 Metadata name | AEL name | setInfo label | Type                 |
---------------|----------|---------------|----------------------|
 Title         | m_name   | Title         | string               |
 Year          |
 Genre         |
 Studio        |
 Plot          |
 Driver        |
 Status        |
 Control       |
 Players       |
 Coins         |
 Orientation   |

 
## MAME machine asset labels ##

 Asset name | AEL name  | setArt label | setInfo label |
------------|-----------|--------------|---------------|
            |           | icon         |               |
 Title      |
 Snap       |
 Preview    |
 Boss       |
 End        |
 GameOver   |
 HowTo      |
 Logo       |
 Scores     |
 Select     |
 Versus     |
 Cabinet    |
 CPanel     |
 Flyer      |
 Icon       |
 Marquee    |
 PCB        |
 Manual     |
 Trailer    |


### MAME metadata availability ###

 Metada source | Title | Year | Genre | Studio | Plot | Driver | Status | Control | Players | Coins | Orientation | 
---------------|-------|------|-------|--------|------|--------|--------|---------|---------|-------|-------------|
 MAME XML      |
 Catver.ini    |
 NPlayers.ini  |
 History.dat   |

 * This metadata list for AML is still provisional.


### Software Lists Metadata availability ###

Same as Console ROMs Metadata.

 Metada source | Title | Year | Genre | Studio | Plot | Platform |
---------------|-------|------|-------|--------|------|----------|
Software Lists |  YES  |  YES | YES   |  YES   | YES  |   YES    |

 * Platform is the MAME machine that runs the Software List ROMs.


## MAME machine asset availability ##

 Artwork site     | Title | Snap  | Preview | Boss | End | GameOver | HowTo | Logo | Scores | Select | Versus | Cabinet | CPanel | Flyer  | Icon | Marquee | PCB | Manual | Trailer |
------------------|-------|-------|---------|------|-----|----------|-------|------|--------|--------|--------|---------|--------|--------|------|---------|-----|--------|---------|
[Pleasuredome]    |  YES  | YES   | YES     | YES  | YES |    YES   |  YES  | YES  |  YES   |  YES   |  YES   |  YES    |  YES   |  YES   | YES  |   YES   | YES |  YES   |  YES    |
[ProgrrettoSNAPS] |  YES  | YES   | YES     | YES  | YES |    YES   |  YES  | YES  |  YES   |  YES   |  YES   |  YES    |  YES   |  YES   | YES  |   YES   | YES |  YES   |  YES    |
 

## Software Lists asset availability ##

 Artwork site     |  Title | Snap | Fanart | Banner | Boxfront | Boxback  | Manual | Trailer | 
------------------|--------|------|--------|--------|----------|----------|--------|---------|
[Pleasuredome]    |  YES   | YES  | NO     | NO     |   YES    |   NO     |  YES   | YES     |
[ProgrrettoSNAPS] |  YES   | YES  | NO     | NO     |   YES    |   NO     |  YES   | YES     |

 * Many consoles/computers have the same artwork as arcade. For MAME, both arcade and consoles/computers are
   just "machines". For example, CPanel of MegaDrive is the SEGA 3 button joystick.

[Pleasuredome]: http://www.pleasuredome.org.uk/
[ProgrrettoSNAPS]: http://www.progettosnaps.net
