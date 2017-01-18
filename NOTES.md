## Boolean options ##

A machine has the boolean option or not.

 * Parent / Clone (integrated on filter menu)

 * Working / NonWorking (display tag)

 * BIOS / NoBIOS (display tag)

 * Coins / NoCoins (own menu `Machines (with coin slot)` and `Machines (no coin slot)`)

 * Mechanical / NonMechanical (own menu `Machines (mechanical)`)

 * CHD / NoCHD (own menu `Machines with CHDs`)

 * Sample / NoSamples (own menu `Machines with Samples`)

 * Devices / Nodevices (filtered out when making main database)


## Input data and directories ##

Required data files:

 * `~/DATA_DIR/MAME.xml`
 * `~/SofwareLists/hash/*.xml`
 * `~/DATA_DIR/Catver.ini`
 * `~/DATA_DIR/Catlist.ini`
 * `~/DATA_DIR/Genre.ini`

ROM directories:

 * `~/MAME/ROMs` 

 * `~/MAME/CHDs`

 * `~/MAME/SLs`

Assets directories:

 Directory       | Explanation
-----------------|---------------------------------
`~/MAME/EXTRAs/` |


## Kinds of MAME machines ##

 * Machine has ROMs and/or CHDs
 
 * Machine has Software List
 

## Launching MAME machines with media types (former MESS) ##

http://www.mess.org/mess/howto

### Known media types in MAME ###

 Name      | Short name | Machine example  |
-----------|------------|------------------|
cartridge  | cart       | 32x, sms, smspal |
cassete    | cass       |                  |
floppydisk | flop       |                  |
quickload  | quick      |                  |
snapshot   | dump       |                  |
harddisk   | hard       |                  |
cdrom      | cdrm       |                  |
printer    | prin       |                  |

Machines may have more than one media type. In this case, a number is appended at the end. For
example, a machine with 2 cartriged slots has `cartridge1` and `cartridge2`.

### Cartridges ###

Most consoles have only one cartridge slot, for example `32x`.

```
<machine name="32x" sourcefile="megadriv.cpp">
...
<device type="cartridge" tag="cartslot" mandatory="1" interface="_32x_cart">
	<instance name="cartridge" briefname="cart"/>
	<extension name="32x"/>
	<extension name="bin"/>
</device>
```

Device name and its brief version can be used at command line to launch a specific program/game.

```
mame 32x -cartridge foo1.32x
mame 32x -cart foo1.32x
```

A machine may have more than one cartridge slot, for example `abc110`.

```
<machine name="abc110" sourcefile="bbc.cpp" cloneof="bbcbp" romof="bbcbp">
...
<device type="cartridge" tag="exp_rom1" interface="bbc_cart">
    <instance name="cartridge1" briefname="cart1"/>
    <extension name="bin"/>
    <extension name="rom"/>
</device>
<device type="cartridge" tag="exp_rom2" interface="bbc_cart">
    <instance name="cartridge2" briefname="cart2"/>
    <extension name="bin"/>
    <extension name="rom"/>
</device>
...
```

Launching command example.

```
mame abc110 -cart1 foo1.bin -cart2 foo2.bin
```


## Launching Software Lists ##

http://www.mess.org/mess/howto#software_lists

http://www.mess.org/mess/swlist_format

Example of machines with SL: `32x`.

```
<machine name="32x" sourcefile="megadriv.cpp">
...
    <device type="cartridge" tag="cartslot" mandatory="1" interface="_32x_cart">
		<instance name="cartridge" briefname="cart"/>
		<extension name="32x"/>
		<extension name="bin"/>
	</device>
	<slot name="cartslot">
	</slot>
	<softwarelist name="32x" status="original" filter="NTSC-U" />
</machine>
```


## Plugin URL schema ##

       Root menu              | 1st sub          | 2nd     | 3rd    | URL                                                           |
------------------------------|------------------|---------|--------|---------------------------------------------------------------|
Machines (with coin slot)     | Parents          | Clones  |        | ?list=Machines        &parent=ROM_name                        |
Machines (no coin slot)       | Parents          | Clones  |        | ?list=NoCoin          &parent=ROM_name                        |
Machines (mechanical)         | Parents          | Clones  |        | ?list=Mechanical      &parent=ROM_name                        |
Machines (dead)               | Parents          | Clones  |        | ?list=Dead            &parent=ROM_name                        |
Machines with CHDs            | Parents          | Clones  |        | ?list=CHD             &parent=ROM_name                        |
Machines with Samples         | Parents          | Clones  |        | ?list=Samples         &parent=ROM_name                        |
Machines by Category (Catver) | Category         | Parents | Clones | ?clist=Catver         &category=Cat_name     &parent=ROM_name |
Machines by Category (Catlist)| Category         | Parents | Clones | ?clist=Catlist        &category=Cat_name     &parent=ROM_name |
Machines by Category (Genre)  | Category         | Parents | Clones | ?clist=Genre          &category=Cat_name     &parent=ROM_name |
Machines by Manufacturer      | Manufacturer     | Parents | Clones | ?clist=Manufacturer   &manufacturer=Man_name &parent=ROM_name |
Machines by Year              | Year             | Parents | Clones | ?clist=Year           &year=Year_name        &parent=ROM_name |
Machines by Driver            | Driver           | Parents | Clones | ?clist=Driver         &driver=Driver_name    &parent=ROM_name |
Machines by Control Type      | Controls         | Parents | Clones | ?clist=Controls       &control=Control_name  &parent=ROM_name |
Machines by Display Tag       | Display Tag      | Parents | Clones | ?clist=Display_Tag    &tag=Display_tag       &parent=ROM_name |
Machines by Display Type      | Display Type     | Parents | Clones | ?clist=Display_Type   &type=Display_type     &parent=ROM_name |
Machines by Display Rotation  | Display Rotation | Parents | Clones | ?clist=Display_Rotate &rotate=Display_rotate &parent=ROM_name |
Machines by Software List     | SoftList         | Parents | Clones | ?clist=BySL           &SL=SL_name            &parent=ROM_name |
Software Lists                | SoftList         | Parents | Clones | ?clist=SL             &SL=SL_name                             |
